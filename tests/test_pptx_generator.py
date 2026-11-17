"""Automated tests for PowerPoint (.pptx) creation, layouts, themes, and integrity."""

import io
import pytest
from pptx import Presentation

from src.ai_service import generate_offline_sample
from src.pptx_generator import generate_presentation_pptx
from src.theme_manager import get_theme_palette, THEMES
from src.utils import verify_pptx_integrity


def test_offline_pptx_generation_integrity():
    """Verify that a presentation generates offline and passes strict ZIP/OOXML integrity checks."""
    sample_data = generate_offline_sample(topic="Modern Cloud Architecture", slide_count=10)
    pptx_bytes = generate_presentation_pptx(
        presentation_data=sample_data,
        theme="Blue Modern",
        font_name="Calibri",
        font_size=22,
        aspect_ratio="16:9",
        include_slide_numbers=True,
        include_images=False
    )

    assert pptx_bytes is not None
    assert pptx_bytes.getbuffer().nbytes > 1000

    # Verify integrity
    is_valid, msg = verify_pptx_integrity(pptx_bytes)
    assert is_valid is True, f"Integrity failed: {msg}"

    # Re-open with python-pptx to inspect contents
    pptx_bytes.seek(0)
    prs = Presentation(pptx_bytes)
    assert len(prs.slides) == 10


def test_aspect_ratios_16_9_and_4_3():
    """Verify widescreen (16:9) and standard (4:3) slide dimensions."""
    sample_data = generate_offline_sample(topic="Aspect Ratio Test", slide_count=3)

    # 16:9
    stream_16_9 = generate_presentation_pptx(sample_data, aspect_ratio="16:9")
    prs_16_9 = Presentation(stream_16_9)
    assert round(prs_16_9.slide_width.inches, 2) == 13.33
    assert round(prs_16_9.slide_height.inches, 2) == 7.50

    # 4:3
    stream_4_3 = generate_presentation_pptx(sample_data, aspect_ratio="4:3")
    prs_4_3 = Presentation(stream_4_3)
    assert round(prs_4_3.slide_width.inches, 2) == 10.00
    assert round(prs_4_3.slide_height.inches, 2) == 7.50


def test_theme_variations():
    """Verify that multiple light and dark themes generate without errors."""
    sample_data = generate_offline_sample(topic="Theme Test", slide_count=4)

    test_themes = ["Blue Modern", "Dark Elegance", "Emerald Green", "Royal Purple", "Light Minimal"]
    for theme_name in test_themes:
        stream = generate_presentation_pptx(sample_data, theme=theme_name)
        assert stream is not None
        is_valid, _ = verify_pptx_integrity(stream)
        assert is_valid is True


def test_speaker_notes_presence():
    """Verify that speaker notes are correctly attached to slides."""
    sample_data = generate_offline_sample(topic="Speaker Notes Test", slide_count=5)
    stream = generate_presentation_pptx(sample_data)
    prs = Presentation(stream)

    has_notes = False
    for slide in prs.slides:
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text
            if notes_text and len(notes_text.strip()) > 0:
                has_notes = True
                break

    assert has_notes is True, "Expected at least one slide with speaker notes attached."


def test_all_layout_types_render_safely():
    """Verify that rich layouts (tables, charts, KPIs, two-column, timeline) render without crashing."""
    sample_data = generate_offline_sample(topic="Full Layout Test", slide_count=10)
    stream = generate_presentation_pptx(sample_data, include_images=True)
    is_valid, msg = verify_pptx_integrity(stream)
    assert is_valid is True, f"Full layout rendering failed integrity: {msg}"

