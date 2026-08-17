import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from src.generation.prompt_templates import (
    CLINICAL_SYSTEM_PROMPT_EN, STRICT_GROUNDING_PROMPT_TEMPLATE_EN
)
from src.generation.citation_formatter import CitationFormatter
from src.utils.logger import logger

load_dotenv()


class ClinicalGenerator:
    """Orchestrates LLM synthesis grounded strictly in retrieved medical evidence."""

    # Priority model list for Gemini (optimized for ultra-fast latency and quota)
    GEMINI_MODELS = [
        "models/gemini-3.1-flash-lite",
        "models/gemini-3.5-flash",
        "models/gemini-3.7-flash",
        "models/gemini-flash-latest"
    ]

    def __init__(
        self,
        provider: str = "gemini",
        model_name: str = "models/gemini-3.1-flash-lite",
        temperature: float = 0.0,
        max_tokens: int = 1024
    ):
        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        self.genai_mode = None
        self._init_client()

    def _init_client(self):
        """Initializes API client based on provider."""
        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in environment. Generator will run in fallback mock mode.")
                return

            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=api_key)
                self.client = genai_legacy
                self.genai_mode = "legacy_sdk"
                logger.info(f"Initialized Google Gemini with model: {self.model_name}")
            except ImportError:
                logger.warning("'google-generativeai' not installed.")

        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    logger.warning("OPENAI_API_KEY not found in environment.")
            except ImportError:
                logger.warning("openai package not installed.")

    def generate_response(self, query: str, retrieved_chunks: List[Dict[str, Any]], language: str = "en") -> Dict[str, Any]:
        """Generates evidence-grounded response with transparent citations and requested language."""
        if not retrieved_chunks:
            return {
                "answer": "INSUFFICIENT EVIDENCE: No relevant medical guideline documents were retrieved for this clinical query.",
                "citations": [],
                "retrieved_chunks_count": 0,
                "is_refusal": True
            }

        context_block = CitationFormatter.format_context_block(retrieved_chunks)
        sys_prompt = CLINICAL_SYSTEM_PROMPT_EN
        user_prompt = STRICT_GROUNDING_PROMPT_TEMPLATE_EN.format(retrieved_context=context_block, query=query)

        response_text = ""



        # Call Gemini API
        if self.provider == "gemini" and self.client:
            full_prompt = f"{sys_prompt}\n\n{user_prompt}"
            generated_success = False

            # Try candidate models
            candidate_models = [self.model_name] + [m for m in self.GEMINI_MODELS if m != self.model_name]
            
            for mod in candidate_models:
                try:
                    m = self.client.GenerativeModel(
                        model_name=mod,
                        generation_config={"temperature": self.temperature, "max_output_tokens": self.max_tokens}
                    )
                    resp = m.generate_content(full_prompt)
                    if resp and resp.text:
                        response_text = resp.text
                        generated_success = True
                        break
                except Exception as e:
                    logger.warning(f"Attempt with Gemini model '{mod}' failed: {e}")
                    if any(k in str(e).lower() for k in ["api_key_invalid", "api key not valid", "permission_denied", "invalid api key"]):
                        raise ValueError(f"Invalid or expired Gemini API Key: {e}")
                    continue

            if not generated_success:
                raise RuntimeError("Failed to generate clinical response with Gemini. Please verify your API key and quotas.")

        # Call OpenAI API
        elif self.provider == "openai" and self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                response_text = response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI Generation Error: {e}")
                response_text = self._mock_fallback_synthesis(query, retrieved_chunks, language=language)

        else:
            response_text = self._mock_fallback_synthesis(query, retrieved_chunks, language=language)

        citations = CitationFormatter.extract_citations(response_text)
        is_refusal = "INSUFFICIENT EVIDENCE" in response_text or "غير كافية" in response_text

        return {
            "answer": response_text,
            "citations": citations,
            "retrieved_chunks": retrieved_chunks,
            "is_refusal": is_refusal
        }

    def _mock_fallback_synthesis(self, query: str, retrieved_chunks: List[Dict[str, Any]], language: str = "ar") -> str:
        """Deterministic offline synthesizer used when API keys are not provided."""
        top_chunk = retrieved_chunks[0]
        meta = top_chunk.get("metadata", {})
        doc = meta.get("doc_name", "Clinical Guideline")
        sec = meta.get("section", "Section")
        page = meta.get("page_number", "1")
        content_preview = top_chunk.get("content", "")[:280]

        if language == "ar":
            return (
                f"### ملخص التوصية السريرية:\n"
                f"بناءً على الأدلة الإكلينيكية المسترجعة للاستفسار '{query}'، تشير الإرشادات المعتمدة إلى: {content_preview}... "
                f"[{doc} | Page: {page}]\n\n"
                f"### التوصيات الإكلينيكية:\n"
                f"- \"{content_preview}...\" [{doc} | Page: {page}]\n\n"
                f"### المراجع المعتمدة:\n"
                f"- **المستند**: {doc}\n"
                f"- **القسم**: {sec}\n"
                f"- **رقم الصفحة**: {page}\n"
            )

        return (
            f"### Clinical Recommendation / Direct Answer:\n"
            f"Based on the retrieved clinical evidence for query '{query}', recommendations indicate: {content_preview}... "
            f"[{doc} | Section: {sec} | Page: {page}]\n\n"
            f"### Supporting Evidence & Excerpts:\n"
            f"- \"{content_preview}...\" [{doc} | Section: {sec} | Page: {page}]\n\n"
            f"### Source Citations:\n"
            f"- **Document**: {doc}\n"
            f"- **Section**: {sec}\n"
            f"- **Page**: {page}\n"
        )

