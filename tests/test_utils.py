"""Automated tests for utility helpers, filename sanitization, and JSON import/export."""

import io
import pytest
from src.utils import (
    sanitize_filename,
    verify_pptx_integrity,
    export_presentation_to_json,
    import_presentation_from_json
)
from src.ai_service import generate_offline_sample


def test_sanitize_filename():
    """Verify filename sanitization handles special characters, slashes, and spaces."""
    assert sanitize_filename("AI & Robotics: The Future (2025)?") == "AI_Robotics_The_Future_2025.pptx"
    assert sanitize_filename("topic/subtopic\\test*name") == "topicsubtopictestname.pptx"
    assert sanitize_filename("") == "presentation.pptx"
    assert sanitize_filename("   ") == "presentation.pptx"


def test_verify_pptx_integrity_invalid_data():
    """Verify corrupted bytes fail integrity check with descriptive message."""
    invalid_bytes = io.BytesIO(b"Not a zip file at all")
    is_valid, msg = verify_pptx_integrity(invalid_bytes)
    assert is_valid is False
    assert "not a valid ZIP" in msg


def test_json_export_import_roundtrip():
    """Verify export to JSON and re-import preserves presentation structure."""
    original = generate_offline_sample(topic="Quantum Mechanics", slide_count=4)
    json_text = export_presentation_to_json(original)
    assert json_text is not None
    assert "Quantum Mechanics" in json_text

    imported, err = import_presentation_from_json(json_text)
    assert err is None
    assert imported is not None
    assert imported.title == original.title
    assert len(imported.slides) == len(original.slides)

