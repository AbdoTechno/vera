# Hybrid Retrieval & Ranking Subsystem (`src/retrieval/`)

This module implements the hybrid search engine combining dense vector similarity with sparse lexical search.

---

## Retrieval Architecture

1. **Dense Vector Search**:
   - Computes query embeddings via `BAAI/bge-small-en-v1.5` and performs cosine nearest-neighbor search in ChromaDB.
   - Captures semantic intent and clinical concept synonyms.

2. **Sparse Lexical Search (`rank_bm25`)**:
   - Uses Okapi BM25 index over tokenized clinical chunk catalog.
   - Accurately matches specific gene symbols (`SMN1`, `SMN2`), pharmaceutical brand names (`Spinraza`, `Zolgensma`, `Evrysdi`), and diagnostic keywords (`PacBio`, `Nanopore`).

3. **Reciprocal Rank Fusion (RRF)**:
   - Combines dense and sparse ranked candidates using reciprocal rank fusion:
     $$RRF(d) = \sum_{m} \frac{w_m}{60 + r_m(d)}$$
   - Default weights: Dense Weight = 0.6, BM25 Weight = 0.4.

4. **Document Scoping Support**:
   - When a specific `doc_id` or `doc_name` is passed, candidate generation is strictly constrained to chunks originating from that document.

---

## Module Files

- `hybrid_retriever.py`: Hybrid RRF search orchestrator.
- `query_expansion.py`: Medical synonym and Arabic-English terminology expansion dictionary.
- `semantic_search.py`: Standalone dense vector search utility.
