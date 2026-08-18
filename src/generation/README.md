# Grounded Clinical Generation & Citations (`src/generation/`)

This module manages context-grounded response generation, prompt templates, and in-line citation extraction.

---

## Technical Workflow

1. **System Prompts & Grounding Templates (`prompts.py`)**:
   - Strictly instructs the language model to rely exclusively on the provided medical guideline context.
   - Enforces bullet-point recommendations and explicit citation formatting (`[Source: Document#page=X]`).
   - Forbids autonomous ungrounded speculation or dosage invention.

2. **Multi-Provider Client (`generator.py`)**:
   - Supports Google Gemini (`models/gemini-3.1-flash-lite`, `gemini-1.5-flash`) and OpenAI (`gpt-4o-mini`).
   - Supports dynamic per-request API key override (BYOK).
   - Zero-temperature configuration (`temperature=0.0`) for deterministic clinical recommendations.

3. **Citation Parser & Formatter (`citation_formatter.py`)**:
   - Parses generated text to extract structured citation objects with document title, page number, and section.
   - Formats evidence blocks passed into the generation prompt.

---

## Module Files

- `generator.py`: Multi-provider LLM generation client with dynamic key support.
- `prompts.py`: Clinical system prompts and strict context templates in English and Arabic.
- `citation_formatter.py`: In-line citation tag parser, validator, and formatter.
