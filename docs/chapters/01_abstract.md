# Chapter 1 — Abstract

## 1.1 Abstract

The proliferation of AI language models has opened new opportunities for automating
knowledge-intensive, creative tasks that traditionally required significant manual
effort. One such task is the creation of professional presentation slides — a
time-consuming process that demands both domain expertise and design sensibility.

This project presents **AI PPT Generator**, a web-based Python application that
bridges large language model (LLM) inference and automated PowerPoint generation to
produce editable, professionally formatted `.pptx` files directly from a plain-text
topic description. The system is built using **Streamlit** for the browser interface,
the **Groq AI SDK** for LLM inference, and **python-pptx** for programmatic
PowerPoint authoring.

The application accepts a user-defined topic, presentation style, language,
target audience, theme, and content depth as input. It constructs a structured
prompt, submits it to the Groq inference API, and parses the returned JSON into a
validated **Pydantic** data model. The validated schema drives a modular layout
rendering engine that maps each slide to one of **13 specialized layout types**
(title, agenda, bullet list, two-column, statistics/KPI, process flow, table, chart,
section header, conclusion, references, image-text, and ending). Seven professionally
designed **colour themes** — including Blue Modern, Dark Elegance, Emerald Green,
Royal Purple, Sunset Warmth, Crimson Slate, and Light Minimal — are applied through
a dedicated theme management subsystem.

The project includes a robust JSON repair pipeline to handle malformed LLM outputs,
a dynamic model discovery mechanism with automatic fallback on 404 errors, a
slide-by-slide in-browser editor, JSON export/import for round-trip editing, and an
offline sample mode for demonstrations without an API key. A suite of **18 automated
pytest tests** validates the core subsystems, covering content validation, PPTX
generation, AI service behavior, and utility functions, with all tests passing on the
target platform.

The result is a fully working, modular, extensible, and academically transparent
system that eliminates the manual overhead of slide preparation while producing
output that is editable in standard office software, in contrast to existing AI tools
that produce static, non-editable PDF or image artefacts.

**Keywords**: Large Language Model, Groq AI, PowerPoint Automation, python-pptx,
Streamlit, Presentation Generation, Content Validation, Pydantic, JSON Schema

