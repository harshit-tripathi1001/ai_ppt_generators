"""Automated tests for JSON parsing, schema normalization, and content validation."""

import pytest
import json
from src.content_validator import (
    extract_json_from_text,
    repair_common_json_issues,
    normalize_layout_name,
    validate_presentation_data,
    parse_and_validate_response
)


def test_extract_json_from_markdown():
    """Verify JSON extraction from markdown code fences."""
    raw = "Here is the presentation:\n```json\n{\"title\": \"AI Future\", \"slides\": []}\n```\nHope you like it!"
    extracted = extract_json_from_text(raw)
    assert extracted is not None
    data = json.loads(extracted)
    assert data["title"] == "AI Future"


def test_repair_trailing_commas():
    """Verify repair of trailing commas in JSON."""
    bad_json = '{"title": "Test", "slides": [{"title": "S1", "bullets": ["A", "B",],},],}'
    repaired = repair_common_json_issues(bad_json)
    parsed = json.loads(repaired)
    assert parsed["title"] == "Test"
    assert len(parsed["slides"][0]["bullets"]) == 2


def test_normalize_layout_names():
    """Verify mapping of varied layout names to standard layouts."""
    assert normalize_layout_name("title_and_content") == "bullet_list"
    assert normalize_layout_name("table_of_contents") == "agenda"
    assert normalize_layout_name("comparison") == "two_column"
    assert normalize_layout_name("statistics") == "stats_kpi"
    assert normalize_layout_name("visual") == "image_text"
    assert normalize_layout_name("unknown_layout_xyz") == "bullet_list"


def test_slide_count_enforcement():
    """Verify that requested slide count is precisely respected."""
    mock_input = {
        "title": "Quantum Computing",
        "slides": [
            {"title": "Slide 1", "layout": "bullet_list", "bullets": ["Point 1"]},
            {"title": "Slide 2", "layout": "bullet_list", "bullets": ["Point 2"]}
        ]
    }
    # Request 5 slides: validator must pad to exactly 5 slides
    validated = validate_presentation_data(
        parsed_json=mock_input,
        requested_slides=5,
        topic="Quantum Computing",
        include_toc=False,
        include_conclusion=False,
        include_references=False,
        include_title_slide=True,
        include_ending_slide=False
    )
    assert len(validated.slides) == 5
    assert validated.slides[0].layout == "title"


def test_empty_response_handling():
    """Verify that empty or malformed strings return descriptive errors."""
    val, err = parse_and_validate_response("", 5, "Topic")
    assert val is None
    assert "Empty response" in err

    val2, err2 = parse_and_validate_response("Not valid JSON at all", 5, "Topic")
    assert val2 is None
    assert "Could not parse" in err2 or "No valid JSON" in err2


def test_missing_fields_defaulting():
    """Verify that slides with missing titles or bullets receive sensible defaults."""
    raw_dict = {
        "title": "Edge AI",
        "slides": [
            {}  # completely empty slide dict
        ]
    }
    validated = validate_presentation_data(
        parsed_json=raw_dict,
        requested_slides=3,
        topic="Edge AI",
        include_toc=False,
        include_conclusion=False,
        include_title_slide=False,
        include_ending_slide=False
    )
    assert len(validated.slides) == 3
    # Check that missing fields were defaulted gracefully
    assert validated.slides[0].title is not None
    assert len(validated.slides[0].bullets) > 0

