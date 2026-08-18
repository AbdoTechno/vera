# Interactive Research Notebooks (`notebooks/`)

This directory contains interactive Jupyter notebooks documenting the experimental development and verification of the VERA clinical RAG pipeline.

---

## Notebook Catalog

| Notebook | Focus Area | Description |
| :--- | :--- | :--- |
| `01_ingestion_and_chunking.ipynb` | Ingestion | PDF extraction, section-aware clinical chunking, and metadata serialization. |
| `02_embeddings_and_indexing.ipynb` | Embeddings | Dense vector generation via BGE-Small and ChromaDB indexing. |
| `03_retrieval_optimization.ipynb` | Retrieval | Hybrid retrieval benchmarking (Dense Vector vs BM25 vs RRF). |
| `04_grounded_generation_citations.ipynb` | Generation | Context-constrained generation and in-line citation extraction. |
| `05_safety_guardrails_evaluation.ipynb` | Safety & Evaluation | Confidence gate verification, refusal engine testing, and RAGAS metrics. |
| `06_end_to_end_demo_day5.ipynb` | Live Demonstration | End-to-end clinical workflow execution across supported scenarios. |

---

## Execution

Start the Jupyter environment:

```bash
jupyter notebook
```
