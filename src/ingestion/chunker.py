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
    page_number: int # Starting page number of the chunk
    content: str
    token_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MedicalChunker:
    """Implements section-aware and token-bounded chunking for clinical guidelines.
    (splits text into chunks while respecting sections and word limits.)"""

    SECTION_PATTERNS = [
        # handle multi-level numbered headings like 1.1., 1.2.3.
        r'^(\d+(\.\d+)*)\.?\s+[A-Z][A-Za-z0-9\s,;\-—]+$',
        r'^(?:ABSTRACT|INTRODUCTION|BACKGROUND|METHODS|RESULTS|DISCUSSION|TREATMENT|RECOMMENDATIONS|CONCLUSION|REFERENCES|BEST PRACTICES|DIAGNOSIS|ETHICS)\b',
        r'^[A-Z\s]{4,80}$' # All uppercase headers, allowing longer headers
    ]

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100, min_chunk_length: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length

    def is_section_header(self, line: str) -> bool:
        """Detects if a single line matches any section header pattern.."""
        line = line.strip()
        if len(line) < 3 or len(line) > 100: # max length for headers
            return False
        for pattern in self.SECTION_PATTERNS:
            if re.search(pattern, line):
                return True
        return False

    def chunk_pages(self, pages_data: List[Dict[str, Any]]) -> List[Chunk]:
        """Creates section-aware, metadata-rich chunks from extracted page data."""
        all_chunks: List[Chunk] = []
        
        current_buffer_lines = [] # Stores lines for the current potential chunk
        current_section = "General Overview"
        current_doc_id = None
        current_doc_name = None
        current_doc_meta = {}
        current_chunk_start_page = None # Page number of the *first* line in current_buffer_lines

        def _add_chunk_from_buffer(buffer_text_lines: List[str], page_for_chunk: int):
            nonlocal all_chunks
            if not buffer_text_lines:
                return
            
            chunk_content = " ".join(buffer_text_lines)
            words_count = len(chunk_content.split())
            
            if words_count >= self.min_chunk_length:
                 all_chunks.append(Chunk(
                    chunk_id=str(uuid.uuid4())[:8], # Generate new ID for each flushed chunk
                    doc_id=current_doc_id,
                    doc_name=current_doc_name,
                    section=current_section,
                    page_number=page_for_chunk,
                    content=chunk_content,
                    token_count=words_count,
                    metadata=current_doc_meta
                ))

        for page in pages_data:
            doc_name = page["doc_name"]
            page_num = page["page_number"]
            doc_meta = page.get("metadata", {})
            doc_id = doc_meta.get("doc_id", doc_name.split(".")[0])
            text = page.get("text", "")
            lines = text.split("\n")

            # Check for new document. If so, flush existing buffer and reset context.
            if current_doc_id is None or current_doc_id != doc_id:
                if current_buffer_lines:
                    _add_chunk_from_buffer(current_buffer_lines, current_chunk_start_page)
                current_buffer_lines = []
                current_section = "General Overview"
                current_doc_id = doc_id
                current_doc_name = doc_name
                current_doc_meta = doc_meta
                current_chunk_start_page = None # Reset for new document

            # If current_buffer_lines is empty, it means a new chunk is starting.
            # Set its starting page to the current page.
            if not current_buffer_lines and current_chunk_start_page is None:
                current_chunk_start_page = page_num

            for line_idx, line in enumerate(lines):
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue

                if self.is_section_header(cleaned_line):
                    # If we have content for the OLD section, flush it
                    if current_buffer_lines:
                        _add_chunk_from_buffer(current_buffer_lines, current_chunk_start_page)
                        current_buffer_lines = [] # Clear buffer after flushing
                    
                    current_section = cleaned_line # Update section for *new* content
                    current_chunk_start_page = page_num # New chunk starts with this new section
                    continue # Do not add header to content, it's metadata

                # Accumulate content in the buffer
                current_buffer_lines.append(cleaned_line)
                current_words_in_buffer = len(" ".join(current_buffer_lines).split())

                # If current buffer content exceeds chunk_size, split it
                if current_words_in_buffer >= self.chunk_size:
                    # Find a good split point within the accumulated text
                    full_text_so_far = " ".join(current_buffer_lines)
                    words_so_far = full_text_so_far.split()

                    # Determine the split index to make the first part ~chunk_size
                    # This prioritizes sentence breaks if possible for better coherence
                    split_idx = self.chunk_size
                    temp_chunk_text = " ".join(words_so_far[:split_idx])
                    
                    # Look for a sentence-ending punctuation near the target split_idx
                    last_period_idx = max(temp_chunk_text.rfind('.'), 
                                          temp_chunk_text.rfind('!'), 
                                          temp_chunk_text.rfind('?'))

                    # If a suitable punctuation is found and it's not too far off
                    if last_period_idx != -1 and (split_idx - last_period_idx < (self.chunk_size * 0.2)) and (last_period_idx > self.min_chunk_length * 0.8):
                        # Adjust split_idx to be after the sentence end
                        split_idx = len(temp_chunk_text[:last_period_idx+1].split())
                    
                    # Ensure split_idx is not too small due to sentence splitting
                    if split_idx < self.min_chunk_length:
                        split_idx = self.chunk_size # Fallback to hard split if sentence split is too aggressive

                    # Form the chunk to add
                    chunk_to_add_words = words_so_far[:split_idx]
                    _add_chunk_from_buffer(chunk_to_add_words, current_chunk_start_page)

                    # Prepare the remaining content for the next buffer with overlap
                    remaining_words_start_idx = max(0, split_idx - self.chunk_overlap)
                    remaining_words = words_so_far[remaining_words_start_idx:]
                    
                    current_buffer_lines = [" ".join(remaining_words)] if remaining_words else []
                    current_chunk_start_page = page_num # The subsequent chunk (from remaining content) starts from current page

        # After all pages and lines are processed, flush any remaining content
        if current_buffer_lines:
            _add_chunk_from_buffer(current_buffer_lines, current_chunk_start_page)
        logger.success(f"Generated {len(all_chunks)} structured chunks.")
        return all_chunks
