"""PowerPoint presentation generation module.

Integrates theme configurations, content layouts, image retrieval,
and python-pptx presentation construction in an independent, testable service.
"""

import io
import os
import logging
from typing import Optional, Union, Dict, Any
from pptx import Presentation
from pptx.util import Inches

from src.content_schema import PresentationData, SlideContent
from src.theme_manager import get_theme_palette, ThemePalette
from src.slide_layouts import LayoutRenderer

logger = logging.getLogger(__name__)


def generate_presentation_pptx(
    presentation_data: PresentationData,
    theme: Union[str, ThemePalette] = "Blue Modern",
    font_name: str = "Calibri",
    font_size: int = 22,
    aspect_ratio: str = "16:9",
    include_slide_numbers: bool = True,
    logo_bytes: Optional[bytes] = None,
    output_path: Optional[str] = None,
    *args,
    **kwargs
) -> io.BytesIO:
    """Generate an editable PowerPoint presentation from structured presentation data.

    Args:
        presentation_data: Validated PresentationData object.
        theme: Theme name (str) or ThemePalette instance.
        font_name: Typography font family.
        font_size: Base font size scale.
        aspect_ratio: '16:9' or '4:3'.
        include_slide_numbers: Whether to stamp slide index footers.
        logo_bytes: Optional raw bytes of company/brand logo.
        output_path: Optional path on disk to also save the generated .pptx file.

    Returns:
        io.BytesIO containing the complete PPTX binary data.
    """
    prs = Presentation()

    # Determine slide dimensions
    is_widescreen = (aspect_ratio == "16:9")
    if is_widescreen:
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
    else:
        prs.slide_width = Inches(10.0)
        prs.slide_height = Inches(7.5)

    # Resolve theme palette
    if isinstance(theme, str):
        theme_palette = get_theme_palette(theme)
    else:
        theme_palette = theme

    # Initialize layout renderer
    renderer = LayoutRenderer(
        presentation=prs,
        theme=theme_palette,
        font_name=font_name,
        font_size_base=font_size,
        is_widescreen=is_widescreen,
        logo_bytes=logo_bytes
    )

    total_slides = len(presentation_data.slides)
    topic = presentation_data.title

    for idx, slide in enumerate(presentation_data.slides):
        current_idx = idx + 1
        layout = (slide.layout or "bullet_list").lower()

        try:
            if layout == "title":
                renderer.render_title_slide(
                    slide_data=slide,
                    presentation_title=presentation_data.title,
                    subtitle=presentation_data.subtitle,
                    audience=presentation_data.target_audience or ""
                )

            elif layout == "agenda":
                renderer.render_agenda_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "two_column":
                renderer.render_two_column_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "stats_kpi":
                renderer.render_stats_kpi_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "image_text":
                renderer.render_image_text_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "process_flow":
                renderer.render_process_flow_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "table":
                renderer.render_table_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "chart":
                renderer.render_chart_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "section_header":
                renderer.render_section_header_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "conclusion":
                renderer.render_conclusion_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "references":
                renderer.render_references_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

            elif layout == "ending":
                renderer.render_ending_slide(
                    slide_data=slide,
                    presentation_title=presentation_data.title
                )

            else:
                # Default: bullet_list layout
                renderer.render_bullet_list_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )

        except Exception as e:
            logger.exception("Error rendering layout '%s' for slide %s. Falling back to bullet_list.", layout, current_idx)
            try:
                renderer.render_bullet_list_slide(
                    slide_data=slide,
                    current_idx=current_idx,
                    total_slides=total_slides,
                    topic=topic
                )
            except Exception as e2:
                logger.critical("Critical fallback failure on slide %s: %s", current_idx, e2)

    # Save to BytesIO in-memory stream
    pptx_stream = io.BytesIO()
    prs.save(pptx_stream)
    pptx_stream.seek(0)

    # Optionally persist to disk
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pptx_stream.getvalue())
        pptx_stream.seek(0)

    return pptx_stream

