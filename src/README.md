# Source Code Architecture (`src/`)

This directory contains the modular architecture of the VERA (Verified Evidence Retrieval Assistant) platform. Each module represents an independent, unit-tested component of the clinical decision support pipeline.

---

## Directory Organization

```
src/
|-- api/                       # API routing, Pydantic schemas, and service orchestration
|   |-- document_manager.py    # Document catalog management and ingestion workflows
|   |-- main.py                # FastAPI application initialization and lifespans
|   |-- query_analyzer.py      # Language detection, intent classification, and key validation
|   |-- response_formatter.py  # Structured bullet response and citation formatting
|   |-- routes.py              # REST API endpoints (/chat, /upload-document, /health)
|   |-- schemas.py             # Strongly-typed Pydantic request and response models
|   |-- service.py             # Central clinical RAG orchestration service
|   `-- telegram_service.py    # Telegram bot webhook handler and HTML card formatter
|-- config.py                  # Dynamic configuration loader and hyperparameter registry
|-- embeddings/                # Local dense embeddings and ChromaDB vector store manager
|   |-- embedder.py            # Local BAAI/bge-small-en-v1.5 sentence-transformers wrapper
|   `-- vector_store.py        # ChromaDB persistent/in-memory collection manager
|-- evaluation/                # Benchmark suites and evaluation metrics (RAGAS / Precision@K)
|   |-- benchmark_runner.py    # Automated benchmark execution engine
|   `-- metrics.py             # Retrieval and generation quality evaluation metrics
|-- generation/                # LLM synthesis and citation extraction
|   |-- citation_formatter.py  # Page-level citation tag parser and validator
|   |-- generator.py           # Multi-provider LLM client (Google Gemini / OpenAI)
|   `-- prompts.py             # Strict clinical system prompts and grounding templates
|-- ingestion/                 # Document parsing and section-aware chunking
|   |-- chunker.py             # Section-aware recursive clinical text splitter
|   |-- metadata_extractor.py  # Document-level and section-level metadata extractor
|   `-- pdf_loader.py          # PDF text and table extraction with page tracking
|-- retrieval/                 # Hybrid search and ranking subsystem
|   |-- hybrid_retriever.py    # Hybrid RRF (Dense Vector + Sparse BM25) retriever
|   |-- query_expansion.py     # Domain-specific synonym and terminology mapper
|   `-- semantic_search.py     # Standalone dense semantic search utility
|-- safety/                    # Clinical guardrails, confidence gates, and refusal engine
|   |-- confidence_gate.py     # Retrieval similarity threshold evaluator
|   |-- document_validator.py  # AI document ingestion guardrail and smart profiler
|   |-- hallucination_checker.py # Faithfulness and grounding verification
|   `-- refusal_engine.py      # Pre-retrieval emergency and out-of-scope interceptor
`-- utils/                     # Shared logging and environment utilities
    `-- logger.py              # Structured console and container-safe stream logger
```

---

## Architectural Principles

1. **Deterministic Safety**: All safety checks (pre-retrieval refusal, confidence gates, smart document profile verification) operate deterministically before calling generative language models.
2. **Decoupled Components**: Ingestion, vectorization, retrieval, and generation can be executed and tested independently.
3. **Local Embedding Optimization**: Embeddings are computed locally using optimized single-thread CPU execution to prevent cloud container memory saturation.
4. **Ephemerality**: Non-indexed runtime documents are processed in temporary memory buffers to prevent disk storage bloat.
