# 📐 VERA System Architecture & Diagrams

توثيق مرئي شامل للبنية المعمارية لمنظومة **VERA (Verified Evidence Retrieval Assistant)**.

---

## 1. البنية المعمارية ذات الـ 4 طبقات (4-Layer CDS Architecture)

```mermaid
flowchart TD
    subgraph L1["Layer 1: Document Ingestion"]
        PDF["Official Clinical PDFs"] --> Extractor["Structured PDF Extractor (pdfplumber)"]
        Extractor --> Chunker["Section-Aware Chunker (w/ Page & Sec Meta)"]
        Chunker --> Embedder["Embedding Engine (BGE-small / OpenAI)"]
        Embedder --> VectorDB[("ChromaDB Vector Store")]
    end

    subgraph L2["Layer 2: Retrieval Engine"]
        Query["Clinical Query"] --> Expander["Medical Synonym Expander"]
        Expander --> Dense["Dense Vector Search"]
        Expander --> BM25["BM25 Keyword Search"]
        Dense & BM25 --> RRF["Reciprocal Rank Fusion (Hybrid Top-K)"]
    end

    subgraph L4_Pre["Layer 4: Pre-Gating Safety"]
        Query --> ScopeCheck{"Scope & Emergency Filter"}
        ScopeCheck -- "Out-of-Scope / Crisis" --> Refusal1["Safe Refusal Response"]
        ScopeCheck -- "In-Scope" --> L2
        RRF --> ConfidenceGate{"Confidence Gate (Similarity >= 0.60)"}
        ConfidenceGate -- "Low Score" --> Refusal2["Insufficient Evidence Refusal"]
    end

    subgraph L3["Layer 3: Generation & Citations"]
        ConfidenceGate -- "Passed" --> PromptGen["Strict Medical Grounding Prompt"]
        PromptGen --> LLM["LLM Synthesis (gpt-4o-mini, temp=0.0)"]
        LLM --> CitationVal["Citation Validator [Doc|Sec|Page]"]
    end

    subgraph L4_Post["Layer 4: Post-Verification"]
        CitationVal --> Hallucination["NLI & Faithfulness Checker"]
        Hallucination --> FinalResp["Evidence-Grounded Recommendation + Citations + Disclaimer"]
    end
```

---

## 2. مسار معالجة الاستعلام السريري (Query Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Clinician as 👨‍⚕️ Clinician / Judge
    participant Safety as 🛡️ Safety & Refusal Gate
    participant Retriever as 🔍 Hybrid Retriever (Dense + BM25)
    participant VectorDB as 🗄️ ChromaDB
    participant Generator as ✍️ Grounded Generator
    participant Checker as ⚖️ Hallucination Checker

    Clinician->>Safety: Clinical Question (e.g. SMA Treatment)
    Safety->>Safety: Check Emergency / Scope boundaries
    Safety->>Retriever: Approved Clinical Query
    Retriever->>VectorDB: Query Embedding + Keyword match
    VectorDB-->>Retriever: Top-K Chunks with Page & Section Meta
    Retriever->>Safety: Evaluate Retrieval Confidence Score
    Safety->>Generator: Pass Verified Evidence Chunks
    Generator->>Generator: Synthesize using Strict Prompt (temp=0.0)
    Generator->>Checker: Generated Answer with [Doc|Sec|Page]
    Checker->>Checker: Verify Citations & Overlap with Context
    Checker-->>Clinician: Structured Output + Direct Excerpts + Verified Citations + Disclaimer
```
