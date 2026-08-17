from typing import List, Dict, Any
from src.utils.logger import logger

class ConfidenceGate:
    """Evaluates retrieval confidence before passing context to generation."""

    def __init__(self, min_confidence: float = 0.62, min_chunks: int = 1):
        self.min_confidence = min_confidence
        self.min_chunks = min_chunks

    def evaluate(self, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Checks if retrieval quality meets the threshold for safe clinical generation."""
        if not retrieved_chunks or len(retrieved_chunks) < self.min_chunks:
            return {
                "passed": False,
                "reason": "NO_EVIDENCE_FOUND",
                "max_score": 0.0,
                "message": "Retrieval returned 0 relevant guideline passages."
            }

        scores = [ch.get("similarity_score", 0.0) for ch in retrieved_chunks]
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        if max_score < self.min_confidence:
            logger.warning(f"Confidence Gate FAILED: max similarity {max_score:.4f} < {self.min_confidence}")
            return {
                "passed": False,
                "reason": "LOW_CONFIDENCE_RETRIEVAL",
                "max_score": max_score,
                "avg_score": avg_score,
                "message": f"Best matching evidence similarity ({max_score:.3f}) is below safety threshold ({self.min_confidence})."
            }

        logger.info(f"Confidence Gate PASSED: max similarity {max_score:.4f} >= {self.min_confidence}")
        return {
            "passed": True,
            "reason": "CONFIDENCE_SUFFICIENT",
            "max_score": max_score,
            "avg_score": avg_score,
            "message": "Evidence confidence is sufficient for generation."
        }
