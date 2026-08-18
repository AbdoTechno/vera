import re
from typing import Optional, Dict

def detect_target_language(req_lang: Optional[str], query: str) -> str:
    """Detects target language; defaults to English for pristine structure unless Arabic is explicitly specified."""
    if req_lang:
        cleaned = req_lang.strip().lower()
        if cleaned in ["ar", "arabic", "ar_eg", "ar_sa", "عربي", "العربية"]:
            return "ar"
        if cleaned in ["en", "english", "en_us", "en_gb"]:
            return "en"
    # Default to English
    return "en"

def is_valid_key_format(k: Optional[str]) -> bool:
    """Validates if an API key string is well-formed and not a placeholder."""
    if not k or not isinstance(k, str):
        return False
    k_clean = k.strip()
    if len(k_clean) < 15 or k_clean.lower() in ["null", "none", "undefined", "your_api_key_here", ""]:
        return False
    return True

def classify_query_intent(query: str) -> Dict[str, str]:
    """Classifies medical domain and intent from physician inquiry."""
    q_lower = query.lower()
    
    # Domain detection
    if any(term in q_lower for term in ["sma", "spinal muscular", "smn1", "smn2", "nusinersen", "spinraza", "onasemnogene", "zolgensma", "risdiplam", "evrysdi"]):
        category = "Spinal Muscular Atrophy (SMA) Guidelines"
    elif any(term in q_lower for term in ["chromosome", "chromosomal", "translocation", "inversion", "long-read", "oxford nanopore", "pacbio", "hifi", "structural variant", "sv"]):
        category = "Clinical Cytogenetics & Chromosomal Rearrangements"
    else:
        category = "General Medical & Genetic Research"

    # Intent detection
    if any(term in q_lower for term in ["dose", "dosing", "treatment", "therapy", "protocol", "علاج", "جرعة", "بدء"]):
        intent = "Treatment Protocol & Dosing Guidelines"
    elif any(term in q_lower for term in ["diagnos", "detect", "exome", "panel", "screen", "تشخيص", "فحص", "كشف"]):
        intent = "Diagnostic Methodology & Carrier Screening"
    elif any(term in q_lower for term in ["variant", "mutation", "sequencing", "جين", "طفرة", "تسلسل"]):
        intent = "Genomic Sequencing & Variant Interpretation"
    else:
        intent = "Evidence Inquiry & Synthesis"

    return {"disease_category": category, "intent": intent}
