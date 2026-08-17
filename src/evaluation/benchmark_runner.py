from typing import List, Dict, Any, Set
from pathlib import Path
from src.utils.helpers import load_json, save_json
from src.utils.logger import logger
from src.evaluation.retrieval_metrics import calculate_precision_at_k, calculate_recall_at_k, calculate_mrr
from src.evaluation.ragas_evaluator import SimpleRAGEvaluator

class BenchmarkRunner:
    """Runs automated end-to-end evaluation across standard benchmark test cases."""

    def __init__(self, retrieval_engine, generator, safety_gate):
        self.retrieval_engine = retrieval_engine
        self.generator = generator
        self.safety_gate = safety_gate

    @staticmethod
    def _is_match(retrieved_meta: Dict[str, Any], gold_targets: Set[str]) -> bool:
        """Flexible matching across doc_id, doc_name, or filename."""
        doc_id = str(retrieved_meta.get("doc_id", "")).lower()
        doc_name = str(retrieved_meta.get("doc_name", "")).lower()
        
        for target in gold_targets:
            t = target.lower()
            if t in doc_id or doc_id in t or t in doc_name or doc_name in t:
                return True
        return False

    def run_benchmark(self, dataset_path: str, top_k: int = 4) -> Dict[str, Any]:
        """Executes full benchmark evaluation against test queries."""
        items = load_json(dataset_path)
        logger.info(f"Running benchmark on {len(items)} test queries...")

        results = []
        precision_scores = []
        faithfulness_scores = []
        relevance_scores = []

        for idx, item in enumerate(items):
            query = item["query"]
            # Target doc identifiers (doc_ids + gold_citations)
            gold_targets = set(item.get("relevant_doc_ids", []) + item.get("gold_citations", []))
            
            # 1. Retrieval
            retrieved = self.retrieval_engine.retrieve(query, top_k=top_k)
            
            # Match retrieved chunks against gold references
            relevant_count = sum(1 for ch in retrieved[:top_k] if self._is_match(ch.get("metadata", {}), gold_targets))
            p_at_k = round(relevant_count / len(retrieved[:top_k]), 4) if retrieved else 0.0
            precision_scores.append(p_at_k)

            # 2. Safety Gate
            gate_result = self.safety_gate.evaluate(retrieved)

            # 3. Generation
            if gate_result["passed"]:
                gen_res = self.generator.generate_response(query, retrieved)
                answer = gen_res["answer"]
            else:
                answer = "INSUFFICIENT EVIDENCE: Gating refusal."

            # 4. Evaluation scoring
            contexts = [c["content"] for c in retrieved]
            eval_score = SimpleRAGEvaluator.evaluate_item(query, answer, contexts)
            
            faithfulness_scores.append(eval_score["faithfulness"])
            relevance_scores.append(eval_score["answer_relevance"])

            results.append({
                "test_id": item.get("id", idx + 1),
                "query": query,
                "precision_at_k": p_at_k,
                "safety_passed": gate_result["passed"],
                "answer": answer,
                "scores": eval_score
            })

        avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0
        avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

        summary = {
            "total_queries": len(items),
            "average_precision_at_k": round(avg_precision, 4),
            "average_faithfulness": round(avg_faithfulness, 4),
            "average_relevance": round(avg_relevance, 4),
            "results": results
        }

        logger.success(f"Benchmark finished! Avg Precision@{top_k}: {avg_precision * 100:.1f}%, Avg Faithfulness: {avg_faithfulness * 100:.1f}%")
        return summary
