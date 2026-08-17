import os
import pypdf
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.utils.logger import logger
from src.utils.helpers import clean_text

class PDFLoader:
    """Extracts text, page numbers, and structural elements from medical PDFs."""

    def __init__(self, extract_tables: bool = True):
        self.extract_tables = extract_tables

    def load_pdf(self, pdf_path: str, doc_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Loads a single PDF and returns a list of page objects with text and metadata."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info(f"Extracting PDF: {path.name}")
        pages_data = []
        doc_name = path.name

        with pdfplumber.open(path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_number = page_idx + 1
                raw_text = page.extract_text(layout=False) or ""
                cleaned = clean_text(raw_text)

                # Extract tables if requested
                tables = []
                if self.extract_tables:
                    extracted_tables = page.extract_tables() or []
                    for t in extracted_tables:
                        cleaned_table = [[clean_text(str(cell)) if cell else "" for cell in row] for row in t]
                        tables.append(cleaned_table)

                page_obj = {
                    "doc_name": doc_name,
                    "doc_path": str(path),
                    "page_number": page_number,
                    "text": cleaned,
                    "tables": tables,
                    "metadata": doc_metadata or {}
                }
                pages_data.append(page_obj)

        logger.success(f"Extracted {len(pages_data)} pages from {doc_name}")
        return pages_data

    def load_directory(self, dir_path: str, doc_configs: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Loads all PDFs in a directory matching doc_configs or all found .pdf files."""
        dir_p = Path(dir_path)
        all_pages = []
        pdf_files = list(dir_p.glob("*.pdf"))

        config_map = {}
        if doc_configs:
            for c in doc_configs:
                fname = c.get("new_filename") or c.get("filename") or c.get("old_filename")
                if fname:
                    config_map[fname] = c

        for pdf_file in pdf_files:
            meta = config_map.get(pdf_file.name, {"title": pdf_file.stem, "category": "Clinical Guideline"})
            pages = self.load_pdf(str(pdf_file), doc_metadata=meta)
            all_pages.extend(pages)

        return all_pages
