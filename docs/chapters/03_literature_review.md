# Chapter 3 — Literature Review

## 3.1 Introduction

This chapter surveys existing work and technologies relevant to the AI PPT Generator
project. The review is organised into five thematic areas: LLM-based document
generation, structured output from language models, PowerPoint and Office Open XML
automation, AI presentation generation tools, and Python web frameworks for AI
applications.

---

## 3.2 Large Language Model-Based Document Generation

The use of transformer-based language models for automated document generation has
grown significantly since the introduction of GPT-2 [1] and GPT-3 [2]. These models
demonstrated that large-scale pre-training on diverse text corpora enables zero-shot
and few-shot generation of coherent, contextually relevant long-form text.

Brown et al. [2] showed that GPT-3 can perform complex text generation tasks such
as summarisation, translation, and question answering without task-specific
fine-tuning, establishing the precedent for prompt-driven content generation that
this project exploits.

Zhao et al. [3] provide a comprehensive survey of LLM capabilities, noting that
structured generation — where the model is prompted to produce output conforming to a
predefined schema — is one of the most practically impactful LLM capabilities for
downstream automation.

---

## 3.3 Structured JSON Output from Language Models

A key challenge in LLM-to-application integration is ensuring that the model
produces output that conforms to a machine-readable schema. White et al. [4]
demonstrated that carefully engineered prompts can dramatically increase the
structural reliability of LLM outputs for downstream tasks.

Wei et al. [5] introduced Chain-of-Thought prompting, which improves the reasoning
quality of LLM responses and has been shown to produce more consistent structured
outputs. This project incorporates CoT-style prompt instructions that ask the model
to reason through content structure before producing the final JSON.

The use of Pydantic for schema validation of LLM outputs is documented by the
LangChain project [6], which popularised the pattern of `model.model_validate(dict)`
as a post-processing step for LLM responses. This project directly implements
this pattern in `src/content_validator.py`.

---

## 3.4 PowerPoint and Office Open XML Automation

The Office Open XML (OOXML) standard [7] defines the XML-based file format used by
Microsoft PowerPoint 2007 and later (`*.pptx`). The standard enables programmatic
creation and modification of presentation files without relying on the Microsoft
Office application itself.

The **python-pptx** library [8] provides a high-level Python API over OOXML,
enabling the creation of slides, text frames, shape objects, charts, tables, and
speaker notes. Smith [8] documents the library's support for placeholder management,
custom colour themes, and master slide layouts — all features leveraged extensively
in `src/slide_layouts.py` and `src/pptx_generator.py`.

Existing automation work using python-pptx has typically focused on report
generation [9] and data visualisation embedding; however, integration with AI content
generation for general-purpose slide authoring is a novel contribution of this project.

---

## 3.5 Existing AI Presentation Generation Systems

Several commercial systems address AI-assisted presentation generation:

| System | Output Format | Editable PPTX | Open Source | Offline Mode |
|---|---|---|---|---|
| Gamma [10] | Proprietary web | No | No | No |
| Beautiful.ai | Proprietary web | No | No | No |
| Canva AI | PNG/PDF export | No | No | No |
| SlidesAI.io | Google Slides | Partial | No | No |
| **AI PPT Generator** (this work) | Native `.pptx` | **Yes** | **Yes** | **Yes** |

None of the surveyed commercial systems produce native, fully editable `.pptx` files
without proprietary lock-in, offline support, or open-source code. This project
uniquely satisfies all three criteria simultaneously.

---

## 3.6 Python Web Frameworks for AI Applications

Streamlit [11] is an open-source Python framework for building data and ML
applications. Streamlit's reactive execution model (re-running the script on each
user interaction) and built-in session state management make it well-suited for
AI-assisted tools where the UI state depends on asynchronous API calls.

Bisong [12] compares Streamlit, Dash, and Gradio for ML application deployment,
concluding that Streamlit offers the best balance of development speed, component
richness, and community support — factors that informed its selection for this
project.

---

## 3.7 Groq LPU Inference

The Groq Language Processing Unit (LPU) [13] is a dedicated AI inference chip
designed for low-latency LLM serving. Groq's cloud API exposes an OpenAI-compatible
`/v1/chat/completions` endpoint, enabling drop-in use of the Groq SDK as a
high-speed alternative to the OpenAI API.

The substantially lower inference latency of the LPU compared to GPU-based
inference (reported as 10–18 tokens/second on GPU vs. 700–800 tokens/second on LPU
for equivalent model sizes) was a primary factor in selecting Groq as the AI
backend, as it enables near-real-time presentation generation for typical slide
counts.

---

## 3.8 Data Validation with Pydantic

Pydantic [14] is a Python library for data parsing and validation using Python type
annotations. Version 2 introduced a Rust-based core for significant performance
improvements and stricter model validation semantics. This project uses Pydantic v2
(`pydantic>=2.0.0`) to define the `PresentationData`, `SlideContent`, and related
models in `src/content_schema.py`, providing automatic type coercion, default
injection, and validation error reporting.

---

## 3.9 Summary

The literature review establishes that:
1. LLMs are capable of producing structured, schema-conforming JSON when
   appropriately prompted.
2. python-pptx provides sufficient API coverage to programmatically author
   professional `.pptx` files without Microsoft Office.
3. Streamlit is an appropriate framework for rapid AI application development.
4. No existing open-source tool combines all three capabilities (LLM generation,
   native PPTX output, interactive web UI) with offline support.

This project fills this gap and is novel in its JSON repair pipeline, 13-layout
rendering engine, and dynamic model fallback mechanism.

---

## 3.10 References

> See [Chapter 10 — References](10_references.md) for the full IEEE-format
> bibliography. In-text citations use bracketed numbers [1]–[14] corresponding to
> the numbered entries in Chapter 10.

