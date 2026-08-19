import re
from typing import List, Dict, Any, Tuple

class CitationFormatter:
    """Validates, parses, and standardizes citations in generated clinical responses."""

    CITATION_REGEX = r'\[([^\|\]]+)\s*\|\s*(?:Section:?\s*)?([^\|\]]+)\s*\|\s*(?:Page:?\s*)?([^\]\|]+)(?:\s*\|\s*([^\]]+))?\]'

    @classmethod
    def format_context_block(cls, chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks into a standardized evidence block for the LLM prompt."""
        formatted_blocks = []
        for idx, ch in enumerate(chunks):
            meta = ch.get("metadata", {}) if isinstance(ch, dict) else {}
            doc_name = meta.get("doc_name") or ch.get("doc_name", "Unknown Document")
            section = meta.get("section") or ch.get("section", "General Section")
            page_num = meta.get("page_number") or ch.get("page_number", "N/A")
            chunk_id = meta.get("chunk_id") or ch.get("chunk_id", f"chk_{idx+1}")
            score = ch.get("similarity_score", 0.0) if isinstance(ch, dict) else 0.0
            content = ch.get("content", "").strip() if isinstance(ch, dict) else str(ch)

            block = (
                f"--- EVIDENCE CHUNK #{idx+1} ---\n"
                f"Document: {doc_name}\n"
                f"Section: {section}\n"
                f"Page: {page_num}\n"
                f"Chunk ID: {chunk_id}\n"
                f"Retrieval Score: {score}\n"
                f"Content:\n{content}\n"
            )
            formatted_blocks.append(block)

        return "\n".join(formatted_blocks)

    @classmethod
    def extract_citations(cls, text: str) -> List[Dict[str, str]]:
        """Extracts structured citations from response text."""
        matches = re.findall(cls.CITATION_REGEX, text)
        citations = []
        for m in matches:
            citations.append({
                "doc_name": m[0].strip(),
                "section": m[1].strip(),
                "page": m[2].strip()
            })
        return citations

    @classmethod
    def validate_citations_against_context(cls, text: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[bool, float]:
        """Checks whether cited documents and pages actually exist in the retrieved chunks context."""
        extracted = cls.extract_citations(text)
        if not extracted:
            return False, 0.0

        valid_citations = 0
        valid_sources = set()
        for ch in retrieved_chunks:
            meta = ch.get("metadata", {}) if isinstance(ch, dict) else {}
            d_name = (meta.get("doc_name") or ch.get("doc_name", "")).lower()
            p_num = str(meta.get("page_number") or ch.get("page_number", ""))
            valid_sources.add((d_name, p_num))

        for c in extracted:
            c_doc = c["doc_name"].lower()
            c_page = str(c["page"])
            is_valid = any(
                c_doc in v_doc or v_doc in c_doc
                for v_doc, v_page in valid_sources
                if c_page == v_page or c_page == "N/A"
            )
            if is_valid:
                valid_citations += 1

        accuracy = valid_citations / len(extracted) if extracted else 0.0
        return accuracy >= 0.7, round(accuracy, 2)
