# Chapter 7 — Testing

## 7.1 Testing Strategy

The project adopts a **unit and integration testing** strategy using the **pytest**
framework. Tests are co-located under the `tests/` directory and are organized into
four test modules corresponding to the four primary subsystems:

| Test File | Subsystem Tested | Tests |
|---|---|---|
| `test_ai_service.py` | `GroqAIService` | 4 |
| `test_content_validator.py` | `ContentValidator` | 6 |
| `test_pptx_generator.py` | `PresentationGenerator` / `LayoutRenderer` | 5 |
| `test_utils.py` | Utility functions | 3 |
| **Total** | | **18** |

All 18 tests pass on the target platform (Python 3.15.0, pytest 9.1.1, Windows 11).

---

## 7.2 Test Environment Setup

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run all tests with verbose output
python -m pytest tests -v
```

---

## 7.3 Test Module: `test_ai_service.py`

### TC-AI-01: `test_missing_api_key_behavior`
**Purpose**: Verify that `GroqAIService` raises a `ValueError` when no API key is
provided and `generate_presentation()` is called.

**Input**: `GroqAIService(api_key="")`, topic="Test"

**Expected**: `ValueError` raised with message containing "API key".

**Result**: ✅ PASSED

---

### TC-AI-02: `test_empty_topic_behavior`
**Purpose**: Verify that an empty or whitespace-only topic is rejected before the
API call is made.

**Input**: `GroqAIService(api_key="dummy")`, topic="   "

**Expected**: `ValueError` raised with message indicating empty topic.

**Result**: ✅ PASSED

---

### TC-AI-03: `test_mocked_groq_successful_generation`
**Purpose**: Verify the complete generation pipeline using a mocked Groq client
that returns a valid JSON string.

**Method**: `unittest.mock.patch` replaces `Groq.chat.completions.create` with a
stub that returns a mock response object containing a valid JSON slide outline.

**Input**: Valid topic, 5-slide config, mocked Groq client.

**Expected**: Returns a `PresentationData` object with 5 slides and correct title.

**Result**: ✅ PASSED

---

### TC-AI-04: `test_image_service_graceful_fallback`
**Purpose**: Verify that `ImageService` returns a valid placeholder result when
the Wikimedia API is unreachable (network mocked to raise `ConnectionError`).

**Method**: `unittest.mock.patch` replaces `requests.get` to raise `ConnectionError`.

**Expected**: Returns an `ImageResult` with `success=False` and no exception raised.

**Result**: ✅ PASSED

---

## 7.4 Test Module: `test_content_validator.py`

### TC-VAL-01: `test_extract_json_from_markdown`
**Purpose**: Verify that JSON wrapped in markdown fences is correctly extracted.

**Input**:
```
```json
{"title": "Test", "slides": []}
```
```

**Expected**: Extracted string is `{"title": "Test", "slides": []}`.

**Result**: ✅ PASSED

---

### TC-VAL-02: `test_repair_trailing_commas`
**Purpose**: Verify that trailing commas before `}` and `]` are removed.

**Input**: `{"key": "value",}` and `["a", "b",]`

**Expected**: Both repaired to valid JSON without trailing commas.

**Result**: ✅ PASSED

---

### TC-VAL-03: `test_normalize_layout_names`
**Purpose**: Verify that layout aliases are correctly mapped to canonical names.

**Input**: Slides with layouts `"cover"`, `"toc"`, `"kpi"`, `"steps"`, `"vs"`.

**Expected**: Mapped to `"title"`, `"agenda"`, `"stats_kpi"`, `"process_flow"`,
`"two_column"` respectively.

**Result**: ✅ PASSED

---

### TC-VAL-04: `test_slide_count_enforcement`
**Purpose**: Verify that the slide list is padded when fewer slides than requested
are returned by the AI.

**Input**: JSON with 3 slides, `target_slide_count=7`.

**Expected**: `PresentationData.slides` has length 7; padded slides use
`layout="bullet_list"`.

**Result**: ✅ PASSED

---

### TC-VAL-05: `test_empty_response_handling`
**Purpose**: Verify that an empty string response does not crash the application.

**Input**: `raw_text=""`

**Expected**: Returns a `PresentationData` using the offline sample fallback
without raising an exception.

**Result**: ✅ PASSED

---

### TC-VAL-06: `test_missing_fields_defaulting`
**Purpose**: Verify that slides with missing optional fields receive correct
default values from Pydantic.

**Input**: JSON with slides missing `speaker_notes`, `bullets`, and `body_text`.

**Expected**: Missing fields default to `""` or `[]` as per schema definition.

**Result**: ✅ PASSED

---

## 7.5 Test Module: `test_pptx_generator.py`

### TC-PPT-01: `test_offline_pptx_generation_integrity`
**Purpose**: Verify that the complete offline pipeline produces a valid `.pptx`
binary that can be re-opened by python-pptx.

**Method**: Generate using offline sample; call `verify_pptx_integrity(buffer)`.

**Expected**: Returns `True`; `Presentation(buffer)` does not raise.

**Result**: ✅ PASSED

---

### TC-PPT-02: `test_aspect_ratios_16_9_and_4_3`
**Purpose**: Verify that both supported aspect ratios produce PPTX files with
the correct slide dimensions.

**Input**: Generate with `aspect_ratio="16:9"` and `aspect_ratio="4:3"`.

**Expected**:
- 16:9: width=9144000 EMU, height=5143500 EMU
- 4:3: width=9144000 EMU, height=6858000 EMU

**Result**: ✅ PASSED

---

### TC-PPT-03: `test_theme_variations`
**Purpose**: Verify that all 7 themes produce valid PPTX output without errors.

**Method**: Iterate all theme names; generate a 3-slide presentation with each.

**Expected**: No exception raised; all 7 PPTX buffers pass integrity check.

**Result**: ✅ PASSED

---

### TC-PPT-04: `test_speaker_notes_presence`
**Purpose**: Verify that speaker notes are added to slides when
`include_speaker_notes=True` and the slide has non-empty `speaker_notes` text.

**Input**: Slide with `speaker_notes="Test notes"`, config with
`include_speaker_notes=True`.

**Expected**: `slide.notes_slide.notes_text_frame.text` equals "Test notes".

**Result**: ✅ PASSED

---

### TC-PPT-05: `test_all_layout_types_render_safely`
**Purpose**: Verify that all 13 layout types can be rendered without raising
any exception.

**Method**: Create a `SlideContent` object for each layout type with minimal
valid data; call the corresponding renderer.

**Expected**: No exception raised for any of the 13 layouts.

**Result**: ✅ PASSED

---

## 7.6 Test Module: `test_utils.py`

### TC-UTL-01: `test_sanitize_filename`
**Purpose**: Verify that `sanitize_filename()` replaces special characters and
truncates long names.

**Input**: `"Hello World! (2024) — Test #1"`, `"A" * 200`

**Expected**: `"Hello_World__2024____Test__1"`, truncated to 50 chars.

**Result**: ✅ PASSED

---

### TC-UTL-02: `test_verify_pptx_integrity_invalid_data`
**Purpose**: Verify that `verify_pptx_integrity()` returns `False` for non-PPTX
binary data.

**Input**: `BytesIO(b"not a pptx file")`

**Expected**: Returns `False` without raising an exception.

**Result**: ✅ PASSED

---

### TC-UTL-03: `test_json_export_import_roundtrip`
**Purpose**: Verify that exporting a `PresentationData` to JSON and re-importing
it produces an identical object.

**Input**: A `PresentationData` object with 3 slides.

**Expected**: `import_presentation_json(export_presentation_json(data)) == data`

**Result**: ✅ PASSED

---

## 7.7 Full Test Output

```
============================= test session starts =============================
platform win32 -- Python 3.15.0, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\Sem 7\ROSPL\AI_PPT
plugins: anyio-4.15.1
collected 18 items

tests/test_ai_service.py::test_missing_api_key_behavior PASSED         [  5%]
tests/test_ai_service.py::test_empty_topic_behavior PASSED             [ 11%]
tests/test_ai_service.py::test_mocked_groq_successful_generation PASSED [ 16%]
tests/test_ai_service.py::test_image_service_graceful_fallback PASSED  [ 22%]
tests/test_content_validator.py::test_extract_json_from_markdown PASSED [ 27%]
tests/test_content_validator.py::test_repair_trailing_commas PASSED    [ 33%]
tests/test_content_validator.py::test_normalize_layout_names PASSED    [ 38%]
tests/test_content_validator.py::test_slide_count_enforcement PASSED   [ 44%]
tests/test_content_validator.py::test_empty_response_handling PASSED   [ 50%]
tests/test_content_validator.py::test_missing_fields_defaulting PASSED [ 55%]
tests/test_pptx_generator.py::test_offline_pptx_generation_integrity PASSED [ 61%]
tests/test_pptx_generator.py::test_aspect_ratios_16_9_and_4_3 PASSED  [ 66%]
tests/test_pptx_generator.py::test_theme_variations PASSED             [ 72%]
tests/test_pptx_generator.py::test_speaker_notes_presence PASSED       [ 77%]
tests/test_pptx_generator.py::test_all_layout_types_render_safely PASSED [ 83%]
tests/test_utils.py::test_sanitize_filename PASSED                     [ 88%]
tests/test_utils.py::test_verify_pptx_integrity_invalid_data PASSED   [ 94%]
tests/test_utils.py::test_json_export_import_roundtrip PASSED         [100%]

============================= 18 passed in 5.72s ==============================
```

---

## 7.8 Test Coverage Summary

| Subsystem | Tests | Result |
|---|---|---|
| AI Service & Groq Integration | 4 | ✅ All Pass |
| Content Validation & JSON Repair | 6 | ✅ All Pass |
| PPTX Generation & Layout Rendering | 5 | ✅ All Pass |
| Utility Functions | 3 | ✅ All Pass |
| **Total** | **18** | **✅ 18/18 Pass** |

> **Note**: UI-layer tests (Streamlit `app.py`) are not included in the automated
> suite due to Streamlit's stateful rendering architecture. UI behaviour was
> validated through manual interaction testing across Chrome, Edge, and Firefox.

