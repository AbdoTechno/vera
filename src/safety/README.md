# Clinical Safety, Confidence Gates & Guardrails (`src/safety/`)

This module enforces clinical safety boundaries, pre-retrieval refusal, confidence verification, and AI document validation.

---

## Safety Architecture

1. **Pre-Retrieval Interceptor (`refusal_engine.py`)**:
   - Inspects queries before vector retrieval to detect acute emergencies (chest pain, severe hemorrhage, loss of consciousness) and non-medical topics (recipes, entertainment, sports).
   - Immediately returns structured refusal responses with 0% confidence without invoking downstream LLMs.

2. **Confidence Gate (`confidence_gate.py`)**:
   - Evaluates the maximum similarity score of retrieved evidence.
   - If the best matching passage similarity is below **0.60**, generation is blocked to prevent clinical hallucination, returning an `Insufficient Evidence Refusal`.

3. **AI Document Ingestion Guardrail (`document_validator.py`)**:
   - Evaluates uploaded PDF documents before chunking and vector indexing.
   - Extracts a smart profile sample (Abstract, middle clinical sections, conclusions ~1500 tokens).
   - Generates a structured decision:
     - `PASS`: Verified institutional medical guideline (proceeds to indexing).
     - `REVIEW`: Medical document with ambiguous clinical scope.
     - `REJECT`: Non-medical or corrupt document (blocked from indexing).

4. **Hallucination & Faithfulness Checker (`hallucination_checker.py`)**:
   - Evaluates sentence-level grounding of the generated response against retrieved evidence chunks.

---

## Module Files

- `refusal_engine.py`: Pre-retrieval emergency and out-of-scope inquiry interceptor.
- `confidence_gate.py`: Retrieval similarity score threshold evaluator.
- `document_validator.py`: AI-powered guideline upload validator.
- `hallucination_checker.py`: Post-generation factual consistency verifier.
