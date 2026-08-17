import re
from typing import Dict, Any, Optional

class RefusalEngine:
    """Manages graceful refusal responses for out-of-scope, emergency, or unsupported queries."""

    OUT_OF_SCOPE_TOPICS = [
        r'\b(?:covid|diabetes|alzheimer|cancer|hypertension|cardiac arrest|appendicitis)\b',
        r'\b(?:how to cook|weather|politics|sports|stock market)\b'
    ]

    EMERGENCY_KEYWORDS = [
        r'\b(?:suicide|overdose|unconscious|severe bleeding|chest pain|stroke|anaphylaxis)\b'
    ]

    DISCLAIMER = (
        "--- CLINICAL SAFETY NOTICE ---\n"
        "VERA is an evidence-grounded research assistant designed for healthcare professionals. "
        "It does not provide autonomous clinical diagnoses, replace medical practitioner judgment, "
        "or handle medical emergencies."
    )

    @classmethod
    def check_pre_retrieval_refusal(cls, query: str) -> Optional[Dict[str, Any]]:
        """Detects immediate out-of-scope or emergency queries before retrieval."""
        query_lower = query.lower()

        for pattern in cls.EMERGENCY_KEYWORDS:
            if re.search(pattern, query_lower):
                return {
                    "is_refusal": True,
                    "reason": "EMERGENCY_ALERT",
                    "response": (
                        "🚨 CRITICAL SAFETY REFUSAL: This system cannot handle emergency or acute crisis queries. "
                        "Please contact emergency medical services immediately."
                    ),
                    "disclaimer": cls.DISCLAIMER
                }

        for pattern in cls.OUT_OF_SCOPE_TOPICS:
            if re.search(pattern, query_lower):
                return {
                    "is_refusal": True,
                    "reason": "OUT_OF_SCOPE_QUERY",
                    "response": (
                        "⚠️ SCOPE REFUSAL: This question is outside the approved clinical scope of the ingested "
                        "guidelines (Spinal Muscular Atrophy and Clinical Cytogenetics / Long-Read Sequencing). "
                        "VERA operates strictly within approved guideline boundaries."
                    ),
                    "disclaimer": cls.DISCLAIMER
                }

        return None

    @classmethod
    def generate_insufficient_evidence_response(cls, query: str, reason: str = "") -> Dict[str, Any]:
        """Generates standard refusal when retrieval evidence fails safety confidence gates."""
        return {
            "is_refusal": True,
            "reason": reason or "INSUFFICIENT_EVIDENCE",
            "response": (
                f"⚠️ INSUFFICIENT EVIDENCE REFUSAL: The ingested clinical guidelines do not contain adequate or "
                f"sufficiently confident evidence to answer your query: '{query}'.\n\n"
                f"To prevent medical hallucination, VERA strictly refuses to generate unsupported answers."
            ),
            "disclaimer": cls.DISCLAIMER
        }
