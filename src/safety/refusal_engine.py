import re
from typing import Dict, Any, Optional

class RefusalEngine:
    """Manages graceful refusal responses for out-of-scope, emergency, or unsupported queries."""

    OUT_OF_SCOPE_TOPICS = [
        r'\b(?:how to cook|recipe for|weather forecast|politics news|stock market prediction|tell me a joke)\b',
        r'\b(?:who is messi|who is ronaldo|football match result)\b',
        r'\b(?:diabetes|insulin|alzheimer|appendicitis)\b',
        r'(?:طريقة تحضير|طريقة عمل كيك|وصفة طبخ|أخبار الطقس|نتيجة مباراة|كرة قدم|نكتة|أغنية|سكر|سكري|أنسولين)'
    ]




    EMERGENCY_KEYWORDS = [
        r'\b(?:suicide|overdose|unconscious|severe bleeding|chest pain|stroke|anaphylaxis|dying|emergency)\b',
        r'(?:انتحار|جرعة زائدة|فقدان وعي|نزيف حاد|ألم شديد في الصدر|جلطة|توقف قلب|حالة طارئة|أموت)'
    ]

    DISCLAIMER_EN = (
        "--- CLINICAL SAFETY NOTICE ---\n"
        "VERA is an evidence-grounded research assistant designed for healthcare professionals. "
        "It does not provide autonomous clinical diagnoses, replace medical practitioner judgment, "
        "or handle medical emergencies."
    )

    DISCLAIMER_AR = (
        "--- تنبيه سريري وقائي ---\n"
        "منصة VERA هي مساعد أبحاث سريري مبني على الأدلة للأطباء والممارسين الصحيين. "
        "لا تقدم المنصة تشخيصات طبية مستقلة أو تغني عن الاستشارة الطبية المباشرة أو التعامل مع حالات الطوارئ."
    )

    @classmethod
    def check_pre_retrieval_refusal(cls, query: str, language: str = "en") -> Optional[Dict[str, Any]]:
        """Detects immediate out-of-scope or emergency queries before retrieval."""
        query_lower = query.lower()
        is_ar = language == "ar"

        for pattern in cls.EMERGENCY_KEYWORDS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                resp_text = (
                    "🚨 تنبيه طوارئ حرج: لا يمكن لمنصة VERA التعامل مع الحالات الطارئة أو الأزمات الحادة. "
                    "يرجى التوجه فوراً لأقرب قسم طوارئ أو الاتصال بخدمات الإسعاف الطبي العاجل."
                    if is_ar else
                    "🚨 CRITICAL SAFETY REFUSAL: VERA cannot handle acute emergencies or life-threatening crises. "
                    "Please contact emergency medical services immediately."
                )
                return {
                    "is_refusal": True,
                    "reason": "EMERGENCY_ALERT",
                    "response": resp_text,
                    "disclaimer": cls.DISCLAIMER_AR if is_ar else cls.DISCLAIMER_EN
                }

        for pattern in cls.OUT_OF_SCOPE_TOPICS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                resp_text = (
                    "⚠️ تنبيه خارج النطاق: هذا السؤال يقع خارج النطاق الطبي السريري المعتمد لمنصة VERA "
                    "(مثل إرشادات ضمور العضلات الشوكي SMA والجينات السريرية). تلتزم المنصة بدقة بالأدلة الإرشادية الطبية المعتمدة فقط."
                    if is_ar else
                    "⚠️ SCOPE REFUSAL: This inquiry is outside the approved clinical scope of VERA "
                    "(such as Spinal Muscular Atrophy and Clinical Cytogenetics / Long-Read Sequencing). "
                    "VERA operates strictly within approved peer-reviewed medical guideline boundaries."
                )
                return {
                    "is_refusal": True,
                    "reason": "OUT_OF_SCOPE_QUERY",
                    "response": resp_text,
                    "disclaimer": cls.DISCLAIMER_AR if is_ar else cls.DISCLAIMER_EN
                }

        return None

    @classmethod
    def generate_insufficient_evidence_response(cls, query: str, language: str = "en", reason: str = "") -> Dict[str, Any]:
        """Generates standard refusal when retrieval evidence fails safety confidence gates."""
        is_ar = language == "ar"
        resp_text = (
            f"⚠️ أدلة غير كافية: لا تحتوي الإرشادات السريرية المفهرسة على أدلة كافية وموثوقة للإجابة على: '{query}'.\n\n"
            f"لمنع الهلوسة الطبية وتوليد معلومات غير مؤكدة، ترفض منصة VERA تقديم إجابات غير مدعومة باستشهادات سريرية موثقة."
            if is_ar else
            f"⚠️ INSUFFICIENT EVIDENCE REFUSAL: The ingested clinical guidelines do not contain adequate or "
            f"sufficiently confident evidence to answer: '{query}'.\n\n"
            f"To prevent medical hallucination, VERA strictly refuses to generate unsupported answers."
        )
        return {
            "is_refusal": True,
            "reason": reason or "INSUFFICIENT_EVIDENCE",
            "response": resp_text,
            "disclaimer": cls.DISCLAIMER_AR if is_ar else cls.DISCLAIMER_EN
        }

