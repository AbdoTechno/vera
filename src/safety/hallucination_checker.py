import re
from typing import List, Dict, Any, Tuple
from src.generation.citation_formatter import CitationFormatter
from src.utils.logger import logger

class HallucinationChecker:
    """Verifies that generated claims are fully substantiated by the retrieved evidence context."""

    def __init__(self, strictness_threshold: float = 0.75):
        self.strictness_threshold = strictness_threshold

    def verify_faithfulness(self, generated_text: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Performs lexical and citation grounding checks on the generated text."""
        if not retrieved_chunks:
            return {
                "is_faithful": False,
                "faithfulness_score": 0.0,
                "unsupported_claims": ["No retrieved context provided."]
            }

        # Combine all retrieved context text
        full_context = " ".join([ch.get("content", "").lower() for ch in retrieved_chunks])
        
        # 1. Validate Citations
        citations_valid, citation_score = CitationFormatter.validate_citations_against_context(
            generated_text, retrieved_chunks
        )

        # 2. Extract key factual sentences from answer
        sentences = [s.strip() for s in re.split(r'[.!?\n]', generated_text) if len(s.strip()) > 25]
        
        unsupported = []
        supported_count = 0

        for sent in sentences:
            # Skip structural headers
            if any(sent.startswith(h) for h in ["###", "**Clinical", "**Supporting", "**Source", "---"]):
                continue

            # Extract words (excluding stop words)
            words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', sent)]
            if not words:
                continue

            # Check overlap percentage with context
            matched_words = [w for w in words if w in full_context]
            overlap_ratio = len(matched_words) / len(words)

            if overlap_ratio >= 0.50:
                supported_count += 1
            else:
                unsupported.append(sent)

        total_tested = supported_count + len(unsupported)
        faithfulness_score = supported_count / total_tested if total_tested > 0 else 1.0

        is_faithful = faithfulness_score >= self.strictness_threshold and (citations_valid or len(CitationFormatter.extract_citations(generated_text)) == 0)

        logger.info(f"Hallucination check: Faithfulness Score = {faithfulness_score:.2f} (Passed: {is_faithful})")
        return {
            "is_faithful": is_faithful,
            "faithfulness_score": round(faithfulness_score, 3),
            "citation_score": citation_score,
            "unsupported_claims": unsupported
        }
