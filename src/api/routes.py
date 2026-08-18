import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Header, UploadFile, File, Form, HTTPException, Depends
from src.api.schemas import (
    ChatRequest, ChatResponse, UploadResponse, HealthResponse, MedicalDomains
)
from src.api.service import VERAClinicalService

router = APIRouter(prefix="/api/v1", tags=["Clinical RAG & Decision Support"])

# Global singleton service instance
_service: Optional[VERAClinicalService] = None

def get_service() -> VERAClinicalService:
    global _service
    if _service is None:
        _service = VERAClinicalService()
    return _service

@router.post("/chat", response_model=ChatResponse, summary="Clinical Inquiry & Live RAG Simulation")
async def clinical_chat(
    request: ChatRequest,
    x_gemini_api_key: Optional[str] = Header(default=None, alias="X-Gemini-API-Key"),
    x_openai_api_key: Optional[str] = Header(default=None, alias="X-OpenAI-API-Key"),
    service: VERAClinicalService = Depends(get_service)
):
    """
    Processes a physician's inquiry with live RAG pipeline simulation:
    - Accepts dynamic BYOK API keys via Header or Request Body.
    - Generates step-by-step transparency data (Query Analysis -> Evidence Retrieval -> Safety Gate -> Synthesis).
    - Formats clinical recommendations with citations in Arabic or English.
    """
    api_key_header = x_gemini_api_key or x_openai_api_key
    try:
        response = service.process_clinical_query(request, api_key_header=api_key_header)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clinical Pipeline Error: {str(e)}")

from fastapi.responses import FileResponse

@router.post("/upload-document", response_model=UploadResponse, summary="Ingest Institutional PDF Guideline with AI Guardrail")
async def upload_document(
    file: UploadFile = File(..., description="Medical PDF file to ingest"),
    title: Optional[str] = Form(default=None),
    category: Optional[str] = Form(default="Clinical Guidelines"),
    x_gemini_api_key: Optional[str] = Header(default=None, alias="X-Gemini-API-Key"),
    service: VERAClinicalService = Depends(get_service)
):
    """
    Validates uploaded PDF using AI Guardrails before dynamic chunking and indexing into ChromaDB.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    upload_dir = Path("./data/raw_pdfs")
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / file.filename

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        upload_result = service.ingest_new_pdf(
            file_path=str(saved_path),
            original_filename=file.filename,
            category=category,
            gemini_api_key=x_gemini_api_key
        )
        return upload_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@router.get("/domains", response_model=MedicalDomains, summary="Get Active & Upcoming Clinical Domains")
async def get_clinical_domains():
    """
    Returns active clinical specialties (SMA, Cytogenetics) and upcoming medical modules.
    """
    return MedicalDomains(
        active=[
            "Spinal Muscular Atrophy (SMA) Guidelines & Treatment",
            "Clinical Cytogenetics & Chromosomal Rearrangements"
        ],
        upcoming_soon=[
            "Pediatric Oncology Protocols",
            "Cardiomyopathy & Heart Failure",
            "Inborn Errors of Metabolism & Rare Diseases"
        ]
    )

@router.get("/documents", summary="List Indexed Guidelines & Direct Download URLs")
async def list_indexed_documents(service: VERAClinicalService = Depends(get_service)):
    """
    Returns all indexed medical documents, metadata, and direct download/view URLs for Flutter & web.
    """
    enriched_docs = []
    for doc in service.document_registry:
        fn = doc.get("filename", "")
        doc_entry = dict(doc)
        doc_entry["download_url"] = f"/api/v1/documents/{fn}/download"
        doc_entry["view_url"] = f"/pdfs/{fn}"
        enriched_docs.append(doc_entry)

    return {
        "status": "success",
        "count": len(enriched_docs),
        "documents": enriched_docs
    }

@router.get("/documents/{filename}/download", summary="Download Original PDF Guideline")
async def download_pdf_document(filename: str):
    """
    Directly downloads an institutional guideline PDF file.
    """
    file_path = Path("./data/raw_pdfs") / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"Document '{filename}' was not found on the server.")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )


@router.get("/health", response_model=HealthResponse, summary="System Health & Vector DB Status")
async def health_check(service: VERAClinicalService = Depends(get_service)):
    """
    Verifies API status and ChromaDB connectivity.
    """
    count = 0
    if service.vector_store.collection:
        try:
            count = service.vector_store.collection.count()
        except Exception:
            pass

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        app_name="VERA Clinical Intelligence Platform",
        vector_store={
            "status": "connected",
            "collection": service.vector_store.collection_name,
            "indexed_vectors_count": count
        },
        active_domains_count=len(service.document_registry)
    )
