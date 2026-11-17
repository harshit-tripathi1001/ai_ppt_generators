# Chapter 6 — Implementation

## 6.1 Development Environment

| Component | Value |
|---|---|
| Operating System | Windows 11 |
| Python Version | 3.15.0 (CPython) |
| Virtual Environment | `.venv` (pip-managed) |
| IDE | VS Code / Antigravity |
| Version Control | Git |
| Package Manager | pip |
| Test Framework | pytest 9.1.1 |

---

## 6.2 Module Descriptions

### 6.2.1 `config.py` — Configuration Module

Loads environment variables from `.env` using `python-dotenv` with a
`try/except` fallback. Exposes:

```python
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
DEFAULT_THEME  = "Blue Modern"
APP_TITLE      = "AI PPT Generator"
```

The `try/except` pattern around `from dotenv import load_dotenv` prevents the
application from crashing when `python-dotenv` is not installed in an edge-case
environment, instead silently falling back to raw `os.getenv` calls.

---

### 6.2.2 `src/ai_service.py` — Groq AI Service

**Class**: `GroqAIService`

#### Key Method: `generate_presentation()`

```python
def generate_presentation(self, topic: str, config: Dict[str, Any]
                          ) -> Tuple[PresentationData, str]:
```

This method:
1. Calls `_build_prompt(topic, config)` to assemble the LLM instruction string.
2. Calls `_call_groq_api(prompt, config)` with retry and fallback logic.
3. Passes the raw response to `parse_and_validate_response()`.
4. Returns the validated `PresentationData` and the model name used.

#### Algorithm: Model Auto-Fallback

```
WHILE attempt < MAX_RETRIES:
    TRY:
        response = groq_client.chat.completions.create(model=current_model, ...)
        RETURN response.choices[0].message.content
    EXCEPT HTTP 404 (model_not_found):
        SELECT next model from priority list
        LOG warning
        CONTINUE
    EXCEPT RateLimitError:
        SLEEP 2^attempt seconds
        CONTINUE
    EXCEPT AuthenticationError:
        RAISE immediately (no retry)
```

#### Algorithm: Prompt Construction

The prompt is a structured instruction string with the following sections:
1. **Role assignment**: "You are a professional presentation creator."
2. **Task description**: Generate a JSON slide outline for the given topic.
3. **JSON schema template**: Inline schema showing expected fields and types.
4. **Content constraints**: Number of slides, language, style, depth, audience.
5. **Structural requirements**: Which optional slides to include (ToC, conclusion, references).
6. **Output instruction**: "Return ONLY valid JSON. No markdown, no explanation."

#### Offline Sample Generator

When no API key is configured, `generate_offline_sample(topic)` returns a
pre-defined `PresentationData` with 5 slides covering introduction, overview,
key points, statistics, and conclusion — providing a functional demo without
any external dependency.

---

### 6.2.3 `src/content_schema.py` — Pydantic Data Models

Defines the data contract using Pydantic v2 `BaseModel` classes. Key design
decisions:

- **`SlideContent.layout`** uses a `str` field (not a Python `Enum`) to allow
  flexible layout normalization in the validator without Pydantic rejection.
- **Optional nested models** (`table`, `chart`, `kpi_metrics`, `process_steps`,
  `columns`) are typed as `Optional[X] = None`, allowing the validator to ignore
  absent fields.
- **`PresentationData.slides`** has a minimum length validator of 1 to prevent
  empty presentations.

---

### 6.2.4 `src/content_validator.py` — JSON Parsing and Validation

**Key function**: `parse_and_validate_response(raw_text, target_slide_count)`

#### Algorithm: JSON Extraction

```
1. Strip whitespace from raw_text
2. If text starts with ```json or ``` fence, extract content between fences
3. Otherwise, locate first '{' and last '}' in text
4. If no JSON boundary found, raise ValueError
5. Return extracted substring
```

#### Algorithm: JSON Repair

```
1. Remove trailing commas before '}' or ']' (regex substitution)
2. Count open and close braces/brackets
3. Append missing closing characters to balance structure
4. Attempt json.loads(); if fails, return original for Pydantic to reject
```

#### Algorithm: Layout Normalization

A dictionary of 50+ aliases maps non-canonical layout names to the 13 supported
types. Examples:

| Input alias | Canonical layout |
|---|---|
| `"cover"`, `"front"`, `"intro"` | `"title"` |
| `"toc"`, `"contents"`, `"overview"` | `"agenda"` |
| `"kpi"`, `"metrics"`, `"stats"` | `"stats_kpi"` |
| `"steps"`, `"workflow"`, `"timeline"` | `"process_flow"` |
| `"comparison"`, `"versus"`, `"2col"` | `"two_column"` |
| `"thank_you"`, `"close"`, `"final"` | `"ending"` |

#### Algorithm: Slide Count Enforcement

```
target = config["num_slides"]
current = len(slides)
IF current > target:
    preserve first slide (title) and last slide (ending)
    trim middle slides to fill (target - 2) slots
ELIF current < target:
    needed = target - current
    generate 'needed' padding slides with layout="bullet_list"
    insert padding slides before the last slide
```

---

### 6.2.5 `src/pptx_generator.py` — PPTX Orchestrator

**Class**: `PresentationGenerator`

Key method `generate_presentation_pptx(data, config)`:

1. Creates a `python-pptx` `Presentation()` object.
2. Sets slide width and height for the chosen aspect ratio (16:9 or 4:3).
3. Calls `theme_manager.get_theme(data.theme)` to retrieve the colour palette.
4. Iterates `data.slides`; for each `SlideContent`:
   a. Adds a blank slide layout to the presentation.
   b. Sets the slide background colour using `prs.slides[-1].background.fill`.
   c. Dispatches to the appropriate renderer from `LAYOUT_DISPATCH_TABLE`.
   d. If `include_speaker_notes` and `slide.speaker_notes` is non-empty, adds
      a speaker notes frame.
5. Serialises to `BytesIO` and returns the buffer.

---

### 6.2.6 `src/slide_layouts.py` — Layout Renderers (13 Types)

Each renderer function has the signature:

```python
def render_<layout>(slide, content: SlideContent, palette: ThemePalette,
                    font_family: str, font_size: int) -> None:
```

All positioning uses EMU (English Metric Units) coordinates. Key constants:
- `SLIDE_WIDTH = 9144000 EMU` (12 inches at 914400 EMU/inch)
- `SLIDE_HEIGHT = 5143500 EMU` (6.75 inches, for 16:9)

Representative implementation — `render_stats_kpi()`:
1. Divides slide width by the number of KPI metrics (max 4 per row).
2. For each `KpiMetric`:
   - Adds a filled rectangle as a card background.
   - Adds a large bold text frame for the `value`.
   - Adds a smaller text frame for the `label`.
   - Adds a coloured arrow/symbol for the `trend` (▲ green / ▼ red / — grey).

---

### 6.2.7 `src/theme_manager.py` — Theme Management

Contains a `THEMES` dictionary of 7 `ThemePalette` named tuples. The
`ThemeManager.get_theme(name)` method performs a case-insensitive lookup with
a fallback to `"Blue Modern"` if the name is not found.

---

### 6.2.8 `src/image_service.py` — Image Retrieval (Wikimedia)

`ImageService` fetches Creative-Commons-licensed images from Wikimedia:

1. **Primary**: Wikipedia REST API — `GET /page/summary/{topic}` → `originalimage.source` URL.
2. **Fallback**: Wikimedia Commons API — `action=query&list=search&gsrnamespace=6` → file URL.
3. If both fail, returns a placeholder coloured rectangle drawn with python-pptx native shapes.

> **Note**: The image retrieval feature is optional and primarily used by the
> `image_text` layout. The Pexels and Unsplash integrations were removed in an
> earlier iteration due to API key availability issues.

---

### 6.2.9 `src/utils.py` — Utility Functions

| Function | Description |
|---|---|
| `sanitize_filename(text)` | Replaces non-alphanumeric characters with underscores; truncates to 50 chars |
| `verify_pptx_integrity(buffer)` | Attempts to open the buffer as a `Presentation`; returns `True` if valid |
| `export_presentation_json(data)` | Serialises `PresentationData` to JSON string via `model.model_dump_json()` |
| `import_presentation_json(json_str)` | Parses JSON string and re-validates via `PresentationData.model_validate()` |

---

## 6.3 Prompt Engineering

The LLM prompt is engineered to maximise JSON conformance:

1. **Explicit schema**: The prompt includes a JSON template with all expected
   keys and example values, reducing hallucinated field names.
2. **Slide count constraint**: The exact number of slides is stated twice — in
   the narrative and in the schema template.
3. **Layout instructions**: Valid layout names are listed explicitly; the model
   is instructed not to invent new layouts.
4. **Output constraint**: "Return ONLY the JSON object. Do not include any
   explanation, preamble, or markdown formatting." — reduces fence wrapping.
5. **Language constraint**: When a non-English language is selected, the model is
   instructed to generate all slide content in that language while keeping JSON
   keys in English.

---

## 6.4 Key Implementation Challenges

### Challenge 1: Malformed LLM JSON
LLMs frequently produce JSON with trailing commas, unbalanced brackets, or
markdown fences. The multi-stage repair pipeline in `content_validator.py`
handles these deterministically.

### Challenge 2: Model Availability
The user's Groq account may not have access to all advertised model IDs. The
dynamic model discovery via `GET /v1/models` and the 404-triggered fallback
mechanism ensure the application works regardless of which specific models are
enabled on the account.

### Challenge 3: Streamlit Module Caching
Streamlit's `importlib` caching caused stale module versions to persist across
hot-reloads during development. This was resolved by adding `importlib.reload()`
calls at the top of `app.py` for affected modules during development, and by
clearing `__pycache__` directories after structural code changes.

### Challenge 4: EMU Coordinate Precision
python-pptx uses EMU as its internal unit. All layout renderers perform precise
EMU arithmetic to ensure elements are correctly positioned across both 16:9 and
4:3 aspect ratios, with the aspect ratio difference handled by a ratio multiplier
applied to the `SLIDE_HEIGHT` constant.

