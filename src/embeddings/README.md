# Embeddings & Vector Store Management (`src/embeddings/`)

This module manages dense vector representations, local embedding generation, and ChromaDB vector collection operations.

---

## Technical Specifications

1. **Embedding Model (`embedder.py`)**:
   - Model: `BAAI/bge-small-en-v1.5` (via `sentence-transformers`).
   - Dimension: 384 dimensions.
   - Execution: Optimized local CPU execution with single-thread PyTorch configuration and disabled gradients (`torch.set_grad_enabled(False)`).
   - Latency: Approximately 15ms per query embedding on standard CPU.

2. **Vector Store Manager (`vector_store.py`)**:
   - Manages ChromaDB collections with cosine distance space.
   - Supports metadata filtering via `where={"doc_id": ...}` or `where={"doc_name": ...}` for document-scoped chat.
   - Includes graceful fallback from persistent storage to in-memory collection in environments with Rust PyO3 binding constraints.

---

## Module Files

- `embedder.py`: High-performance local sentence transformer wrapper.
- `vector_store.py`: ChromaDB collection initialization, indexing, and vector query manager.
