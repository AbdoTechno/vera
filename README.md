---
title: VERA Clinical Intelligence Platform
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
---

# VERA: Verified Evidence Retrieval Assistant
### Evidence-Grounded Clinical Decision Support Platform

VERA is an evidence-grounded Clinical Decision Support (CDS) Retrieval-Augmented Generation (RAG) platform designed for medical practitioners, geneticists, and clinical researchers.

The platform synthesizes clinical recommendations strictly from verified medical guidelines, peer-reviewed literature, and genomic datasets with verified in-line citations (`[Document Name | Page Number]`), verifiable safety guardrails, and dynamic BYOK (Bring Your Own Key) LLM integration.

---

## System Capabilities

- **Strict Evidence Grounding**: Enforces factual grounding against verified clinical literature, preventing ungrounded claims and hallucinations.
- **Hybrid Retrieval Architecture**: Combines semantic dense vector search (`ChromaDB` + `BAAI/bge-small-en-v1.5`) with lexical `BM25` retrieval and Reciprocal Rank Fusion (RRF).
- **Safety Confidence Gating**: Automatically evaluates retrieval similarity scores prior to generation and blocks out-of-scope or unverified queries.
- **Transparent Provenance**: Every clinical recommendation links directly to its source document, clinical section, and exact page number.
- **Dynamic BYOK Key Management**: Supports runtime API key injection per request (Google Gemini and OpenAI), with automatic fallback to system defaults.
- **AI Document Ingestion Guardrail**: Automatically evaluates uploaded institutional PDF guidelines using smart profile sampling to prevent corrupt or non-medical indexing.
- **Document-Scoped Chat**: Allows targeting clinical inquiries to a specific document (`doc_id` / `doc_name`) without cross-contamination.
- **Zero-Retention Session Processing**: Processes uploaded guideline files in ephemeral memory, avoiding unauthorized permanent disk persistence.
- **Multi-Platform Interfaces**: Production-ready FastAPI REST API integrated with a Flutter mobile/web client and a 24/7 Telegram bot webhook.

---

## Architectural Workflow

The query execution pipeline consists of four sequential stages:

```
+-------------------------------------------------------------------------+
| 1. PRE-RETRIEVAL & QUERY ANALYSIS                                       |
|    - Emergency Detection & Immediate Life-Safety Refusal                |
|    - Out-of-Scope Pre-Filtering (Non-medical, recipes, general chat)    |
|    - Clinical Intent Extraction (Dosing, Diagnosis, Eligibility)        |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 2. HYBRID EVIDENCE RETRIEVAL                                            |
|    - Dense Vector Search (ChromaDB + bge-small-en-v1.5, 384 dimensions) |
|    - Sparse Lexical Search (Rank-BM25 on Clinical Tokenized Corpus)     |
|    - Reciprocal Rank Fusion (RRF, k=60) & Metadata Top-K Extraction    |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 3. SAFETY & VERIFICATION GATING                                         |
|    - Similarity Threshold Evaluation (Min Confidence Score >= 0.60)     |
|    - Insufficient Evidence Refusal with Zero-Hallucination Enforcement  |
|    - Dynamic Real-Time Grounded Confidence Scoring                      |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 4. GROUNDED SYNTHESIS & ATTRIBUTION                                     |
|    - Context-Constrained LLM Generation (Gemini 3.1 Flash Lite / OpenAI)|
|    - Citation Extraction & Page Linking ([Document.pdf#page=X])        |
|    - Structured Bullet Formatting & Post-Generation Faithfulness Check  |
+-------------------------------------------------------------------------+
```

---

## Project Structure

```
.
|-- Dockerfile                     # Production container configuration
|-- README.md                      # Primary project documentation
|-- app.py                         # Hugging Face Gradio + FastAPI mount entrypoint
|-- config/                        # Global system configuration and hyperparameters
|   `-- config.yaml
|-- data/                          # Guideline repository and processed catalogs
|   |-- processed/
|   |   |-- chunk_catalog.json     # Processed and deduplicated chunk catalog
|   |   `-- document_registry.json # Registered guideline metadata
|   `-- raw_pdfs/                  # Verified institutional PDF guidelines
|-- notebooks/                     # Exploratory research and pipeline verification
|-- pytest.ini                     # Automated test configuration
|-- requirements.txt               # Production and development dependencies
|-- run_server.py                  # Local FastAPI server entrypoint
|-- run_telegram_bot.py            # Standalone Telegram long-polling runner
|-- src/                           # Core platform source code
|   |-- api/                       # FastAPI routes, schemas, and orchestration
|   |-- embeddings/                # Vector store manager and local embedding model
|   |-- evaluation/                # Benchmark suites and evaluation metrics
|   |-- generation/                # LLM synthesis and citation formatters
|   |-- ingestion/                 # PDF extraction and section-aware chunking
|   |-- retrieval/                 # Hybrid search, BM25, and RRF fusion
|   |-- safety/                    # Refusal engine, confidence gates, and guardrails
|   `-- utils/                     # Structured logging and environment helpers
`-- tests/                         # Comprehensive automated test suite
```

---

## Getting Started

### Prerequisites

- Python 3.10 to 3.13
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
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```ini
   GEMINI_API_KEY=your_google_gemini_api_key_here
   DEFAULT_LLM_PROVIDER=gemini
   DEFAULT_LLM_MODEL=models/gemini-3.1-flash-lite
   CONFIDENCE_THRESHOLD=0.60
   ```

---

## Running the Platform

### Running the API Server

Start the FastAPI application locally:

```bash
# Option 1: Using the runner script
python run_server.py

# Option 2: Using Uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## API Reference

### 1. Clinical Chat & RAG Simulation
`POST /api/v1/chat`

Processes clinical inquiries, executes hybrid retrieval and safety verification, and returns structured recommendations with verified citations.

**Request Body:**
```json
{
  "query": "What are the recommended loading doses for Nusinersen in SMA?",
  "language": "en",
  "provider": "gemini",
  "doctor_context": {
    "specialty": "Pediatric Neurology",
    "experience_level": "Consultant",
    "notes": "Evaluating loading schedule"
  },
  "doc_id": null
}
```

### 2. Ingest Institutional Guideline with AI Guardrail
`POST /api/v1/upload-document`

Validates an uploaded medical PDF using smart profile sampling and indexes its sections dynamically into the active vector catalog.

### 3. Document Session Cleanup
`DELETE /api/v1/documents/{doc_id_or_filename}`

Removes temporary session document vectors and catalog entries from active memory upon session completion.

### 4. Telegram Webhook Endpoint
`POST /telegram/webhook`

Handles incoming Telegram bot webhook updates, delivering structured cards with verified citations.

---

## Testing & Quality Assurance

Run the automated test suite covering all platform layers:

```bash
pytest -v
```

All 19 test cases validate:
- In-line citation extraction and page linking
- Section-aware chunking boundaries
- Hybrid retrieval with Reciprocal Rank Fusion
- Emergency and out-of-scope safety gating
- Confidence gate rejection thresholds
- Telegram formatting and webhook handlers

---

## License & Compliance

VERA is designed as a research-grade clinical decision support assistant for licensed healthcare professionals. It does not replace independent clinical judgment or autonomous medical diagnosis.
