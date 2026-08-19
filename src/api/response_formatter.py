import re
from typing import List
from src.api.schemas import ClinicalResponse, SourceFound, CitationItem

def format_clinical_response(
    raw_answer: str,
    sources: List[SourceFound],
    language: str,
    confidence_val: float = 0.85,
    user_role: str = "doctor"
) -> ClinicalResponse:
    """Formats generated medical text into clean bullet recommendations and structured citations."""
    cleaned_text = raw_answer.strip()
    lines = [l.strip() for l in cleaned_text.split("\n") if l.strip()]

    summary = ""
    recs: List[str] = []

    for line in lines:
        # Skip reasoning markers or header titles
        if any(line.lower().startswith(p) for p in ["wait,", "let's", "thinking", "here is", "sure,", "source citations", "###", "---"]):
            continue
        
        clean = re.sub(r'^(?:#+|\*\*|###)\s*(?:Executive\s+)?(?:Clinical\s+)?(?:Summary|Recommendations?|Direct Answer)[:\*#]*\s*', '', line, flags=re.IGNORECASE).strip()
        clean = clean.lstrip("-*•0123456789. ").strip()
        clean = clean.replace("**:", ":").replace("**", "").strip()
        
        if len(clean) < 20:
            continue

        # Identify summary vs recommendation bullets
        if not summary and not line.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.")) and len(clean) > 40:
            summary = clean
        else:
            recs.append(clean)

    if not summary and recs:
        summary = recs.pop(0)

    if not summary:
        if user_role == "general_user":
            summary = "Clinical guidelines provide important health information regarding this inquiry. Always discuss these findings with a licensed healthcare provider."
        else:
            summary = "Approved clinical guidelines outline evidence-based recommendations for this inquiry."

    if not recs:
        sentences = [s.strip() for s in re.split(r'(?<=\.)\s+', summary) if len(s.strip()) > 30]
        if len(sentences) > 1:
            recs = sentences[1:]
            summary = sentences[0]
        else:
            if user_role == "general_user":
                recs = [summary, "Consult a licensed physician or specialist for personalized clinical evaluation and therapeutic guidance."]
            else:
                recs = [summary, "Consult the attached peer-reviewed literature for comprehensive protocol specifics."]

    # Citations
    citations: List[CitationItem] = []
    for idx, s in enumerate(sources[:4], 1):
        citations.append(CitationItem(
            citation_id=idx,
            source=s.doc_title,
            page=s.page_number,
            section=s.section,
            doclink=s.doclink
        ))

    is_ar = language.lower().startswith("ar")
    if user_role == "general_user":
        disclaimer = (
            "تنبيه طبي: هذه المعلومات مستخرجة من إرشادات طبية للتثقيف الصحي فقط ولا تغني عن استشارة الطبيب المختص لتشخيص حالتك وعلاجها."
            if is_ar else
            "Medical Notice: This evidence-based synthesis is for educational purposes only. Always consult a qualified medical professional for diagnosis and personalized treatment."
        )
    else:
        disclaimer = (
            "تنويه سريري: VERA هو مساعد بحثي مبني على الأدلة ولا يغني عن التقييم السريري المستقل للطبيب المعالج."
            if is_ar else
            "VERA is an evidence-grounded research assistant and does not replace autonomous clinical diagnosis or medical practitioner judgment."
        )

    conf_pct = f"{int(confidence_val * 100)}%" if confidence_val <= 1.0 else f"{int(confidence_val)}%"

    return ClinicalResponse(
        summary=summary,
        detailed_recommendations=recs[:5],
        citations=citations,
        medical_disclaimer=disclaimer,
        confidence_score=confidence_val,
        confidence_percentage=conf_pct
    )

