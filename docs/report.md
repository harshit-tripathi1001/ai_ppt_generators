# AI PPT Generator
## Academic Project Report

**Course**: ROSPL — Research Oriented Study Project Laboratory  
**Semester**: VII  
**Project Title**: AI PPT Generator — Automated PowerPoint Presentation Generation using Large Language Models  

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
   - 2.1 Background
   - 2.2 Problem Statement
   - 2.3 Objectives
   - 2.4 Scope
3. [Literature Review](#3-literature-review)
4. [System Requirements](#4-system-requirements)
   - 4.1 Functional Requirements
   - 4.2 Non-Functional Requirements
   - 4.3 Hardware and Software Requirements
5. [System Design](#5-system-design)
   - 5.1 Architectural Layers
   - 5.2 Data Flow
   - 5.3 Slide Layout Design
   - 5.4 Theme Design
   - 5.5 State Management
6. [Implementation](#6-implementation)
   - 6.1 Development Environment
   - 6.2 Module Descriptions
   - 6.3 Prompt Engineering
   - 6.4 Key Implementation Challenges
7. [Testing](#7-testing)
   - 7.1 Test Cases
   - 7.2 Full Test Output
8. [Results and Discussion](#8-results-and-discussion)
9. [Conclusion and Future Scope](#9-conclusion-and-future-scope)
10. [References](#10-references)
- [Appendix A: Abbreviations](#appendix-a--abbreviations)
- [Appendix B: Sample AI JSON Output](#appendix-b--sample-ai-json-output)
- [Appendix C: Full Pytest Output](#appendix-c--full-pytest-output)

---

## 1. Abstract

The proliferation of AI language models has opened new opportunities for automating knowledge-intensive, creative tasks. This project presents **AI PPT Generator**, a web-based Python application that bridges large language model (LLM) inference and automated PowerPoint generation to produce editable, professionally formatted `.pptx` files directly from a plain-text topic description. The system is built using **Streamlit** for the browser interface, the **Groq AI SDK** for LLM inference, and **python-pptx** for programmatic PowerPoint authoring.

The application accepts a user-defined topic, presentation style, language, target audience, theme, and content depth as input. It constructs a structured prompt, submits it to the Groq inference API, and parses the returned JSON into a validated **Pydantic** data model. The validated schema drives a modular layout rendering engine that maps each slide to one of **13 specialized layout types** and applies one of **7 professionally designed colour themes**.

A robust JSON repair pipeline handles malformed LLM outputs; dynamic model discovery with automatic fallback handles model availability; a slide-by-slide in-browser editor and JSON export/import support interactive workflows; and an offline sample mode enables demonstrations without an API key. A suite of **18 automated pytest tests** validates all core subsystems, with all tests passing.

**Keywords**: Large Language Model, Groq AI, PowerPoint Automation, python-pptx, Streamlit, Presentation Generation, Content Validation, Pydantic, JSON Schema

---

## 2. Introduction

### 2.1 Background

Presentations are a ubiquitous medium for knowledge dissemination in academic, corporate, and educational contexts. The emergence of transformer-based large language models (LLMs) capable of producing structured, contextually relevant text on demand has created an opportunity to automate the time-consuming task of slide authoring. However, bridging the gap between unstructured LLM output and a machine-readable, editable PowerPoint file requires a carefully engineered intermediary pipeline.

### 2.2 Problem Statement

Existing AI-assisted presentation tools suffer from the following limitations:

1. **Non-editable outputs**: Generated slides are locked to proprietary vendor formats and cannot be opened in standard office software.
2. **Vendor lock-in**: Users are required to maintain cloud subscriptions; offline use is not possible.
3. **Limited customisation**: Fine-grained control over layout type, content depth, language, audience targeting, and corporate theme is generally absent.
4. **Opaque pipelines**: There is no transparency into the AI-to-slide mapping process.
5. **No programmatic API**: Integration into automated workflows is not supported.

### 2.3 Objectives

1. Accept rich user configuration (20 settings: topic, language, slides, style, theme, font, depth, audience, etc.)
2. Generate structured JSON slide outlines via Groq AI
3. Validate and repair AI output using a multi-stage pipeline backed by Pydantic v2
4. Render editable `.pptx` files with 13 professional layout types
5. Provide an interactive browser UI with slide preview, editor, and download
6. Support offline and automatic model-fallback modes
7. Maintain 18/18 automated test pass rate

### 2.4 Scope

**In scope**: Web-based locally deployable Python application; Groq AI integration; native `.pptx` generation; 11+ languages; 13 layouts; 7 themes; in-browser editing; JSON round-trip; 18 automated tests.

**Out of scope**: PDF export, real-time collaborative editing, user authentication, template import, mobile-native applications.

---

## 3. Literature Review

> See [chapters/03_literature_review.md](chapters/03_literature_review.md) for the full chapter with in-text citations.

**Summary of key works**:

- Brown et al. [2] demonstrated that GPT-3 enables zero-shot structured text generation via prompt engineering — the foundational technique used in this project's AI service.
- Wei et al. [5] showed that Chain-of-Thought prompting improves structural consistency of LLM outputs.
- The python-pptx library [8] provides a Python API over the OOXML standard [7], enabling full programmatic authoring of `.pptx` files.
- Treuille et al. [11] established Streamlit as the leading Python framework for rapid ML application deployment.
- Groq [13] documented the LPU's sub-second inference times, enabling near-real-time presentation generation.

**Comparison with existing tools**:

| Feature | AI PPT Generator | Gamma | Beautiful.ai | SlidesAI |
|---|---|---|---|---|
| Native `.pptx` output | ✅ Yes | ❌ No | ❌ No | ⚠️ Partial |
| Open source | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Offline mode | ✅ Yes | ❌ No | ❌ No | ❌ No |
| 13 layout types | ✅ Yes | ✅ Many | ✅ Many | ⚠️ Limited |

---

## 4. System Requirements

### 4.1 Key Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Accept free-text presentation topic (required, 1–500 chars) |
| FR-02 | Expose 20 configurable settings (topic, language, slides, style, theme, font, etc.) |
| FR-03 | Submit structured prompt to Groq API; retrieve JSON slide outline |
| FR-04 | Parse, extract, and repair malformed JSON from LLM response |
| FR-05 | Enforce user-requested slide count by padding or trimming |
| FR-06 | Generate `.pptx` using python-pptx with selected theme & font |
| FR-07 | Provide download button for the generated `.pptx` |
| FR-08 | Display text-based slide-by-slide preview after generation |
| FR-09 | Allow in-browser editing of each slide's content |
| FR-10 | Function without Groq API key using offline sample mode |
| FR-11 | Auto-retry with next available model on HTTP 404 |
| FR-12 | Export/import presentation as JSON for round-trip editing |

### 4.2 Key Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | End-to-end generation ≤ 30 seconds for 10-slide presentation |
| NFR-02 | Application shall not crash on malformed LLM responses |
| NFR-03 | All settings shall have sensible defaults |
| NFR-04 | Modular architecture; all public functions with docstrings |
| NFR-05 | Runs on Windows/macOS/Linux with Python 3.11+ |
| NFR-06 | API key never logged or displayed in plaintext |
| NFR-07 | Output `.pptx` compatible with PowerPoint 2016+ and LibreOffice 7.0+ |

### 4.3 Software Dependencies

| Package | Version | Purpose |
|---|---|---|
| streamlit | ≥ 1.35.0 | Web UI |
| groq | ≥ 0.9.0 | AI SDK |
| python-pptx | ≥ 1.0.0 | PPTX generation |
| pydantic | ≥ 2.0.0 | Data validation |
| python-dotenv | ≥ 1.0.0 | Environment variables |
| requests | ≥ 2.31.0 | HTTP image fetching |
| Pillow | ≥ 10.0.0 | Image processing |
| pytest | ≥ 8.0.0 | Automated testing |

---

## 5. System Design

> Full architecture diagrams (Mermaid) are in [diagrams/](diagrams/).

### 5.1 Architectural Layers

The system follows an 8-layer modular architecture:

1. **UI Layer** (`app.py`) — Streamlit interface, settings, progress, download
2. **Config Layer** (`config.py`) — Environment variables, constants
3. **AI Service Layer** (`src/ai_service.py`) — Groq API, prompt builder, retry/fallback
4. **Data Model Layer** (`src/content_schema.py`) — Pydantic v2 models
5. **Validation Layer** (`src/content_validator.py`) — JSON repair, normalization, enforcement
6. **PPTX Generation Layer** (`src/pptx_generator.py`, `src/slide_layouts.py`) — 13 layout renderers
7. **Theme Layer** (`src/theme_manager.py`) — 7 colour palettes
8. **Utility Layer** (`src/utils.py`, `src/image_service.py`) — Filename, integrity, images

### 5.2 Pipeline Summary

```
User Settings → Prompt Builder → Groq API → JSON Extractor/Repairer
→ Pydantic Validator → PresentationData → LayoutRenderer (×N slides)
→ python-pptx Presentation → BytesIO → st.download_button
```

### 5.3 Slide Layout Types (13)

| Layout | Purpose |
|---|---|
| `title` | Cover slide |
| `agenda` | Table of contents |
| `bullet_list` | General content (default) |
| `two_column` | Comparison / side-by-side |
| `stats_kpi` | KPI metrics with trend indicators |
| `image_text` | Visual + text (native shape placeholder) |
| `process_flow` | Numbered step-by-step flow |
| `table` | Tabular data |
| `chart` | Bar or line chart |
| `section_header` | Section divider |
| `conclusion` | Key takeaways |
| `references` | Bibliography |
| `ending` | Thank-you / closing slide |

### 5.4 Colour Themes (7)

| Theme | Background | Primary Accent |
|---|---|---|
| Blue Modern | `#1E3A5F` | `#2196F3` |
| Dark Elegance | `#1A1A2E` | `#E94560` |
| Emerald Green | `#1B4332` | `#52B788` |
| Royal Purple | `#2D1B69` | `#7C3AED` |
| Sunset Warmth | `#7C2D12` | `#F97316` |
| Crimson Slate | `#1C1C2E` | `#DC2626` |
| Light Minimal | `#FFFFFF` | `#3B82F6` |

---

## 6. Implementation

> Full module descriptions and algorithm pseudocode in [chapters/06_implementation.md](chapters/06_implementation.md).

### 6.1 Development Environment

| Component | Value |
|---|---|
| OS | Windows 11 |
| Python | 3.15.0 |
| Virtual Environment | `.venv` (pip) |
| Groq Model (primary) | `openai/gpt-oss-120b` |

### 6.2 Key Algorithms

**Algorithm 1: JSON Extraction**
1. Strip whitespace; detect markdown fences → extract content between fences
2. Locate first `{` and last `}` as JSON boundary
3. Return extracted substring; raise `ValueError` if no boundary found

**Algorithm 2: JSON Repair**
1. Remove trailing commas before `}` or `]` using regex substitution
2. Count `{`, `}`, `[`, `]`; append missing closing characters
3. Attempt `json.loads()`; return original on failure (for Pydantic to reject)

**Algorithm 3: Slide Count Enforcement**
```
IF len(slides) > target:
    preserve slides[0] (title) and slides[-1] (ending)
    trim middle slides to (target - 2) elements
ELIF len(slides) < target:
    pad with bullet_list slides until len(slides) == target
```

**Algorithm 4: Model Auto-Fallback**
```
FOR attempt IN range(MAX_RETRIES):
    TRY: call Groq API with current_model
    ON HTTP 404: select next model from priority list; continue
    ON RateLimitError: sleep 2^attempt seconds; continue
    ON AuthenticationError: raise immediately
```

### 6.3 Module File Summary

| File | Lines (approx.) | Responsibility |
|---|---|---|
| `app.py` | ~679 | Streamlit UI, orchestration |
| `config.py` | ~40 | Constants, environment |
| `src/ai_service.py` | ~535 | Groq API, prompt builder |
| `src/content_schema.py` | ~120 | Pydantic models |
| `src/content_validator.py` | ~280 | JSON parsing, repair |
| `src/pptx_generator.py` | ~220 | PPTX orchestration |
| `src/slide_layouts.py` | ~1134 | 13 layout renderers |
| `src/theme_manager.py` | ~130 | 7 themes |
| `src/image_service.py` | ~190 | Wikimedia image API |
| `src/utils.py` | ~110 | Utilities |

---

## 7. Testing

> Full test cases with descriptions in [chapters/07_testing.md](chapters/07_testing.md).

### 7.1 Test Summary

| Module | Tests | Result |
|---|---|---|
| `test_ai_service.py` | 4 | ✅ All pass |
| `test_content_validator.py` | 6 | ✅ All pass |
| `test_pptx_generator.py` | 5 | ✅ All pass |
| `test_utils.py` | 3 | ✅ All pass |
| **Total** | **18** | **✅ 18/18** |

### 7.2 Test Output Summary

```
============================= 18 passed in 5.72s ==============================
```

Full output: [appendices/test_results.md](appendices/test_results.md)

---

## 8. Results and Discussion

### 8.1 Objective Achievement

All 7 objectives achieved. See [chapters/08_results.md](chapters/08_results.md) for full details.

### 8.2 Performance

| Operation | Duration |
|---|---|
| Groq API call (10 slides) | 4–8 seconds |
| PPTX generation (10 slides) | 0.8–1.5 seconds |
| Total end-to-end (10 slides) | 5–10 seconds |
| Total end-to-end (30 slides) | 12–22 seconds |

### 8.3 Identified Limitations

| ID | Limitation |
|---|---|
| L-01 | Generation quality depends on Groq account's available models |
| L-02 | `image_text` layout uses coloured shape placeholder, not real images |
| L-03 | Session state cleared on page refresh (mitigated by JSON export) |
| L-04 | 25–30 slide decks may hit token limits on smaller models |
| L-05 | No user authentication; single-user deployment recommended |
| L-06 | No PDF export |

---

## 9. Conclusion and Future Scope

### 9.1 Conclusion

The AI PPT Generator successfully delivers a fully working, modular, open-source system that automates professional PowerPoint presentation creation from a plain-text topic description. The project's key contributions are:

- A robust multi-stage JSON repair pipeline that handles real-world LLM output inconsistency
- A 13-layout rendering engine producing fully editable `.pptx` files with python-pptx
- A dynamic model discovery and auto-fallback mechanism ensuring API resilience
- Comprehensive test coverage (18/18 tests) validating all subsystems
- An interactive Streamlit UI suitable for both technical and non-technical users

### 9.2 Future Scope

1. PDF export via LibreOffice headless
2. User `.pptx` template import
3. Real image API integration (Google Custom Search)
4. Multi-user authentication and session isolation
5. RAG-based content from uploaded documents
6. Real-time collaborative slide editing
7. Visual slide thumbnail preview
8. Multi-language UI internationalisation
9. Batch REST API for programmatic generation
10. Fine-tuned domain-specific presentation model

---

## 10. References

[1] A. Radford *et al.*, "Language models are unsupervised multitask learners," *OpenAI Blog*, vol. 1, no. 8, Feb. 2019.

[2] T. B. Brown *et al.*, "Language models are few-shot learners," in *Advances in NeurIPS*, vol. 33, 2020, pp. 1877–1901.

[3] W. X. Zhao *et al.*, "A survey of large language models," *arXiv:2303.18223*, 2023.

[4] J. White *et al.*, "A prompt pattern catalog to enhance prompt engineering with ChatGPT," *arXiv:2302.11382*, 2023.

[5] J. Wei *et al.*, "Chain-of-thought prompting elicits reasoning in large language models," in *Advances in NeurIPS*, vol. 35, 2022, pp. 24824–24837.

[6] H. Chase, "LangChain: Building applications with LLMs through composability," GitHub, 2022. Available: https://github.com/langchain-ai/langchain

[7] Ecma International, "Office Open XML File Formats," *Standard ECMA-376*, 5th ed., Dec. 2015.

[8] S. Canny, "python-pptx documentation," 2023. Available: https://python-pptx.readthedocs.io/

[9] C. Lebeaupin and B. Maffulli, "Automated report generation in Python using python-pptx," *PyCon IT*, Firenze, 2022.

[10] Gamma App, "Gamma: AI-powered presentation creation," 2023. Available: https://gamma.app

[11] A. Treuille, T. Teixeira, and A. Kelly, "Streamlit: The fastest way to build and share data apps," *ICML Workshop*, 2020.

[12] E. Bisong, *Building ML and DL Models on Google Cloud Platform*, Apress, 2019, ch. 22.

[13] Groq Inc., "Groq LPU Inference Engine: Technical overview," white paper, 2024. Available: https://groq.com

[14] S. Colvin, "Pydantic v2 documentation," 2023. Available: https://docs.pydantic.dev/

[15] Python Software Foundation, "Python 3.11 documentation," 2023. Available: https://docs.python.org/3.11/

[16] Streamlit Inc., "Session state documentation," 2024. Available: https://docs.streamlit.io

[17] Groq Inc., "Groq API: Chat completions," 2024. Available: https://console.groq.com/docs/text-chat

[18] Wikimedia Foundation, "MediaWiki API documentation," 2024. Available: https://www.mediawiki.org/wiki/API:Main_page

[19] G. van Rossum and P. J. Eby, "PEP 3107 — Function annotations," Python Enhancement Proposal, 2006. Available: https://peps.python.org/pep-3107/

[20] pytest developers, "pytest 9.1.1 documentation," 2024. Available: https://docs.pytest.org/

> **Full IEEE-formatted bibliography**: [chapters/10_references.md](chapters/10_references.md)

---

## Appendix A — Abbreviations

| Abbr. | Meaning |
|---|---|
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| CoT | Chain of Thought |
| DFD | Data Flow Diagram |
| EMU | English Metric Unit |
| ER | Entity Relationship |
| FR | Functional Requirement |
| HTTP | Hypertext Transfer Protocol |
| JSON | JavaScript Object Notation |
| KPI | Key Performance Indicator |
| LLM | Large Language Model |
| LPU | Language Processing Unit |
| MVC | Model-View-Controller |
| NFR | Non-Functional Requirement |
| OOXML | Office Open XML |
| PDF | Portable Document Format |
| PPTX | PowerPoint Open XML Presentation |
| RAG | Retrieval-Augmented Generation |
| REST | Representational State Transfer |
| SDK | Software Development Kit |
| UI | User Interface |
| UML | Unified Modelling Language |

> Full list: [appendices/abbreviations.md](appendices/abbreviations.md)

---

## Appendix B — Sample AI JSON Output

> See [appendices/sample_ai_output.md](appendices/sample_ai_output.md) for a representative 5-slide JSON output with schema field reference.

---

## Appendix C — Full Pytest Output

> See [appendices/test_results.md](appendices/test_results.md) for the complete pytest terminal output.

```
============================= 18 passed in 5.72s ==============================
```

