# Chapter 2 — Introduction

## 2.1 Background

Presentations are a ubiquitous medium for knowledge dissemination in academic,
corporate, and educational contexts. Creating a high-quality presentation
typically involves deciding on structure, writing content, choosing a visual theme,
and arranging elements for readability — a process that can take several hours even
for an experienced professional. Despite the wide availability of office suites,
templates, and design tools, the fundamental bottleneck remains the **manual
authoring of slide content**.

The emergence of transformer-based large language models (LLMs) capable of
producing structured, contextually relevant text on demand has created an
opportunity to automate this bottleneck. Modern LLMs can generate well-organised
outlines, speaker notes, comparative data, and narrative text when given a topic and
context. However, bridging the gap between unstructured LLM output and a
machine-readable, editable PowerPoint file requires a carefully engineered
intermediary pipeline.

## 2.2 Problem Statement

Existing AI-assisted presentation tools (e.g., Gamma, Beautiful.ai, Canva AI)
produce visually polished outputs but suffer from the following limitations:

1. **Non-editable outputs**: Generated slides are typically locked to the vendor's
   proprietary format and cannot be opened or modified in standard office software
   (Microsoft PowerPoint, LibreOffice Impress).
2. **Vendor lock-in**: Users are required to maintain subscriptions to cloud
   platforms; offline use is not possible.
3. **Limited customisation**: Fine-grained control over layout type, content depth,
   language, audience targeting, and corporate theme is generally absent.
4. **Opaque pipelines**: There is no transparency into the AI-to-slide mapping
   process, making it difficult to debug or extend the system.
5. **No programmatic API**: Integration into automated workflows or batch processing
   pipelines is not supported.

This project addresses all five limitations by delivering an open-source, locally
deployable, fully editable, and modularly extensible AI presentation generator.

## 2.3 Objectives

The primary objectives of the AI PPT Generator project are:

1. **Accept rich user configuration** — topic, language, number of slides,
   presentation style, theme, font, content depth, target audience, and optional
   structural elements (table of contents, conclusion, references, speaker notes).
2. **Generate structured JSON via Groq AI** — construct a schema-conforming prompt
   and obtain a validated slide outline from an LLM.
3. **Validate and repair AI output** — robustly handle malformed JSON from the LLM
   using a multi-stage parsing and repair pipeline backed by Pydantic schema
   validation.
4. **Render editable PPTX files** — map validated JSON to 13 professional
   PowerPoint layout types using python-pptx, with full theme, font, and colour
   customisation applied.
5. **Provide an interactive browser UI** — expose all settings, a progress display,
   slide-by-slide preview and editing, and a one-click PPTX download through a
   Streamlit web application.
6. **Support offline and fallback modes** — allow the application to function without
   a live Groq API key using a pre-defined sample presentation, and automatically
   switch models when the configured model is unavailable.
7. **Maintain code quality** — achieve comprehensive test coverage with an automated
   pytest suite validating all subsystems.

## 2.4 Scope

The scope of this project is as follows:

**In scope**:
- Web-based Python application deployable locally or on any cloud VM
- Integration with the Groq AI inference API
- Generation of native `.pptx` files compatible with Microsoft PowerPoint 2016+
- Support for multiple languages (English, Hindi, Spanish, French, German, etc.)
- 13 slide layout types and 7 colour themes
- In-browser slide editing and JSON round-trip editing
- 18 automated unit and integration tests

**Out of scope**:
- PDF export
- Real-time collaborative editing
- User authentication and multi-user accounts
- Template import from existing `.pptx` files
- Presentation rendering to HTML or image formats
- Mobile-native applications

## 2.5 Organisation of the Report

The remainder of this report is organised as follows:

| Chapter | Title |
|---|---|
| 3 | Literature Review |
| 4 | System Requirements |
| 5 | System Design |
| 6 | Implementation |
| 7 | Testing |
| 8 | Results and Discussion |
| 9 | Conclusion and Future Scope |
| 10 | References |
| Appendix A | List of Abbreviations |
| Appendix B | Sample AI JSON Output |
| Appendix C | Full Pytest Output |

