import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import CONFIG
from src.ingestion.pdf_loader import PDFLoader
from src.ingestion.chunker import MedicalChunker
from src.safety.document_validator import validate_medical_document
from src.api.schemas import UploadResponse
from src.utils.logger import logger

def load_chunk_catalog() -> List[Dict[str, Any]]:
    """Loads processed chunk catalog from disk."""
    catalog_path = Path("./data/processed/chunk_catalog.json")
    if catalog_path.exists():
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading chunk catalog: {e}")
    return []

def load_document_registry() -> List[Dict[str, Any]]:
    """Loads document registry metadata from disk."""
    registry_path = Path("./data/processed/document_registry.json")
    if registry_path.exists():
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading document registry: {e}")
    return []

def ingest_pdf_document(
    file_path: str,
    original_filename: str,
    category: str,
    vector_store,
    chunk_catalog: List[Dict[str, Any]],
    document_registry: List[Dict[str, Any]],
    retriever,
    gemini_api_key: Optional[str] = None
) -> UploadResponse:
    """Dynamically validates, chunks, and embeds an uploaded medical PDF with AI Guardrail protection."""
    logger.info(f"AI Guardrail: Validating uploaded document '{original_filename}'...")
    
    # 1. AI Guardrail Validation
    validation = validate_medical_document(file_path, gemini_api_key=gemini_api_key)
    
    if validation.decision == "REJECT":
        logger.warning(f"AI Guardrail REJECTED '{original_filename}': {validation.reason}")
        return UploadResponse(
            status="rejected",
            message=f"Document rejected: {validation.reason}",
            filename=original_filename,
            doc_id="DOC_REJECTED",
            pages_processed=0,
            chunks_indexed=0,
            doclink="",
            decision="REJECT",
            domain=validation.domain,
            document_type=validation.document_type,
            confidence=validation.confidence,
            reason=validation.reason,
            warnings=validation.warnings
        )
    
    # 2. Proceed with Ingestion for PASS / REVIEW
    doc_count = len(document_registry) + 1
    doc_id = f"DOC_{doc_count:03d}"
    
    # Parse PDF pages
    loader = PDFLoader()
    pages = loader.load_pdf(
        pdf_path=file_path,
        doc_metadata={
            "doc_id": doc_id,
            "category": validation.domain or category,
            "title": original_filename,
            "doc_name": original_filename
        }
    )
    total_pages = len(pages) if pages else 1
    
    # Chunk document pages
    chunker = MedicalChunker(
        chunk_size=CONFIG.ingestion.chunk_size,
        chunk_overlap=CONFIG.ingestion.chunk_overlap
    )
    chunks = chunker.chunk_pages(pages)
    
    # Add to ChromaDB vector store
    vector_store.index_chunks(chunks)
    
    # Add to in-memory catalog and re-initialize BM25
    raw_chunks_dicts = [
        {
            "chunk_id": c.chunk_id,
            "doc_id": c.doc_id,
            "doc_name": original_filename,
            "section": c.section,
            "page_number": c.page_number,
            "content": c.content,
            "token_count": c.token_count
        }
        for c in chunks
    ]
    chunk_catalog.extend(raw_chunks_dicts)
    retriever.chunks_corpus = chunk_catalog
    retriever._init_bm25()
    
    # Update registry
    reg_entry = {
        "doc_id": doc_id,
        "filename": original_filename,
        "title": original_filename.replace(".pdf", ""),
        "source": "Uploaded Institutional Guideline",
        "published_year": "2026",
        "category": validation.domain or category,
        "total_pages": total_pages,
        "document_type": validation.document_type
    }
    document_registry.append(reg_entry)

    # Persist catalog & registry to disk
    try:
        catalog_path = Path("./data/processed/chunk_catalog.json")
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(chunk_catalog, f, indent=2, ensure_ascii=False)
        
        registry_path = Path("./data/processed/document_registry.json")
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(document_registry, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Could not persist updated registry/catalog to disk: {e}")

    logger.success(f"Successfully validated & indexed '{original_filename}' ({len(chunks)} vectors, decision: {validation.decision})")
    
    return UploadResponse(
        status="success",
        message=f"Guideline '{original_filename}' passed AI validation and was indexed with {len(chunks)} searchable vectors.",
        filename=original_filename,
        doc_id=doc_id,
        pages_processed=total_pages,
        chunks_indexed=len(chunks),
        doclink=f"{original_filename}#page=1",
        decision=validation.decision,
        domain=validation.domain,
        document_type=validation.document_type,
        confidence=validation.confidence,
        reason=validation.reason,
        warnings=validation.warnings
    )
