import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import pypdf
from pydantic import BaseModel, Field

from src.utils.logger import logger

class DocumentValidation(BaseModel):
    is_medical: bool = Field(description="Whether the document is genuinely medical.")
    is_clinical: bool = Field(description="Whether the document contains clinically relevant medical information.")
    scope_match: bool = Field(description="Whether the document falls within supported VERA clinical domains.")
    domain: str = Field(description="Identified primary medical domain.")
    subdomain: str = Field(description="Specific medical subdomain.")
    document_type: str = Field(description="Document type e.g., Clinical Guideline, Research Paper, Protocol.")
    has_clinical_recommendations: bool = Field(description="Whether it contains actionable clinical recommendations.")
    evidence_quality: float = Field(ge=0.0, le=1.0, description="Estimated usefulness from 0 to 1.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in validation decision from 0 to 1.")
    decision: str = Field(description="Final decision: PASS, REVIEW, or REJECT.")
    reason: str = Field(description="Clinical rationale for the decision.")
    warnings: List[str] = Field(default_factory=list, description="Potential issues or limitations.")

VERA_SUPPORTED_SCOPE = """
VERA Supported Clinical Domains:
1. Spinal Muscular Atrophy (SMA): Diagnosis, SMN1/SMN2 genetics, treatment protocols (Nusinersen, Zolgensma, Risdiplam), clinical trials.
2. Clinical Cytogenetics & Genomics: Chromosomal rearrangements, structural variants, long-read sequencing, karyotyping, genetic disorders.
3. General Clinical Practice: Evidence-based clinical guidelines, therapeutic recommendations, dosing protocols, pediatric neurology, cardiology, oncology.

Rejected Documents (OUT OF SCOPE):
- Non-medical documents (CVs, financial invoices, general science, non-clinical papers).
- Speculative blogs, patient self-diagnosis posts, unverified marketing brochures.
"""

def extract_smart_document_profile(pdf_path: str) -> Dict[str, Any]:
    """Smartly extracts title, abstract, key clinical excerpts, and conclusion within ~1500 tokens."""
    filename = Path(pdf_path).name
    pages = []
    
    try:
        reader = pypdf.PdfReader(pdf_path)
        for idx, page in enumerate(reader.pages, start=1):
            txt = page.extract_text() or ""
            pages.append({"page": idx, "text": " ".join(txt.split())})
    except Exception as e:
        logger.warning(f"Failed to parse PDF pages from '{filename}': {e}")
        return {
            "filename": filename,
            "total_pages": 0,
            "total_characters": 0,
            "profile_text": f"FILE NAME: {filename}\nCORRUPT_OR_UNREADABLE_PDF: True\nERROR: {str(e)}",
            "is_corrupt": True
        }
        
    total_pages = len(pages)
    total_chars = sum(len(p["text"]) for p in pages)
    
    parts = [
        f"FILE NAME: {filename}",
        f"TOTAL PAGES: {total_pages}",
        f"TOTAL CHARACTERS: {total_chars}",
        "",
        "SMART DOCUMENT PROFILE & EXCERPTS:",
        "=" * 60
    ]
    
    # 1. Page 1: Title & Abstract
    p1 = pages[0]["text"] if pages else ""
    parts.append(f"\n--- [PAGE 1: TITLE & ABSTRACT] ---\n{p1[:1800]}")

    
    # 2. Scan for key clinical anchors
    CLINICAL_KEYWORDS = [
        "recommendation", "guideline", "treatment", "dosing", "protocol",
        "diagnosis", "inclusion criteria", "monitoring", "sequencing", "conclusion"
    ]
    found = []
    for p in pages[1:-1]:
        t_low = p["text"].lower()
        for kw in CLINICAL_KEYWORDS:
            if kw in t_low:
                idx = t_low.find(kw)
                start = max(0, idx - 80)
                end = min(len(p["text"]), idx + 350)
                snippet = p["text"][start:end].strip()
                found.append(f"• [Page {p['page']} | Section: '{kw}']: \"...{snippet}...\"")
                if len(found) >= 3:
                    break
        if len(found) >= 3:
            break
            
    if found:
        parts.append("\n--- [KEY CLINICAL EXCERPTS] ---")
        parts.extend(found)
        
    # 3. Last page conclusion
    if total_pages > 2:
        last = pages[-1]["text"]
        parts.append(f"\n--- [PAGE {total_pages}: CONCLUSION / SUMMARY] ---\n{last[:800]}")
        
    return {
        "filename": filename,
        "total_pages": total_pages,
        "total_characters": total_chars,
        "profile_text": "\n".join(parts)
    }

def validate_medical_document(pdf_path: str, gemini_api_key: Optional[str] = None) -> DocumentValidation:
    """Validates an uploaded PDF against VERA medical relevance and clinical scope using Gemini LLM or heuristics."""
    profile_data = extract_smart_document_profile(pdf_path)
    
    if profile_data.get("is_corrupt") or profile_data.get("total_pages", 0) == 0:
        return DocumentValidation(
            is_medical=False,
            is_clinical=False,
            scope_match=False,
            domain="Invalid / Corrupted File",
            subdomain="None",
            document_type="Unreadable PDF",
            has_clinical_recommendations=False,
            evidence_quality=0.0,
            confidence=1.0,
            decision="REJECT",
            reason="Uploaded file is unreadable, empty, or corrupted.",
            warnings=["File contains invalid PDF binary structure"]
        )
        
    profile_text = profile_data["profile_text"]
    api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "").strip()

    
    if api_key and len(api_key) >= 15:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("models/gemini-3.1-flash-lite")
            
            prompt = f"""You are VERA's Senior Clinical Document Gatekeeper.
Validate whether this document is medically relevant and suitable for inclusion in the VERA evidence-grounded RAG knowledge base.

{VERA_SUPPORTED_SCOPE}

DOCUMENT PROFILE:
{profile_text}

Respond in STRICT JSON format matching these exact fields:
{{
  "is_medical": true/false,
  "is_clinical": true/false,
  "scope_match": true/false,
  "domain": "primary medical domain",
  "subdomain": "specific subdomain",
  "document_type": "Clinical Guideline / Research Paper / Non-Medical / etc",
  "has_clinical_recommendations": true/false,
  "evidence_quality": 0.0 to 1.0,
  "confidence": 0.0 to 1.0,
  "decision": "PASS" or "REVIEW" or "REJECT",
  "reason": "Clear explanation for decision",
  "warnings": ["warning 1 if any"]
}}
"""
            resp = model.generate_content(prompt)
            raw_text = resp.text.strip()
            
            # Extract JSON block
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                validation = DocumentValidation(**parsed)
                logger.info(f"AI Document Validation Result: {validation.decision} (Domain: {validation.domain})")
                return validation
        except Exception as e:
            logger.warning(f"LLM Document Validation error: {e}. Using deterministic safety heuristic.")
            
    # Deterministic Fallback Heuristic
    profile_lower = profile_text.lower()
    medical_terms = ["clinical", "treatment", "patient", "disease", "sma", "smn1", "smn2", "chromosome", "therapy", "diagnosis", "dosage", "protocol"]
    matches = sum(1 for term in medical_terms if term in profile_lower)
    
    if matches >= 3:
        return DocumentValidation(
            is_medical=True,
            is_clinical=True,
            scope_match=True,
            domain="Clinical Medical Guidelines",
            subdomain="General Clinical / Genetic Medicine",
            document_type="Clinical Guideline / Medical Publication",
            has_clinical_recommendations=True,
            evidence_quality=0.85,
            confidence=0.90,
            decision="PASS",
            reason="Document contains established medical terminology and clinical guidance.",
            warnings=[]
        )
    else:
        return DocumentValidation(
            is_medical=False,
            is_clinical=False,
            scope_match=False,
            domain="Unknown / Non-Medical",
            subdomain="General",
            document_type="Unverified Document",
            has_clinical_recommendations=False,
            evidence_quality=0.10,
            confidence=0.95,
            decision="REJECT",
            reason="Document does not contain sufficient clinical evidence or medical terminology.",
            warnings=["Lacks peer-reviewed clinical structure"]
        )
