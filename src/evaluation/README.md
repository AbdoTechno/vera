# Evaluation & Benchmark Metrics (`src/evaluation/`)

This module provides quantitative and qualitative evaluation suites for evaluating retrieval quality, answer faithfulness, and clinical safety.

---

## Evaluation Metrics

1. **Retrieval Performance**:
   - `Precision@K`: Proportion of top-K retrieved passages relevant to the clinical inquiry.
   - `Recall@K`: Coverage of ground-truth guideline sections.
   - `Mean Reciprocal Rank (MRR)`: Rank position of the primary clinical evidence chunk.

2. **Generation & Grounding Quality**:
   - `Faithfulness (RAGAS framework)`: Ratio of generated statements directly entailed by retrieved evidence.
   - `Answer Relevance`: Semantic alignment between the clinical prompt and generated recommendations.
   - `Citation Accuracy`: Verification of document titles and exact page indices.

---

## Module Files

- `metrics.py`: Statistical precision, recall, and citation verification functions.
- `benchmark_runner.py`: Automated batch evaluation runner across test query suites.
