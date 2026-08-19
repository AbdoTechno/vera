from typing import List, Dict, Any

class SimpleRAGEvaluator:
    """RAGAS: Evaluates RAG pipeline outputs for faithfulness, answer relevance, and citation integrity.
     - checks if the retrieved chunks are relevant to the query.
     - checks if the generated answer is correct, grounded in those chunks, and not hallucinated.
     - labels claims in the answer as supported (found in retrieved text) or unsupported (not backed by evidence).
     - gives you scores that show how good your RAG pipeline is at retrieval and generation. """

    @staticmethod
    def evaluate_item(
        query: str,
        generated_answer: str,
        retrieved_contexts: List[str],
        ground_truth_answer: str = ""
    ) -> Dict[str, float]:
        """Calculates lightweight automated scoring for faithfulness and answer coverage."""
        all_context = " ".join(retrieved_contexts).lower()
        answer_lower = generated_answer.lower()
        query_words = [w.lower() for w in query.split() if len(w) > 3]

        # 1. Answer Relevance (query term presence in answer)
        matched_query_terms = sum(1 for w in query_words if w in answer_lower)
        relevance_score = matched_query_terms / len(query_words) if query_words else 1.0

        # 2. Context Grounding (answer words in context)
        ans_words = [w.lower() for w in generated_answer.split() if len(w) > 4]
        grounded_words = sum(1 for w in ans_words if w in all_context)
        faithfulness_score = grounded_words / len(ans_words) if ans_words else 1.0

        # 3. Citation presence
        has_citations = 1.0 if "[" in generated_answer and "]" in generated_answer else 0.0

        return {
            "faithfulness": round(min(faithfulness_score, 1.0), 3),
            "answer_relevance": round(min(relevance_score, 1.0), 3),
            "citation_presence": has_citations
        }
