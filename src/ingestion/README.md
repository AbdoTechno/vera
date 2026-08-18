# Document Ingestion & Section-Aware Chunking (`src/ingestion/`)

This module handles document ingestion, PDF parsing, text normalization, and section-aware clinical chunking.

---

## Core Capabilities

1. **High-Fidelity PDF Extraction (`pdf_loader.py`)**:
   - Uses `pdfplumber` and `pypdf` to extract text from clinical guideline documents.
   - Preserves original page numbering across all extracted text blocks.
   - Cleans broken line wraps, hyphenated medical terms, and whitespace irregularities.

2. **Section-Aware Clinical Chunking (`chunker.py`)**:
   - Splits text hierarchically using clinical section headers (`Dosing`, `Administration`, `Diagnosis`, `Monitoring`, `Adverse Reactions`).
   - Default parameters: **500 tokens chunk size** with **100 tokens overlap** (20% overlap window).
   - Preserves semantic boundaries so dosing tables and eligibility criteria are not split across disjoint chunks.

3. **Metadata Enrichment (`metadata_extractor.py`)**:
   - Tags each chunk with `doc_id`, `doc_name`, `page_number`, `section`, and `token_count`.
   - Enables verified in-line citations and page-exact retrieval.

---

## Module Files

- `pdf_loader.py`: PDF loader with page-index tracking and text sanitization.
- `chunker.py`: Section-aware recursive clinical text splitter.
- `metadata_extractor.py`: Metadata extraction and validation utilities.
