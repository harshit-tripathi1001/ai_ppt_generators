# Appendix C — Full Pytest Output

This appendix records the complete output of the automated test suite as executed
on the development machine.

**Platform**: Windows 11  
**Python**: 3.15.0 (CPython)  
**pytest**: 9.1.1  
**pluggy**: 1.7.0  
**Virtual Environment**: `D:\Sem 7\ROSPL\AI_PPT\.venv`

**Command**:
```bash
python -m pytest tests -v
```

**Output**:
```
============================= test session starts =============================
platform win32 -- Python 3.15.0, pytest-9.1.1, pluggy-1.7.0 --
D:\Sem 7\ROSPL\AI_PPT\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Sem 7\ROSPL\AI_PPT
plugins: anyio-4.15.1
collecting ... collected 18 items

tests/test_ai_service.py::test_missing_api_key_behavior PASSED           [  5%]
tests/test_ai_service.py::test_empty_topic_behavior PASSED               [ 11%]
tests/test_ai_service.py::test_mocked_groq_successful_generation PASSED  [ 16%]
tests/test_ai_service.py::test_image_service_graceful_fallback PASSED    [ 22%]
tests/test_content_validator.py::test_extract_json_from_markdown PASSED  [ 27%]
tests/test_content_validator.py::test_repair_trailing_commas PASSED      [ 33%]
tests/test_content_validator.py::test_normalize_layout_names PASSED      [ 38%]
tests/test_content_validator.py::test_slide_count_enforcement PASSED     [ 44%]
tests/test_content_validator.py::test_empty_response_handling PASSED     [ 50%]
tests/test_content_validator.py::test_missing_fields_defaulting PASSED   [ 55%]
tests/test_pptx_generator.py::test_offline_pptx_generation_integrity PASSED [ 61%]
tests/test_pptx_generator.py::test_aspect_ratios_16_9_and_4_3 PASSED     [ 66%]
tests/test_pptx_generator.py::test_theme_variations PASSED               [ 72%]
tests/test_pptx_generator.py::test_speaker_notes_presence PASSED         [ 77%]
tests/test_pptx_generator.py::test_all_layout_types_render_safely PASSED [ 83%]
tests/test_utils.py::test_sanitize_filename PASSED                       [ 88%]
tests/test_utils.py::test_verify_pptx_integrity_invalid_data PASSED      [ 94%]
tests/test_utils.py::test_json_export_import_roundtrip PASSED            [100%]

============================= 18 passed in 5.72s ==============================
```

---

## Test File Listing

```
tests/
├── __init__.py
├── test_ai_service.py          (4 tests)
├── test_content_validator.py   (6 tests)
├── test_pptx_generator.py      (5 tests)
└── test_utils.py               (3 tests)
```

**Total**: 18 tests, 0 failures, 0 errors, 0 skips  
**Execution time**: 5.72 seconds

