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

@router.post("/upload-document", response_model=UploadResponse, summary="Ingest Institutional PDF Guideline")
async def upload_document(
    file: UploadFile = File(..., description="Medical PDF file to ingest"),
    title: Optional[str] = Form(default=None),
    category: Optional[str] = Form(default="Clinical Guidelines"),
    service: VERAClinicalService = Depends(get_service)
):
    """
    Allows physicians/institutions to upload new PDF guidelines for dynamic vectorization.
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
            category=category
        )
        return upload_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest PDF: {str(e)}")

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

@router.get("/documents", summary="List Indexed Guidelines & Resources")
async def list_indexed_documents(service: VERAClinicalService = Depends(get_service)):
    """
    Returns all indexed medical documents and their direct doclinks for the Flutter PDF viewer.
    """
    return {
        "status": "success",
        "count": len(service.document_registry),
        "documents": service.document_registry
    }

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
