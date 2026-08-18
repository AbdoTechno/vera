# Data Management & Storage (`data/`)

This directory manages the lifecycle of medical guideline documents, extracted text chunks, and structured knowledge catalogs.

---

## Directory Organization

```
data/
|-- processed/            # Structured chunk catalogs and document registries (JSON)
|   |-- chunk_catalog.json     # Section-aware chunk catalog with page indices
|   `-- document_registry.json # Registered guideline metadata
|-- raw_pdfs/             # Institutional medical guideline PDF documents
`-- vector_db/            # Local vector database storage (ChromaDB / FAISS)
```

---

## Subdirectories

1. **`raw_pdfs/`**:
   - Stores source institutional guidelines (such as Spinal Muscular Atrophy consensus statements and long-read sequencing studies).

2. **`processed/`**:
   - Contains extracted, deduplicated chunk catalogs (`chunk_catalog.json`) and document metadata registries (`document_registry.json`) with page numbers and section labels.
