# Automated Testing Suite (`tests/`)

This directory contains unit and integration test suites validating the reliability of the VERA platform.

---

## Test Suites

| File | Layer | Validated Functionality |
| :--- | :--- | :--- |
| `test_ingestion.py` | Ingestion | Section-aware chunking boundaries and page-number metadata preservation. |
| `test_retrieval.py` | Retrieval | Query expansion, synonym mapping, and BM25 token matching. |
| `test_generation.py` | Generation | Citation extraction, citation tags `[Document#page=X]`, and formatting. |
| `test_safety.py` | Safety | Emergency interception, out-of-scope refusal, and similarity score gating. |
| `test_telegram.py` | Telegram Integration | HTML card rendering, message paragraph splitting, and webhook handlers. |

---

## Running Tests

Execute all tests:

```bash
pytest -v
```
