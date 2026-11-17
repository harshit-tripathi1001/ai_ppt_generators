# Chapter 5 — System Design

## 5.1 Overview

The AI PPT Generator follows a **layered, modular MVC-like architecture** with clear
separation between the user-interface layer, the AI service layer, the data model
layer, and the rendering layer. No database is used; all state is managed
in-memory via Pydantic models and Streamlit's session state during a single user
session.

The high-level system architecture is shown in **Figure 1** (see
[`diagrams/architecture.md`](../diagrams/architecture.md)).

---

## 5.2 Architectural Layers

### Layer 1 — Presentation / UI (`app.py`)
The Streamlit application serves as the entry point and UI controller. It:
- Renders all setting controls and collects user input.
- Orchestrates the generation pipeline by invoking the AI service and PPTX
  generator.
- Displays progress indicators, slide previews, and the download button.
- Manages session state (`st.session_state`) for the generated `PresentationData`
  object and the PPTX binary buffer.

### Layer 2 — Configuration (`config.py`)
A standalone configuration module that:
- Loads environment variables from `.env` using `python-dotenv`.
- Exposes constants for default model name, theme defaults, and path resolution.
- Provides a `try/except` fallback for environments where `python-dotenv` is not
  installed.

### Layer 3 — AI Service (`src/ai_service.py`)
The `GroqAIService` class encapsulates all LLM interactions:
- Builds a structured, schema-aware prompt from user settings.
- Calls the Groq `/v1/chat/completions` endpoint via the official Groq Python SDK.
- Implements retry logic with exponential back-off for rate limit errors.
- Implements automatic model fallback on HTTP 404 responses.
- Generates an offline sample presentation when no API key is configured.

### Layer 4 — Data Model (`src/content_schema.py`)
Pydantic v2 models define the data contract between the AI service and the rendering
layer:
- `PresentationData` — top-level container with metadata and slide list.
- `SlideContent` — per-slide data with layout discriminator and typed optional fields.
- Supporting models: `KpiMetric`, `ColumnData`, `TableData`, `ChartData`,
  `ChartSeries`, `ProcessStep`.

### Layer 5 — Validation (`src/content_validator.py`)
A stateless module of pure functions:
- `parse_and_validate_response()` — orchestrates the full parsing pipeline.
- `_extract_json()` — strips markdown fences and locates JSON boundaries using regex.
- `_repair_json()` — removes trailing commas and rebalances brackets.
- `_normalize_layouts()` — maps layout aliases to the 13 canonical layout names.
- `_enforce_slide_count()` — pads or trims the slide list to the target count.

### Layer 6 — PPTX Generation (`src/pptx_generator.py`, `src/slide_layouts.py`)
The `PresentationGenerator` class orchestrates file creation:
- Initialises a `python-pptx` `Presentation` object with the selected aspect ratio.
- Iterates over validated `SlideContent` objects.
- Delegates each slide to the appropriate `LayoutRenderer` function in
  `src/slide_layouts.py`.
- Serialises the completed presentation to a `BytesIO` buffer.

`src/slide_layouts.py` contains 13 independent renderer functions, each responsible
for placing shapes, text frames, tables, and charts on a blank python-pptx slide
using absolute positioning (EMU coordinates).

### Layer 7 — Theming (`src/theme_manager.py`)
The `ThemeManager` class holds 7 hard-coded `ThemePalette` objects (named colour
dictionaries) and exposes `get_theme(name)` for palette retrieval. Each palette
defines: `background`, `text_primary`, `text_secondary`, `accent_primary`,
`accent_secondary`, `accent_tertiary`, `title_color`, `subtitle_color`.

### Layer 8 — Utilities (`src/utils.py`, `src/image_service.py`)
- `src/utils.py`: filename sanitisation, `BytesIO` PPTX integrity verification,
  JSON export/import helpers.
- `src/image_service.py`: Wikimedia REST API image fetcher with Commons fallback;
  returns `ImageResult` named tuples.

---

## 5.3 Data Flow

The complete data flow is documented in DFD Level 0 and Level 1 diagrams in
[`diagrams/dfd.md`](../diagrams/dfd.md).

In summary:

```
User Settings
    → Prompt Builder
    → Groq API (HTTP POST)
    → JSON Extractor + Repairer
    → Pydantic Validator
    → PresentationData
    → LayoutRenderer (×N slides)
    → python-pptx Presentation
    → BytesIO
    → st.download_button
```

---

## 5.4 Slide Layout Design

The 13 layout types cover the full range of content that a professional presentation
requires:

| # | Layout Name | Content Type | Key python-pptx Elements |
|---|---|---|---|
| 1 | `title` | Cover slide | Large title, subtitle, accent bar |
| 2 | `agenda` | Table of contents | Numbered items, icon column |
| 3 | `bullet_list` | Generalcontent | Title bar, styled bullet points |
| 4 | `two_column` | Comparison | Left/right text frames with divider |
| 5 | `stats_kpi` | KPIs / metrics | Card grid with value, label, trend |
| 6 | `image_text` | Visual + text | Native coloured shape + text frame |
| 7 | `process_flow` | Step-by-step | Numbered step cards with arrows |
| 8 | `table` | Tabular data | python-pptx Table object |
| 9 | `chart` | Data chart | python-pptx BarChart / LineChart |
| 10 | `section_header` | Divider | Large centred title, accent rule |
| 11 | `conclusion` | Summary | Key takeaways list |
| 12 | `references` | Bibliography | Numbered reference list |
| 13 | `ending` | Thank-you slide | Closing message, contact info |

---

## 5.5 Theme Design

Each of the 7 themes is a dictionary of 8 colour values (hex strings):

| Theme | Background | Primary Accent | Text Primary |
|---|---|---|---|
| Blue Modern | `#1E3A5F` | `#2196F3` | `#FFFFFF` |
| Dark Elegance | `#1A1A2E` | `#E94560` | `#EAEAEA` |
| Emerald Green | `#1B4332` | `#52B788` | `#FFFFFF` |
| Royal Purple | `#2D1B69` | `#7C3AED` | `#FFFFFF` |
| Sunset Warmth | `#7C2D12` | `#F97316` | `#FFFFFF` |
| Crimson Slate | `#1C1C2E` | `#DC2626` | `#E2E8F0` |
| Light Minimal | `#FFFFFF` | `#3B82F6` | `#1F2937` |

---

## 5.6 State Management

Streamlit's session state (`st.session_state`) is used to persist:

| Key | Type | Description |
|---|---|---|
| `presentation_data` | `PresentationData \| None` | Validated slide data after generation |
| `pptx_buffer` | `BytesIO \| None` | Generated PPTX binary |
| `available_models` | `List[str]` | Dynamically fetched Groq model list |
| `generation_error` | `str \| None` | Last error message for UI display |

State is cleared on page reload; no persistent storage is used.

---

## 5.7 Class and Sequence Diagrams

Full UML diagrams are available in the `diagrams/` folder:
- **Class diagram**: [`diagrams/uml_class.md`](../diagrams/uml_class.md) (Figure 8)
- **Sequence diagram**: [`diagrams/uml_sequence.md`](../diagrams/uml_sequence.md) (Figures 9, 10)
- **Use case diagram**: [`diagrams/uml_usecase.md`](../diagrams/uml_usecase.md) (Figure 11)
- **ER / logical data model**: [`diagrams/er_diagram.md`](../diagrams/er_diagram.md) (Figure 13)

