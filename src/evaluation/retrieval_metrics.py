from typing import List, Set, Any, Dict

def calculate_precision_at_k(retrieved_doc_ids: List[str], ground_truth_doc_ids: Set[str], k: int) -> float:
    """Calculates Precision@K for retrieved document IDs."""
    if k <= 0 or not retrieved_doc_ids:
        return 0.0
    top_k = retrieved_doc_ids[:k]
    relevant_retrieved = sum(1 for doc_id in top_k if doc_id in ground_truth_doc_ids)
    return round(relevant_retrieved / len(top_k), 4)

def calculate_recall_at_k(retrieved_doc_ids: List[str], ground_truth_doc_ids: Set[str], k: int) -> float:
    """Calculates Recall@K for retrieved document IDs."""
    if not ground_truth_doc_ids:
        return 1.0
    top_k = retrieved_doc_ids[:k]
    relevant_retrieved = sum(1 for doc_id in top_k if doc_id in ground_truth_doc_ids)
    return round(relevant_retrieved / len(ground_truth_doc_ids), 4)

def calculate_mrr(retrieved_doc_ids: List[str], ground_truth_doc_ids: Set[str]) -> float:
    """Calculates Mean Reciprocal Rank (MRR)."""
    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in ground_truth_doc_ids:
            return round(1.0 / rank, 4)
    return 0.0
