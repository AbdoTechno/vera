import re
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.utils.logger import logger

class Chunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    doc_id: str
    doc_name: str
    section: str
    page_number: int
    content: str
    token_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MedicalChunker:
    """Implements section-aware and token-bounded chunking for clinical guidelines."""

    SECTION_PATTERNS = [
        r'^(?:[0-9]+\.|\b[IVXLCDM]+\.|\b[A-Z]\.)\s+[A-Z][A-Za-z0-9\s,-]+$',
        r'^(?:ABSTRACT|INTRODUCTION|BACKGROUND|METHODS|RESULTS|DISCUSSION|TREATMENT|RECOMMENDATIONS|CONCLUSION|REFERENCES|BEST PRACTICES|DIAGNOSIS)\b',
        r'^[A-Z\s]{4,40}$' # All uppercase headers
    ]

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100, min_chunk_length: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length

    def is_section_header(self, line: str) -> bool:
        """Detects if a single line acts as a clinical section header."""
        line = line.strip()
        if len(line) < 3 or len(line) > 80:
            return False
        for pattern in self.SECTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def chunk_pages(self, pages_data: List[Dict[str, Any]]) -> List[Chunk]:
        """Creates section-aware, metadata-rich chunks from extracted page data."""
        chunks: List[Chunk] = []
        current_section = "General Overview"

        for page in pages_data:
            doc_name = page["doc_name"]
            page_num = page["page_number"]
            doc_meta = page.get("metadata", {})
            doc_id = doc_meta.get("doc_id", doc_name.split(".")[0])
            text = page.get("text", "")

            # Split text by paragraphs/lines
            lines = text.split("\n")
            current_buffer = []
            current_words_count = 0

            for line in lines:
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue

                if self.is_section_header(cleaned_line):
                    # Flush current buffer if it has content
                    if current_buffer and current_words_count >= self.min_chunk_length:
                        chunk_text = " ".join(current_buffer)
                        chunks.append(Chunk(
                            doc_id=doc_id,
                            doc_name=doc_name,
                            section=current_section,
                            page_number=page_num,
                            content=chunk_text,
                            token_count=current_words_count,
                            metadata=doc_meta
                        ))
                        current_buffer = []
                        current_words_count = 0
                    current_section = cleaned_line

                words = cleaned_line.split()
                current_buffer.append(cleaned_line)
                current_words_count += len(words)

                # Check if buffer exceeded chunk size
                if current_words_count >= self.chunk_size:
                    chunk_text = " ".join(current_buffer)
                    chunks.append(Chunk(
                        doc_id=doc_id,
                        doc_name=doc_name,
                        section=current_section,
                        page_number=page_num,
                        content=chunk_text,
                        token_count=current_words_count,
                        metadata=doc_meta
                    ))
                    # Overlap handling: retain the last few words
                    overlap_words = words[-min(len(words), self.chunk_overlap):]
                    current_buffer = [" ".join(overlap_words)]
                    current_words_count = len(overlap_words)

            # Flush remaining words on the page
            if current_buffer and current_words_count >= self.min_chunk_length:
                chunk_text = " ".join(current_buffer)
                chunks.append(Chunk(
                    doc_id=doc_id,
                    doc_name=doc_name,
                    section=current_section,
                    page_number=page_num,
                    content=chunk_text,
                    token_count=current_words_count,
                    metadata=doc_meta
                ))

        logger.success(f"Generated {len(chunks)} structured chunks across {len(pages_data)} pages.")
        return chunks
