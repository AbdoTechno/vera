# VERA — Evidence-Grounded Clinical Decision Support System

> **Hackathon Project Context & Research Brief**

>
> **IMPORTANT — Latest Official Challenge Brief**
>
> The latest challenge brief supplied by the team is the highest-priority event specification in this document. Where it conflicts with older copied event material, use the latest brief for:
> - team size: **2–4 members**
> - final presentation: **15–30 minutes per team**
> - scope: **1–2 official guideline PDFs**
> - judging: **30 Retrieval + 25 Grounding/Citations + 15 Architecture + 15 Evaluation + 10 Clinical Safety + 5 UX/Live Demo**
> - the four required layers and the specific Day 1–5 deliverables
>
>
> This README is the context document for AI agents, researchers, developers, and team members working on VERA. It explains the hackathon, the official challenge requirements, the proposed clinical domain, the RAG architecture, judging criteria, evaluation strategy, safety requirements, and the expected project outputs.

---

## 1. Project Identity

### Project Name

**VERA**

### Proposed Meaning

**Verified Evidence Retrieval Assistant**

### Project Category

**Clinical Decision Support (CDS) + Retrieval-Augmented Generation (RAG)**

### Main Goal

VERA is an evidence-grounded clinical decision-support prototype designed to help healthcare professionals retrieve, understand, and verify information from approved clinical guidelines.

VERA is **not intended to diagnose patients, replace physicians, or act as an autonomous medical decision-maker**.

The core principle is:

> **Fluent Answer ≠ Safe Answer**

Every clinical answer should be grounded in approved evidence and traceable to its source.

---

# 2.1 Latest Official Challenge Brief — AI Clinical Decision Support Lite

This section is based directly on the latest challenge information supplied by the team and should be treated as the primary event specification.

## Executive Overview

The hackathon is a specialized **5-day technical competition**.

The goal is to design and implement a **Retrieval-Augmented Generation (RAG)** system that delivers evidence-based clinical recommendations grounded strictly in official medical guidelines.

## Core Challenge

LLMs can generate fluent medical advice but may hallucinate or produce unsupported claims.

The team must build a system that:

- Ingests official medical PDFs.
- Retrieves only relevant, high-quality evidence.
- Generates responses strictly from retrieved evidence.
- Provides transparent citations:
  - Document Name
  - Section
  - Page

## Required 4-Layer Architecture

### 1. Document Ingestion Layer

- PDF parsing
- Section-aware chunking
- Vector indexing

### 2. Retrieval Layer

- Semantic search optimization
- Transparent chunk display

### 3. Generation Layer

- Strict grounding prompts
- Structured citation formatting

### 4. Safety Layer

- Hallucination / unsupported-claim detection
- Refusal mechanisms for out-of-scope or insufficient-evidence queries

## Scope Constraint

On Day 1, teams are expected to select **1–2 official guideline PDFs**.

The selected documents must be:

- Publicly accessible
- Legally usable for the project
- Appropriate for the selected clinical scope
- Approved by mentors for legal and technical suitability

This is important: VERA should **not** begin by ingesting hundreds of papers.

The hackathon is specifically optimized around a **small, controlled, high-quality guideline corpus**.

## Latest 5-Day Deliverables

### Day 1 — Research, Scope & Document Ingestion

Objective:

> Define the clinical scope and build a reliable ingestion pipeline.

Tasks:

- Select 1–2 official guideline PDFs.
- Verify public accessibility and legal usability.
- Parse PDF content; structured extraction is preferred.
- Implement section-aware chunking.
- Generate embeddings.
- Index chunks in a vector database.
- Store document name, section, and page metadata.

Expected outcome:

> **Fully indexed guideline corpus and retrieval-ready vector database.**

### Day 2 — Retrieval Optimization

Objective:

> Achieve high-precision evidence retrieval.

Tasks:

- Implement Top-K semantic search.
- Tune chunk size and overlap.
- Tune K.
- Evaluate embedding model choice.
- Log retrieval scores.
- Display retrieved chunks before generation.

Expected outcome:

> **Stable and explainable retrieval layer with evaluation logs.**

### Day 3 — Grounded Generation & Citation

Objective:

> Generate structured answers strictly grounded in retrieved evidence.

Tasks:

- Design strict grounding prompts.
- Prohibit external knowledge use.
- Format citations using document name, section, and page number.
- Structure the response around recommendation, excerpt/evidence, and citation.
- Implement refusal behavior when context is insufficient.

Expected outcome:

> **Fully functional RAG pipeline with proper citation and refusal mechanism.**

### Day 4 — Safety, Guardrails & Internal Evaluation

Objective:

> Improve reliability and quantify performance.

Tasks:

- Add retrieval confidence threshold.
- Implement unsupported-claim detection.
- Test in-scope, ambiguous, and out-of-domain queries.
- Measure Retrieval Precision@K.
- Measure citation accuracy.
- Evaluate faithfulness to retrieved text.

Expected outcome:

> **Evaluated and stress-tested system with prepared safety demonstrations.**

### Day 5 — Final Presentation & Judge Evaluation

Objective:

> Demonstrate transparency, safety, and system rigor.

Final presentation:

**15–30 minutes per team**

Required components:

- Problem & Scope
- Clinical topic
- Guideline source
- System Architecture
- Ingestion
- Retrieval
- Generation
- Safety
- Live demonstration with a judge-provided query
- Display retrieved chunks
- Generated structured response with citation
- Refusal case demonstration

## Selection / Review Stages

The latest brief defines four important stages:

1. **Initial Screening**
   - Technical skills, especially Python/APIs
   - Team composition
   - Team size: 2–4 members

2. **Scope Approval — Day 1**
   - Mentors review selected clinical guidelines
   - Legal suitability
   - Technical suitability

3. **Technical Milestone — Day 3**
   - Functional RAG pipeline
   - Citation accuracy

4. **Final Evaluation — Day 5**
   - Live presentation
   - Judge-provided queries
   - Stress-testing by judges

## Staff Roles

### Mentor

- Provides technical guidance on RAG logic.
- Keeps teams within the medical scope.

### Trainer

- Conducts workshops on:
  - Prompt engineering
  - Embeddings
  - Medical AI safety

### Operations

- Handles schedule and logistics.
- Coordinates communication between teams and judges.

# 2. Hackathon Context

The project is being developed for the **AI Hackathon 2026**, organized in partnership by:

- CREATIVA Innovation Hubs
- ITIDA
- TIEC
- Orange Digital Center (ODC)
- INSTANT Software Solutions

The hackathon is designed to bridge the gap between academic AI knowledge and real-world AI applications.

### Format

**Hybrid**

### Official Sessions

| Day | Date | Format | Main Focus | Expected Output |
|---|---|---|---|---|
| Day 1 | Aug 16, 2026 | Offline | Research, Scope, Ingestion, Team Formation | Searchable Vector DB with Metadata |
| Day 2 | Aug 17, 2026 | Offline | Retrieval Optimization | Measured Baseline + Precision@K |
| Day 3 | Aug 18, 2026 | Online | Grounded Generation + Citation | Structured, Cited RAG Pipeline |
| Day 4 | Aug 19, 2026 | Online | Safety, Guardrails + Internal Evaluation | Guardrail Workflow + Benchmark Dashboard |
| Day 5 | Aug 20, 2026 | Offline | Final Presentation + Judge Evaluation | Frozen Prototype + Live Demo + Pitch |

The provided official Terms also state that the official hackathon build period is **96 hours** and that the core code, architecture, and solution should be built during the official period.

---

# 3. What the Hackathon Is

This is primarily a **hands-on hackathon**, not a traditional course.

The organizers provide:

- Challenge direction
- Sessions and explanations
- Mentors / instructors
- Technical guidance
- Evaluation expectations
- Support during development

The participating teams are responsible for:

- Choosing the clinical scope
- Building the ingestion pipeline
- Preparing the knowledge base
- Building the retrieval system
- Testing retrieval
- Building grounded generation
- Implementing citations
- Adding safety mechanisms
- Evaluating the system
- Building the user interface
- Integrating the components
- Preparing the live demo
- Presenting the final project

Mentors and instructors are not supposed to write code for teams or build the project on their behalf.

---

# 4. Core Clinical Problem

Generic LLMs can generate fluent answers from their parametric knowledge.

In a clinical context, this creates a major risk:

- The answer may sound confident.
- The answer may be medically plausible.
- The answer may still be unsupported by the approved evidence.
- The answer may contain hallucinated or outdated recommendations.

Therefore, VERA follows a different principle:

```text
Clinical Question
       ↓
Approved Evidence Retrieval
       ↓
Relevant Guideline Evidence
       ↓
Grounded Generation
       ↓
Citation
       ↓
Safety Verification
       ↓
Clinical Evidence Answer
```

The LLM should act primarily as an **evidence synthesizer**, not as a diagnostician.

---

# 5. Proposed Clinical Domain

## Current Candidate: Spinal Muscular Atrophy (SMA)

The team is currently considering:

**Spinal Muscular Atrophy (SMA) — ضمور العضلات الشوكي**

This is a candidate clinical domain, not yet an immutable final scope.

### Proposed Target User

Primary target:

**Pediatric Neurologist / Neuromuscular Specialist**

Potential secondary users:

- Neurologists
- Multidisciplinary SMA care teams
- Other clinicians involved in SMA management

### Proposed Scope

A focused VERA version could target:

**SMA Diagnosis & Treatment Decision Support**

Potential subdomains:

1. Diagnosis
2. Genetic confirmation
3. Treatment initiation
4. Treatment selection
5. Treatment monitoring
6. Treatment switching / sequencing
7. Safety
8. Supportive multidisciplinary care

The scope must remain narrow enough to build and evaluate reliably during the hackathon.

---

# 6. Important Scope Rule

Do **not** turn VERA into:

> "An AI doctor for all diseases."

Do **not** attempt to cover every neuromuscular disease.

Do **not** allow the knowledge base to become an uncontrolled collection of random medical papers.

The project should have:

- One clearly defined clinical domain
- A controlled knowledge base
- Approved evidence sources
- Clear inclusion/exclusion criteria
- A defined target user
- A defined set of clinical questions
- Explicit out-of-scope behavior

If the team later changes the clinical domain, this README should be updated.

---

# 7. Official Medical Data Constraint

The hackathon terms state that the challenge focuses on **Clinical Decision Support**.

Solutions must retrieve and generate answers based on:

> **Provided or approved official medical guidelines**

Examples mentioned in the hackathon materials include:

- WHO
- NICE
- CDC
- USPSTF

For the final SMA implementation, the team must identify the most authoritative and relevant SMA-specific guidelines, consensus documents, and approved evidence sources.

### Important

Scientific papers are not automatically equivalent to clinical guidelines.

The knowledge hierarchy should distinguish between:

### Tier 1 — Authoritative Clinical Guidelines

Primary source for clinical recommendations.

### Tier 2 — Consensus Statements / High-quality Reviews

Supporting evidence and interpretation.

### Tier 3 — High-quality Primary Studies

Clinical evidence supporting specific findings.

### Tier 4 — Background Literature

Useful for research and context but not necessarily suitable as the direct source of clinical recommendations.

---

# 8. VERA Core Architecture

The official hackathon agenda describes a modular, layered pipeline.

The target architecture is:

```text
                ┌──────────────────────┐
                │ Approved Guidelines  │
                │ / Clinical Evidence  │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Data Ingestion       │
                │ PDF Extraction       │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ PDF Cleaning         │
                │ Headers / Footers    │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Section-Aware        │
                │ Chunking             │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Metadata             │
                │ page / section / id  │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Embeddings           │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Vector Database      │
                └──────────┬───────────┘
                           ↓
User Question → Query Processing
                           ↓
                ┌──────────────────────┐
                │ Retrieval            │
                │ Semantic / BM25      │
                │ / Hybrid             │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Reranking            │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Evidence Panel       │
                │ chunks + scores      │
                │ metadata              │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Grounded Generation  │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Citation / Evidence  │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Safety / Guardrails  │
                │ Claim Verification   │
                └──────────┬───────────┘
                           ↓
                ┌──────────────────────┐
                │ Final Clinical       │
                │ Evidence Answer      │
                └──────────────────────┘
```

Each layer should be independently testable where practical.

---

# 9. Day 1 — Research, Scope & Ingestion

## Main Goal

Build the foundation of the knowledge base.

### Activities

- Form / finalize team
- Research the clinical problem
- Define the exact clinical scope
- Identify authoritative sources
- Collect approved documents
- Extract PDF text
- Clean extracted text
- Preserve page numbers
- Remove extraction artifacts
- Perform section-aware chunking
- Attach metadata
- Generate embeddings
- Store vectors

### Metadata

Each vector entry should contain metadata similar to:

```json
{
  "document_name": "...",
  "page_number": 15,
  "section_title": "...",
  "chunk_id": "...",
  "source_url": "..."
}
```

### Expected Day 1 Output

> **Searchable Vector DB with Metadata**

---

# 10. Day 2 — Retrieval Optimization

The goal is not simply to make retrieval work.

The goal is to **measure and improve retrieval quality**.

## Experiments

### Top-K

Compare:

- Top-3
- Top-5
- Top-10

### Chunk Size

The official agenda suggests experiments such as:

- 400–600 tokens
- 700–900 tokens

### Retrieval Methods

Compare:

- Semantic Search
- Keyword Search / BM25
- Hybrid Search
- Reranking

### Evidence Panel

The UI should ideally expose:

- Retrieved chunks
- Relevance scores
- Document
- Page
- Section
- Metadata

This makes retrieval auditable.

---

# 11. Precision@K

Precision@K is a core retrieval metric.

Example:

If the system retrieves 5 chunks and 3 are relevant:

```text
Precision@5 = 3 / 5 = 0.60
             = 60%
```

The hackathon specifically mentions reporting:

- Precision@3
- Precision@5

The evaluation should use a labeled clinical question set.

---

# 12. Clinical Evaluation Dataset

The project should build a structured evaluation dataset.

Target:

**20–30 structured clinical test cases**

The hackathon materials mention:

- Direct questions
- Multi-chunk questions
- Ambiguous questions
- Out-of-scope questions

The team should expand this into categories such as:

1. Direct retrieval
2. Multi-chunk
3. Multi-document
4. Comparative
5. Ambiguous
6. Safety-sensitive
7. Out-of-scope
8. Citation verification

Each evaluation question should have:

```text
Question
Expected Topic
Expected Evidence
Relevant Document
Expected Page / Section
Question Type
Difficulty
```

Do not invent expected clinical answers without supporting evidence.

---

# 13. Day 3 — Grounded Generation & Citation

The retrieval output becomes the context for generation.

Target pipeline:

```text
Question
   ↓
Retriever
   ↓
Relevant Evidence
   ↓
Reranker
   ↓
Selected Evidence
   ↓
LLM
   ↓
Grounded Answer
   ↓
Citation
```

The LLM must not freely answer from general knowledge.

### Grounding Rule

The retrieved guideline text is treated as the primary source of truth for the answer.

If sufficient evidence is not retrieved:

```text
Insufficient evidence was found
in the approved knowledge base.
```

The system should prefer uncertainty/refusal over unsupported generation.

---

# 14. Citation Requirements

Every clinically meaningful answer should be traceable.

Possible citation information:

- Guideline name
- Document name
- Page
- Section
- Source URL
- Retrieved evidence chunk

Example:

```text
Answer
   ↓
Supporting Evidence
   ↓
NICE / SMA Guideline
   ↓
Section
   ↓
Page
   ↓
Source
```

The exact source hierarchy will depend on the final SMA evidence review.

---

# 15. Evidence Panel

A major UX concept from the official agenda is the **Evidence Panel**.

The Evidence Panel should make the RAG process transparent.

Potential content:

```text
Retrieved Evidence

1. Guideline A
   Section: Treatment Initiation
   Page: 24
   Score: 0.87

2. Guideline A
   Section: Patient Selection
   Page: 26
   Score: 0.82

3. Guideline B
   Section: Monitoring
   Page: 14
   Score: 0.78
```

The user should be able to understand where the answer came from.

---

# 16. Day 4 — Safety, Guardrails & Evaluation

Safety is a core part of the project.

## Input Risk Classification

Questions may be classified as:

### Allowed

Evidence-based clinical guideline questions.

### Needs Caution

Patient-specific scenarios or questions that require careful handling.

### Refuse / Redirect

Examples include:

- Emergencies
- Out-of-scope questions
- Questions requiring unsupported personalized decisions
- Requests for information absent from the approved knowledge base

---

# 17. Retrieval Confidence Threshold

If retrieval confidence is below a defined threshold:

```text
Low Evidence Confidence
        ↓
Block / downgrade generation
        ↓
Return insufficient-evidence response
```

The system should never use a low-confidence retrieval result as an excuse to generate a confident medical answer.

---

# 18. Unsupported Claim Detection

Generated answers should be checked against the retrieved evidence.

Concept:

```text
Generated Answer
       ↓
Extract Claims
       ↓
Compare Claims with Evidence
       ↓
Unsupported Claim?
       ↓
Flag / Reject / Regenerate
```

Goal:

> Minimize unsupported clinical claims.

---

# 19. Safety Philosophy

VERA is an educational prototype.

It is not a medical device.

It does not replace:

- Physicians
- Clinical judgment
- Emergency services
- Institutional protocols
- Patient-specific medical evaluation

The system should clearly communicate its limitations.

A clinical disclaimer should be visible in the UX where appropriate.

---

# 20. Day 5 — Final Demo & Judging

The final day is:

**Offline — Final Presentation & Judge Evaluation**

Expected state:

> **Frozen Prototype**

The project should be stable enough for a live demonstration.

The official agenda describes:

> Three predefined query scenarios, executed live in front of the judges.

The team should prepare at least three carefully tested demo scenarios.

### Suggested Demo Structure

#### Scenario 1 — Direct Evidence Question

A straightforward clinical question with a strong guideline answer.

Show:

- Answer
- Retrieved evidence
- Citation

#### Scenario 2 — Complex / Multi-chunk Question

A question requiring multiple pieces of evidence.

Show:

- Retrieval
- Evidence aggregation
- Grounded synthesis
- Multiple citations

#### Scenario 3 — Safety / Out-of-scope Question

A question with insufficient evidence or unsafe scope.

Show:

- Guardrail
- Refusal / redirect
- Reason
- Evidence status

---

# 21. Official Judging Criteria

According to the latest supplied **AI Clinical Decision Support Lite** challenge brief, the project is evaluated out of **100 points**:

| Category | Weight | What Judges Look For |
|---|---:|---|
| Retrieval Precision | **30 pts** | Accuracy and relevance of surfaced evidence |
| Answer Grounding & Citations | **25 pts** | No hallucinations, precise source tracking, faithfulness to retrieved evidence |
| Architecture Design | **15 pts** | Technical clarity, modularity, clean separation of layers |
| Evaluation Metrics | **15 pts** | Quality of internal testing methodology and quantitative evaluation |
| Clinical Safety | **10 pts** | Correct handling of insufficient evidence and refusal behavior |
| UX & Live Demo | **5 pts** | Usability and performance under pressure |

## Strategic Interpretation

The highest-value areas are:

### 55% Combined

**Retrieval Precision + Answer Grounding & Citations**

Therefore:

> A beautiful UI is not the core of the competition.

The project must prove that it retrieves the **right evidence** and generates an answer that remains **faithful to that evidence**.

The next major priority is **Evaluation (15%)**, because the team must prove performance rather than simply claim that the RAG works.

# 22. What Makes VERA Different From a Generic Medical Chatbot?

A generic chatbot might do:

```text
Question
 ↓
LLM
 ↓
Answer
```

VERA should do:

```text
Question
 ↓
Risk Classification
 ↓
Approved Knowledge Base
 ↓
Retrieval
 ↓
Reranking
 ↓
Evidence
 ↓
Grounded Generation
 ↓
Claim Verification
 ↓
Citation
 ↓
Safe Answer
```

The differentiation is:

- Controlled evidence
- Transparent retrieval
- Page/section citations
- Retrieval metrics
- Safety thresholds
- Refusal logic
- Unsupported claim detection
- Evaluation benchmark
- Auditable architecture

---

# 23. Proposed VERA User Experience

VERA should not look like a generic ChatGPT clone.

The UI should emphasize **evidence and trust**.

## Main Screen

Possible components:

- Clinical question input
- Scope indicator
- Evidence status
- Answer
- Confidence indicator
- Sources
- Evidence panel
- Clinical disclaimer

### Example

```text
VERA
Verified Evidence Retrieval Assistant

Clinical Scope:
Spinal Muscular Atrophy

Ask a clinical evidence question...

----------------------------------

ANSWER

[Grounded clinical response]

Evidence Confidence: High

----------------------------------

SUPPORTING EVIDENCE

Guideline A
Section: Treatment
Page: 24

Guideline B
Section: Monitoring
Page: 31

----------------------------------

CLINICAL SAFETY

This answer is grounded in the approved
knowledge base and does not replace
clinical judgment.
```

---

# 24. Recommended Technical Responsibilities

The team can divide responsibilities.

### RAG / AI Engineer

- Ingestion
- Chunking
- Embeddings
- Vector DB
- Retrieval
- Hybrid search
- Reranking
- Generation
- Evaluation

### Backend Engineer

- API
- RAG service
- Authentication if needed
- Request/response schemas
- Integration

### Flutter Developer

- User interface
- Evidence panel
- Chat / query flow
- Citations
- Confidence UI
- Safety messages
- Backend integration

### Data / Evaluation

- Clinical documents
- Metadata
- Evaluation questions
- Relevance labels
- Precision@K
- Failure analysis
- Benchmark dashboard

A person can have multiple responsibilities.

---

# 25. Technology Direction

The team plans to use **Flutter** for the application interface.

The RAG/backend stack is still to be finalized.

Possible components may include:

- Python
- FastAPI
- Embedding model
- Vector database
- LLM API
- Retrieval library
- Reranking model
- Evaluation framework

The final choices should be based on:

- Hackathon constraints
- Cost
- Reliability
- Speed
- Ease of integration
- Explainability
- Ability to evaluate
- Team expertise

The official terms explicitly allow third-party APIs such as OpenAI, Pinecone, and LangChain, subject to their respective terms. Teams are responsible for any paid API costs.

---

# 26. Important Hackathon Rules

According to the supplied Terms and Conditions:

## Team

- **2–4 members** according to the latest supplied challenge brief.
- Individual participation is not allowed unless explicitly approved.
- Registration information must be accurate.

## Original Work

The core code, architecture, and solution must be built during the official 96-hour hackathon period.

Pre-existing code or boilerplates may only be used if:

- They are open-source
- They are publicly available
- They are properly declared

## AI Tools / APIs

Third-party AI APIs and tools are allowed if their terms are respected.

Examples mentioned:

- OpenAI
- Pinecone
- LangChain

Paid API costs are the responsibility of the team.

## Medical Safety

The solution must be based on approved medical guidelines.

No malicious or intentionally hallucinatory medical advice.

## Intellectual Property

Teams retain ownership of the IP they create.

The organizers receive a non-exclusive, royalty-free, worldwide license to use:

- Team name
- Project name
- Presentations
- Demo videos
- Project details

for promotional, marketing, and reporting purposes.

---

# 27. What We Should NOT Build

Avoid turning VERA into:

- A general ChatGPT clone
- A diagnosis engine
- A disease prediction model without evidence
- A generic medical search engine
- A system that answers from unrestricted web knowledge
- A system that hides its sources
- A system that confidently answers when evidence is missing
- A system that tries to cover all medical specialties

The core product is:

> **Evidence-grounded clinical decision support.**

---

# 27.1 Officially Suggested Data Sources

The latest supplied challenge brief recommends the following sources as potential starting points.

These are **candidate sources**. The team must still confirm that the selected document is appropriate for the chosen clinical scope and receives Day 1 scope approval.

### USPSTF Recommendations

**U.S. Preventive Services Task Force**

Useful for:

- Screening
- Counseling
- Preventive medications
- Preventive medicine recommendations

A major advantage for RAG is the structured recommendation format and explicit evidence grades.

### NICE Guidance

**National Institute for Health and Care Excellence**

Useful because guidance is generally structured into:

- Recommendations
- Context
- Evidence

This can make section-aware chunking and retrieval easier.

### WHO IRIS

**WHO Institutional Repository for Information Sharing**

Useful for:

- Global health guidance
- Official WHO publications
- Public clinical materials
- Structured guideline PDFs

### ESC Clinical Practice Guidelines

**European Society of Cardiology**

Useful for cardiovascular clinical guidance and structured recommendation/evidence systems.

### MAGICapp

**Making GRADE the Irresistible Choice**

Useful for evidence-based guideline content and GRADE-oriented recommendations. Some guideline outputs may be available as structured PDF exports.

## Source Selection Rule

Do not choose a source merely because it is easy to parse.

The selected guideline should be judged on:

1. Clinical relevance
2. Authority
3. Recency
4. Public accessibility
5. Legal usability
6. Structure
7. Retrieval suitability
8. Ability to answer the benchmark questions
9. Mentor approval

# 28. Research Phase

Before locking the final SMA scope, conduct a recent literature review.

Priority:

- 2026
- 2025
- 2024

Then older foundational/high-impact evidence where necessary.

Search:

- PubMed
- PubMed Central
- Europe PMC
- Google Scholar
- Crossref
- Semantic Scholar
- Major medical journals
- Professional societies
- Official guideline organizations

Research should focus on:

- SMA diagnosis
- SMN1
- SMN2 copy number
- newborn screening
- disease-modifying therapies
- nusinersen
- risdiplam
- onasemnogene abeparvovec
- treatment initiation
- treatment switching
- treatment monitoring
- motor outcomes
- respiratory care
- nutrition
- orthopedic care
- safety
- long-term outcomes
- pediatric SMA
- adult SMA
- treatment sequencing

Do not fabricate references.

Every important source must be verifiable.

---

# 29. Research Output We Need

The research phase should first identify the **1–2 official guideline PDFs** that can serve as the controlled VERA corpus. Supporting papers may be used to understand the field and design evaluation, but the hackathon's core RAG corpus should remain focused on the approved guideline documents.

The literature research should answer:

1. Is SMA a strong clinical domain for VERA?
2. What exact SMA scope should VERA target?
3. Who is the primary user?
4. Which official guidelines should form the primary knowledge base?
5. Which scientific papers should be supporting evidence?
6. What questions should VERA answer?
7. What questions should VERA refuse?
8. What 20–30 questions should form the benchmark?
9. What evidence conflicts exist?
10. What knowledge gaps exist?
11. What retrieval challenges are likely?
12. What safety risks must be addressed?

---

# 30. Initial Evaluation Strategy

The evaluation should contain at least 20 structured questions.

Preferably 20–30.

Example distribution:

```text
5 Direct Questions
5 Multi-chunk Questions
3 Multi-document Questions
3 Comparative Questions
3 Ambiguous Questions
3 Safety / Out-of-scope Questions
```

This distribution can change based on the final clinical scope.

---

# 31. Metrics

At minimum, the project should report at least two quantitative metrics because the judging rubric explicitly rewards quantitative evaluation.

Recommended metrics:

### Retrieval

- Precision@3
- Precision@5
- Recall@K where feasible

### Grounding

- Citation accuracy
- Claim-to-evidence support rate
- Unsupported claim rate

### Safety

- Safe refusal rate
- Out-of-scope detection rate
- Unsafe answer rate

### Overall

- Question-level success rate
- Failure categories

The exact final metrics should be selected based on what can be measured reliably during the hackathon.

---

# 32. Failure Analysis

A strong project should not hide failures.

For every important failure, classify the cause:

```text
Wrong Chunk
      ↓
Retrieval Failure
```

```text
Correct Chunk
      ↓
Generation Failure
```

```text
Correct Answer
      ↓
Citation Failure
```

```text
Low Evidence
      ↓
Safety Failure
```

Examples of failure causes:

- Poor chunk boundaries
- Wrong chunk size
- Missing metadata
- Poor embeddings
- Incorrect Top-K
- Semantic search weakness
- Keyword search weakness
- Reranking error
- Prompt failure
- Unsupported generation
- Citation mismatch
- Missing guideline evidence

This analysis can become a major part of the final pitch.

---

# 33. Final Demo Story

The final pitch should tell a simple story:

### Problem

Clinical information is distributed across long guidelines, and generic LLMs can produce fluent but unsupported answers.

### Solution

VERA retrieves relevant approved evidence, synthesizes it, verifies grounding, and exposes citations.

### Architecture

Show the complete RAG pipeline.

### Evidence

Show retrieved chunks and metadata.

### Evaluation

Show Precision@3 / Precision@5 and other measured metrics.

### Safety

Show an out-of-scope or insufficient-evidence query.

### Result

Demonstrate that VERA is not simply answering questions.

It is answering **from evidence**.

---

# 34. Project Success Criteria

VERA should be considered successful if it can:

- Retrieve relevant evidence reliably
- Preserve source metadata
- Produce grounded answers
- Cite page and section information
- Refuse unsupported questions
- Detect low retrieval confidence
- Reduce unsupported claims
- Demonstrate measurable retrieval quality
- Explain failures
- Provide a clear and professional UX
- Demonstrate the complete pipeline live

---

# 35. Current Project Status

### Confirmed

- Project name: **VERA**
- Category: **Clinical Decision Support + RAG**
- Hackathon: **AI Hackathon 2026**
- Application UI: **Flutter**
- Core principle: **Evidence-grounded answers**
- Official focus: **4-layer RAG Architecture**
- Evaluation is a major part of judging
- Safety is a major part of judging

### Under Research

- Final clinical domain
- Final SMA scope
- Exact target physician
- Approved guideline set
- Final document hierarchy
- Embedding model
- Vector database
- Reranker
- LLM
- Evaluation dataset

### Current Clinical Candidate

**Spinal Muscular Atrophy (SMA)**

### Current Proposed Target User

**Pediatric Neurologist / Neuromuscular Specialist**

### Current Proposed Scope

**SMA Diagnosis & Treatment Decision Support**

This is not final until the literature review confirms that it is feasible, well-supported, and suitable for the hackathon timeline.

---

# 35.1 AI Agent Priority Rules From the Latest Brief

When an AI agent works on VERA, it should prioritize the following order:

```text
1. Latest supplied hackathon brief
2. Mentor-approved clinical scope
3. 1–2 approved official guideline PDFs
4. Evidence-grounded retrieval
5. Citation accuracy
6. Safety / refusal
7. Quantitative evaluation
8. Architecture quality
9. UX polish
```

If a proposed feature increases visual complexity but does not improve evidence retrieval, grounding, safety, evaluation, or judge-facing transparency, it is a lower priority.

If an AI agent proposes adding many external medical papers directly into the production RAG corpus, it must first check whether that conflicts with the **1–2 official guideline PDF** scope.

# 36. AI Agent Instructions

Any AI agent working on VERA should follow these rules:

1. Understand that VERA is a **Clinical Decision Support prototype**, not a general chatbot.
2. Keep the project scope narrow.
3. Prioritize official clinical guidelines.
4. Never fabricate medical references.
5. Clearly distinguish guidelines, consensus statements, reviews, and primary studies.
6. Prioritize recent evidence.
7. Never invent clinical recommendations.
8. Keep every clinical claim traceable to evidence.
9. Prefer refusal when sufficient evidence is unavailable.
10. Treat citations as a core product feature.
11. Consider Retrieval Quality one of the highest project priorities.
12. Always consider Precision@K and measurable evaluation.
13. Design around the official judging rubric.
14. Do not optimize only for visual appearance.
15. Keep the system modular and auditable.
16. Remember that the target user is a healthcare professional, not a general consumer.
17. Never present VERA as replacing physicians.
18. Do not silently expand the clinical scope.
19. When proposing features, explain how they contribute to Retrieval, Grounding, Architecture, Evaluation, Safety, or UX.
20. When uncertain about medical facts, request or locate authoritative evidence instead of guessing.

---

# 37. One-Sentence Project Definition

> **VERA is an evidence-grounded Clinical Decision Support system that retrieves, synthesizes, verifies, and cites approved clinical guideline evidence to help healthcare professionals make better-informed decisions within a narrowly defined clinical domain.**

---

# 38. Project North Star

The project should always optimize for:

```text
RELEVANT EVIDENCE
       +
TRACEABLE SOURCES
       +
GROUNDED GENERATION
       +
SAFETY
       +
MEASURABLE PERFORMANCE
       =
VERA
```

The ultimate goal is not to make the AI sound intelligent.

The goal is to make the system **trustworthy, evidence-grounded, measurable, and auditable**.
