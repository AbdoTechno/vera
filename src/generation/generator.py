import os
import warnings
from typing import List, Dict, Any, Union
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from src.generation.prompt_templates import (
    CLINICAL_SYSTEM_PROMPT_EN,
    STRICT_GROUNDING_PROMPT_TEMPLATE_EN,
)
from src.generation.citation_formatter import CitationFormatter
from src.utils.logger import logger

load_dotenv()


class ClinicalGenerator:
    """Generates responses strictly grounded in retrieved medical evidence."""

    GEMINI_MODELS = [
        "models/gemini-3.1-flash-lite",
        "models/gemini-3.5-flash",
        "models/gemini-3.7-flash",
        "models/gemini-flash-latest",
    ]

    ALLOWED_ROLES = {"doctor", "general_user"}
    ALLOWED_RISK_LEVELS = {"low", "medium", "high"}

    def __init__(
        self,
        provider: str = "gemini",
        model_name: str = "models/gemini-3.1-flash-lite",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ):
        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.client = None
        self.genai_mode = None

        self._init_client()

    def _init_client(self):
        """Initialize the selected LLM provider."""
        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning(
                    "GEMINI_API_KEY not found in environment. "
                    "Generator will run in fallback mock mode."
                )
                return

            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai
                self.genai_mode = "legacy_sdk"
                logger.info(f"Initialized Gemini with model: {self.model_name}")
            except ImportError:
                logger.warning("'google-generativeai' is not installed.")

        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    logger.warning(
                        "OPENAI_API_KEY not found in environment. "
                        "Generator will run in fallback mode."
                    )
            except ImportError:
                logger.warning("'openai' package is not installed.")

    @staticmethod
    def _validate_role(user_role: str) -> str:
        """Validate and flexibly normalize the role supplied by the application."""
        if not user_role or not isinstance(user_role, str):
            return "doctor"

        role = user_role.strip().lower()
        if "user" in role or "patient" in role:
            return "general_user"
        if "doc" in role or "physician" in role or "specialist" in role or "clinical" in role:
            return "doctor"

        if role in ClinicalGenerator.ALLOWED_ROLES:
            return role

        return "doctor"

    @staticmethod
    def _validate_risk_level(risk_level: str) -> str:
        """Validate and normalize the risk classification."""
        if not risk_level or not isinstance(risk_level, str):
            return "low"

        risk = risk_level.strip().lower()
        if risk in ClinicalGenerator.ALLOWED_RISK_LEVELS:
            return risk

        return "low"

    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        user_role: str = "doctor",
        risk_level: str = "low",
        confidence: Union[float, str] = 1.0,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Generate an evidence-grounded response.

        user_role:
            doctor | general_user

        risk_level:
            low | medium | high

        confidence:
            Retrieval confidence calculated by the retrieval layer (0.0 to 1.0).
        """
        # ---------------------------------------------------------
        # Validate application-provided variables
        # ---------------------------------------------------------
        user_role = self._validate_role(user_role)
        risk_level = self._validate_risk_level(risk_level)

        if isinstance(confidence, str):
            confidence_clean = confidence.replace("%", "").strip()
            try:
                conf_float = float(confidence_clean)
                confidence_num = conf_float / 100.0 if conf_float > 1.0 else conf_float
            except ValueError:
                confidence_num = 1.0
        else:
            try:
                confidence_num = float(confidence)
            except (TypeError, ValueError):
                confidence_num = 1.0

        confidence_val = max(0.0, min(1.0, confidence_num))

        # ---------------------------------------------------------
        # No evidence retrieved
        # ---------------------------------------------------------
        if not retrieved_chunks:
            if user_role == "general_user":
                answer = (
                    "INSUFFICIENT EVIDENCE: No relevant medical evidence "
                    "was retrieved for this question. Please consult a "
                    "qualified healthcare professional."
                )
            else:
                answer = (
                    "INSUFFICIENT EVIDENCE: No relevant clinical guideline "
                    "evidence was retrieved for this query."
                )

            return {
                "answer": answer,
                "citations": [],
                "retrieved_chunks": [],
                "retrieved_chunks_count": 0,
                "user_role": user_role,
                "risk_level": risk_level,
                "confidence": confidence_val,
                "is_refusal": True,
            }

        # ---------------------------------------------------------
        # High-risk general-user request
        # ---------------------------------------------------------
        if user_role == "general_user" and risk_level == "high":
            answer = self._high_risk_general_user_response(language=language)
            return {
                "answer": answer,
                "citations": [],
                "retrieved_chunks": retrieved_chunks,
                "retrieved_chunks_count": len(retrieved_chunks),
                "user_role": user_role,
                "risk_level": risk_level,
                "confidence": confidence_val,
                "is_refusal": True,
            }

        # ---------------------------------------------------------
        # Build retrieved context & user prompt
        # ---------------------------------------------------------
        context_block = CitationFormatter.format_context_block(retrieved_chunks)

        user_prompt = STRICT_GROUNDING_PROMPT_TEMPLATE_EN.format(
            user_role=user_role,
            risk_level=risk_level,
            confidence=f"{confidence_val:.2f}",
            retrieved_context=context_block,
            query=query,
        )

        response_text = ""

        # ---------------------------------------------------------
        # Gemini Provider
        # ---------------------------------------------------------
        if self.provider == "gemini" and self.client:
            full_prompt = f"{CLINICAL_SYSTEM_PROMPT_EN}\n\n{user_prompt}"
            candidate_models = [self.model_name] + [
                m for m in self.GEMINI_MODELS if m != self.model_name
            ]

            for model_name in candidate_models:
                try:
                    model = self.client.GenerativeModel(
                        model_name=model_name,
                        generation_config={
                            "temperature": self.temperature,
                            "max_output_tokens": self.max_tokens,
                        },
                    )
                    response = model.generate_content(full_prompt)
                    if response and response.text:
                        response_text = response.text
                        break
                except Exception as e:
                    logger.warning(f"Gemini model '{model_name}' failed: {e}")
                    error = str(e).lower()
                    if any(key in error for key in ("api_key_invalid", "api key not valid", "permission_denied", "invalid api key")):
                        raise ValueError(f"Invalid or expired Gemini API key: {e}")

            if not response_text:
                response_text = self._mock_fallback_synthesis(
                    query=query,
                    retrieved_chunks=retrieved_chunks,
                    user_role=user_role,
                    risk_level=risk_level,
                    confidence=confidence_val,
                    language=language,
                )

        # ---------------------------------------------------------
        # OpenAI Provider
        # ---------------------------------------------------------
        elif self.provider == "openai" and self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": CLINICAL_SYSTEM_PROMPT_EN},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                response_text = response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI generation error: {e}")
                response_text = self._mock_fallback_synthesis(
                    query=query,
                    retrieved_chunks=retrieved_chunks,
                    user_role=user_role,
                    risk_level=risk_level,
                    confidence=confidence_val,
                    language=language,
                )

        # ---------------------------------------------------------
        # Fallback Mock Mode
        # ---------------------------------------------------------
        else:
            response_text = self._mock_fallback_synthesis(
                query=query,
                retrieved_chunks=retrieved_chunks,
                user_role=user_role,
                risk_level=risk_level,
                confidence=confidence_val,
                language=language,
            )

        # ---------------------------------------------------------
        # Citation Extraction & Refusal Detection
        # ---------------------------------------------------------
        citations = CitationFormatter.extract_citations(response_text)

        refusal_markers = (
            "INSUFFICIENT EVIDENCE",
            "insufficient evidence",
            "غير كافية",
            "لا توجد أدلة كافية",
            "does not contain",
            "لا تحتوي الأدلة"
        )
        is_refusal = any(marker in response_text for marker in refusal_markers)

        return {
            "answer": response_text,
            "citations": citations,
            "retrieved_chunks": retrieved_chunks,
            "retrieved_chunks_count": len(retrieved_chunks),
            "user_role": user_role,
            "risk_level": risk_level,
            "confidence": confidence_val,
            "is_refusal": is_refusal,
        }

    @staticmethod
    def _high_risk_general_user_response(language: str = "en") -> str:
        """Safe deterministic response for high-risk general users."""
        if language.lower().startswith("ar"):
            return (
                "لا أستطيع تقديم تعليمات علاجية مباشرة لهذه الحالة لأنها تتطلب "
                "تقييماً سريرياً متخصصاً. يرجى استشارة الطبيب المختص أو زيارة أقرب مركز رعاية صحية."
            )
        return (
            "I cannot provide clinical management instructions for this high-risk query. "
            "Please consult a qualified medical professional for diagnosis and personalized care."
        )

    def _mock_fallback_synthesis(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        user_role: str,
        risk_level: str,
        confidence: float,
        language: str = "en",
    ) -> str:
        """Deterministic evidence synthesis fallback when LLM API is unavailable."""
        if user_role == "general_user" and risk_level == "high":
            return self._high_risk_general_user_response(language)

        top_chunk = retrieved_chunks[0]
        metadata = top_chunk.get("metadata", {})
        document = metadata.get("doc_name", metadata.get("source", "Clinical Guideline"))
        section = metadata.get("section", "General Overview")
        page = metadata.get("page_number", metadata.get("page", 1))

        content = top_chunk.get("content", "")
        preview = content[:280]
        citation = f"[{document} | {section} | Page {page}]"

        if language.lower().startswith("ar"):
            return (
                f"### Summary\n"
                f"بناءً على الإرشادات السريرية المسترجعة: {preview}...\n\n"
                f"### Key Clinical Recommendations\n"
                f"- {preview}... {citation}"
            )

        return (
            f"### Summary\n"
            f"Based on the retrieved clinical evidence: {preview}...\n\n"
            f"### Key Clinical Recommendations\n"
            f"- {preview}... {citation}"
        )
