from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DoctorContext(BaseModel):
    name: Optional[str] = Field(default="Physician", description="Doctor's name or title")
    specialty: Optional[str] = Field(default="General Medicine", description="Doctor's clinical specialty")
    notes: Optional[str] = Field(default=None, description="Doctor's clinical focus or case notes")

class ChatRequest(BaseModel):
    query: str = Field(..., description="Clinical inquiry from physician", min_length=3)
    language: Optional[str] = Field(default="ar", description="Response language ('ar' or 'en')")
    doctor_context: Optional[DoctorContext] = Field(default_factory=DoctorContext)
    api_key: Optional[str] = Field(default=None, description="Optional override for Gemini/OpenAI API key")
    provider: Optional[str] = Field(default="gemini", description="LLM provider: 'gemini' or 'openai'")

class SourceFound(BaseModel):
    doc_id: str
    doc_title: str
    journal: str
    page_number: int
    section: str
    similarity_score: float
    doclink: str

class Step1QueryAnalysis(BaseModel):
    original_query: str
    disease_category: str
    intent: str
    status: str = "Completed"

class Step2Retrieval(BaseModel):
    search_type: str = "Hybrid (Dense Vector + BM25 Lexical)"
    retrieved_count: int
    sources_found: List[SourceFound]

class Step3Safety(BaseModel):
    confidence_score: float
    passed_safety_gate: bool
    hallucination_check: str
    status: str

class Step4Synthesis(BaseModel):
    model_used: str
    latency_seconds: float
    status: str = "Generated"

class RAGPipelineSimulation(BaseModel):
    step_1_query_analysis: Step1QueryAnalysis
    step_2_retrieval: Step2Retrieval
    step_3_safety_and_verification: Step3Safety
    step_4_synthesis: Step4Synthesis

class CitationItem(BaseModel):
    citation_id: int
    source: str
    page: int
    section: str
    doclink: str

class ClinicalResponse(BaseModel):
    summary: str
    detailed_recommendations: List[str]
    citations: List[CitationItem]
    medical_disclaimer: str
    confidence_score: float = 0.85
    confidence_percentage: str = "85%"


class MedicalDomains(BaseModel):
    active: List[str]
    upcoming_soon: List[str]

class ChatResponse(BaseModel):
    status: str = "success"
    language: str
    doctor_context: DoctorContext
    rag_pipeline_simulation: RAGPipelineSimulation
    clinical_response: ClinicalResponse
    available_medical_domains: MedicalDomains

class UploadResponse(BaseModel):
    status: str = "success"
    message: str
    filename: str
    doc_id: str
    pages_processed: int
    chunks_indexed: int
    doclink: str

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    app_name: str = "VERA Clinical Intelligence Platform"
    vector_store: Dict[str, Any]
    active_domains_count: int
