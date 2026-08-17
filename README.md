# VERA - Verified Evidence Retrieval Assistant
### Evidence-Grounded Clinical Decision Support Platform

VERA is an evidence-grounded Clinical Decision Support (CDS) Retrieval-Augmented Generation (RAG) platform designed for physicians, geneticists, and clinical researchers.

The system synthesizes clinical recommendations strictly from peer-reviewed medical guidelines and genomic literature with transparent in-line citations (`[Document Name | Page Number]`), verifiable safety guardrails, and dynamic BYOK (Bring Your Own Key) LLM integration.

---

## Key Features

- **Strict Evidence Grounding**: Enforces factual grounding against verified clinical literature, preventing ungrounded claims and hallucinations.
- **Hybrid Retrieval**: Combines semantic dense vector search (ChromaDB + SentenceTransformers) with lexical BM25 retrieval and Reciprocal Rank Fusion (RRF).
- **Safety Confidence Gating**: Automatically verifies retrieval quality prior to generation and blocks out-of-scope or unverified inquiries.
- **Transparent Citations**: Every clinical point links directly to its source document and exact page number (`[Document.pdf#page=X]`).
- **Dynamic BYOK Integration**: Supports dynamic LLM API key injection per request (Google Gemini / OpenAI), with automatic fallback to system defaults.
- **Dynamic Guideline Ingestion**: Enables on-the-fly parsing, chunking, and embedding of newly uploaded institutional medical PDFs.
- **Production-Ready FastAPI Backend**: High-performance asynchronous API designed for direct integration with mobile (Flutter) and web clients.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INGESTION & INDEXING LAYER                               │
│    - PDF Parsing (pypdf)                                    │
│    - Section-Aware Medical Chunking (500 tokens / 100 ov.)  │
│    - Dense Embeddings (BAAI/bge-small-en-v1.5) + BM25 Index │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. HYBRID RETRIEVAL LAYER                                   │
│    - Clinical Query Analysis & Intent Extraction            │
│    - Dense Vector Search (ChromaDB) + Lexical BM25 Search   │
│    - Reciprocal Rank Fusion (RRF) & Top-K Extraction        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SAFETY CONFIDENCE GATE                                   │
│    - Similarity Threshold Check (Min Score >= 0.60)         │
│    - Ambiguity / Out-of-Scope Detection                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. GROUNDED SYNTHESIS & AUDIT LAYER                         │
│    - LLM Generation (Gemini 3.1 Flash Lite / OpenAI)        │
│    - In-line Citation Extraction & Verification             │
│    - Post-Generation Hallucination & Faithfulness Audit     │
└─────────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AbdoTechno/vera.git
   cd vera
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to configure your API keys and parameters:
   ```ini
   GEMINI_API_KEY=your_gemini_api_key_here
   DEFAULT_LLM_PROVIDER=gemini
   DEFAULT_LLM_MODEL=models/gemini-3.1-flash-lite
   CONFIDENCE_THRESHOLD=0.60
   ```

---

## Running the Server

Start the FastAPI application using the runner script or Uvicorn:

```bash
# Option 1: Using the runner script
python run_server.py

# Option 2: Using Uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Interactive API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Static PDF Guideline Viewer:** [http://localhost:8000/pdfs](http://localhost:8000/pdfs)

---

## API Reference

### 1. Clinical Chat & RAG Simulation
`POST /api/v1/chat`

Processes a physician's inquiry, executes the 4-step RAG pipeline, and returns structured clinical recommendations with verified citations and confidence scoring.

**Headers (Optional - BYOK):**
- `X-Gemini-API-Key`: Physician's custom Gemini API key.
- `X-OpenAI-API-Key`: Physician's custom OpenAI API key.

**Request Body:**
```json
{
  "query": "What are the initiation criteria and dosing considerations for Nusinersen in SMA patients?",
  "language": "en",
  "doctor_context": {
    "name": "Dr. Sarah",
    "specialty": "Pediatric Neurology",
    "notes": "Early intervention assessment"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "language": "en",
  "rag_pipeline_simulation": {
    "step_1_query_analysis": {
      "original_query": "What are the initiation criteria and dosing considerations for Nusinersen in SMA patients?",
      "disease_category": "Spinal Muscular Atrophy (SMA) Guidelines",
      "intent": "Treatment Protocol & Dosing Guidelines",
      "status": "Completed"
    },
    "step_2_retrieval": {
      "search_type": "Hybrid (Dense Vector + BM25 Lexical)",
      "retrieved_count": 4,
      "sources_found": [ ... ]
    },
    "step_3_safety_and_verification": {
      "confidence_score": 0.82,
      "passed_safety_gate": true,
      "hallucination_check": "Verified against retrieved clinical guidelines",
      "status": "Safe & Grounded"
    },
    "step_4_synthesis": {
      "model_used": "Gemini (models/gemini-3.1-flash-lite)",
      "latency_seconds": 2.15,
      "status": "Generated"
    }
  },
  "clinical_response": {
    "confidence_score": 0.82,
    "confidence_percentage": "82%",
    "summary": "Nusinersen is an antisense oligonucleotide approved for 5q SMA treatment across pediatric and adult populations...",
    "detailed_recommendations": [
      "Administration Route and Schedule: Nusinersen is administered via intrathecal bolus injection [ClinPediatr_2023_SMA_Treatment_Best_Practices.pdf | Page 4].",
      "Clinical Decision-Making Factors: Evaluation of patient age and SMN2 copy number is required prior to initiation [ClinPediatr_2023_SMA_Treatment_Best_Practices.pdf | Page 1].",
      "Laboratory Monitoring: Baseline and interval platelet counts, coagulation tests, and spot urine protein must be evaluated before each dose [ClinPediatr_2023_SMA_Treatment_Best_Practices.pdf | Page 4]."
    ],
    "citations": [
      {
        "citation_id": 1,
        "source": "ClinPediatr_2023_SMA_Treatment_Best_Practices.pdf",
        "page": 4,
        "section": "Dosing & Administration",
        "doclink": "ClinPediatr_2023_SMA_Treatment_Best_Practices.pdf#page=4"
      }
    ],
    "medical_disclaimer": "VERA is an evidence-grounded research assistant and does not replace autonomous clinical diagnosis or medical practitioner judgment."
  }
}
```

---

### 2. Upload Institutional Guideline
`POST /api/v1/upload-document`

Dynamically ingests and indexes a new medical PDF into ChromaDB and the hybrid search catalog.

- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: PDF file (Required).
  - `title`: Guideline title (Optional).
  - `category`: Medical category (Optional).

---

### 3. Medical Domains Catalog
`GET /api/v1/domains`

Lists currently active clinical domains (e.g., SMA, Chromosomal Rearrangements) and upcoming research areas.

---

### 4. Indexed Document Registry
`GET /api/v1/documents`

Returns all currently indexed medical literature, source metadata, and static PDF download links.

---

## Project Structure

```text
vera/
├── config/                  # Configuration files
│   ├── config.yaml          # Global pipeline parameters (Chunk size, Top-K, thresholds)
│   └── README.md
│
├── data/                    # Clinical data & storage
│   ├── raw_pdfs/            # Approved medical literature and PDF guidelines
│   ├── knowledge_base/      # Structured markdown medical knowledge base
│   └── README.md
│
├── src/                     # Core application source code
│   ├── api/                 # FastAPI routes, schemas, and pipeline orchestration
│   │   ├── main.py          # FastAPI application entry point with lifespan pre-warming
│   │   ├── routes.py        # REST API endpoint definitions
│   │   ├── schemas.py       # Pydantic data contracts
│   │   └── service.py       # RAG pipeline orchestration service
│   ├── ingestion/           # Document ingestion, PDF loading, and section chunking
│   ├── embeddings/          # Vector store management and dense embeddings
│   ├── retrieval/           # Hybrid retrieval (ChromaDB + BM25) and query expansion
│   ├── generation/          # Grounded synthesis, prompt templates, and citation formatting
│   ├── safety/              # Confidence gating, hallucination checks, and refusal engine
│   ├── evaluation/          # Retrieval and generation evaluation metrics
│   └── utils/               # Logging, configuration loader, and helper utilities
│
├── notebooks/               # Interactive tutorials and verification notebooks
│   ├── VERA_All_In_One_Learning_Lab.ipynb  # Self-contained 10-step interactive RAG lab
│   └── README.md
│
├── tests/                   # Automated unit and integration test suite
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   ├── test_generation.py
│   └── test_safety.py
│
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
├── run_server.py            # Local development server runner
└── README.md                # Project documentation
```

---

## Testing & Quality Assurance

Run the automated test suite to verify pipeline functionality:

```bash
# Run all tests
pytest tests/ -v

# Run specific component tests
pytest tests/test_retrieval.py -v
pytest tests/test_safety.py -v
```

---

## Medical Disclaimer

VERA is intended exclusively for clinical decision support and research assistance by licensed medical professionals. It is not an autonomous diagnostic system and does not replace professional clinical evaluation, diagnosis, or patient management.
