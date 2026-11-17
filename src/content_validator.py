"""Content validation and JSON parsing module.

Provides resilient parsing of LLM outputs, structural validation,
schema repair, and sanitization for presentation content.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from src.content_schema import (
    PresentationData,
    SlideContent,
    VALID_LAYOUTS,
    KpiMetric,
    ColumnData,
    TableData,
    ChartData,
    ChartSeries,
    ProcessStep
)

logger = logging.getLogger(__name__)


def extract_json_from_text(raw_text: str) -> Optional[str]:
    """Extract JSON string from raw text that may contain markdown fences or commentary.

    Args:
        raw_text: Raw string response from LLM.

    Returns:
        Isolated JSON string or None if no JSON block detected.
    """
    if not raw_text or not isinstance(raw_text, str):
        return None

    cleaned = raw_text.strip()

    # Case 1: Markdown code block (```json ... ``` or ``` ... ```)
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if code_block_match:
        return code_block_match.group(1).strip()

    # Case 2: Direct JSON object starting with { and ending with }
    brace_match = re.search(r"(\{[\s\S]*\})", cleaned)
    if brace_match:
        return brace_match.group(1).strip()

    return cleaned


def repair_common_json_issues(json_str: str) -> str:
    """Repair common syntax issues in AI-generated JSON.

    - Trailing commas before } or ]
    - Unescaped newlines in strings
    - Unbalanced brackets/braces
    """
    repaired = json_str

    # Remove single-line JS-style comments: // ...
    repaired = re.sub(r'//[^\n]*', '', repaired)

    # Remove trailing commas in objects and arrays: , \s* [}\]]
    repaired = re.sub(r',\s*([}\]])', r'\1', repaired)

    # Balance unclosed curly braces if simple cutoff
    open_curly = repaired.count('{')
    close_curly = repaired.count('}')
    if open_curly > close_curly:
        repaired += '}' * (open_curly - close_curly)

    open_square = repaired.count('[')
    close_square = repaired.count(']')
    if open_square > close_square:
        repaired += ']' * (open_square - close_square)

    return repaired


def sanitize_text(text: Any, max_len: int = 500) -> str:
    """Sanitize and trim string fields for slides."""
    if text is None:
        return ""
    text_str = str(text).strip()
    # Replace weird unicode quotes or control characters
    text_str = text_str.replace('\u201c', '"').replace('\u201d', '"')
    text_str = text_str.replace('\u2018', "'").replace('\u2019', "'")
    text_str = text_str.replace('\t', ' ')
    if len(text_str) > max_len:
        text_str = text_str[:max_len].rstrip() + "..."
    return text_str


def normalize_layout_name(layout: str) -> str:
    """Map arbitrary AI layout strings to standard valid layouts."""
    if not layout or not isinstance(layout, str):
        return "bullet_list"

    layout_clean = layout.strip().lower().replace("-", "_").replace(" ", "_")

    alias_map = {
        "title_and_content": "bullet_list",
        "title_content": "bullet_list",
        "bullets": "bullet_list",
        "bullet": "bullet_list",
        "list": "bullet_list",
        "toc": "agenda",
        "table_of_contents": "agenda",
        "outline": "agenda",
        "comparison": "two_column",
        "two_columns": "two_column",
        "columns": "two_column",
        "kpi": "stats_kpi",
        "statistics": "stats_kpi",
        "stats": "stats_kpi",
        "metrics": "stats_kpi",
        "image": "image_text",
        "picture": "image_text",
        "visual": "image_text",
        "process": "process_flow",
        "timeline": "process_flow",
        "steps": "process_flow",
        "flow": "process_flow",
        "data_table": "table",
        "grid": "table",
        "graph": "chart",
        "data_chart": "chart",
        "divider": "section_header",
        "section": "section_header",
        "summary": "conclusion",
        "takeaway": "conclusion",
        "sources": "references",
        "citations": "references",
        "thank_you": "ending",
        "closing": "ending"
    }

    if layout_clean in VALID_LAYOUTS:
        return layout_clean

    return alias_map.get(layout_clean, "bullet_list")


def validate_slide_dict(raw_slide: Dict[str, Any], index: int, default_topic: str) -> SlideContent:
    """Validate and normalize a raw slide dictionary into a SlideContent object."""
    title = sanitize_text(raw_slide.get("title", f"Slide {index + 1}"), max_len=120)
    if not title:
        title = f"Slide {index + 1}"

    layout = normalize_layout_name(str(raw_slide.get("layout", "bullet_list")))
    key_message = sanitize_text(raw_slide.get("key_message", ""), max_len=200)

    # Bullets validation
    raw_bullets = raw_slide.get("bullets", [])
    if isinstance(raw_bullets, str):
        raw_bullets = [raw_bullets]
    elif not isinstance(raw_bullets, list):
        # Could be under 'content' in older format
        alt_content = raw_slide.get("content", [])
        raw_bullets = alt_content if isinstance(alt_content, list) else [str(alt_content)]

    cleaned_bullets = [
        sanitize_text(b, max_len=200)
        for b in raw_bullets
        if b and str(b).strip()
    ]

    # Ensure at least 1-2 fallback bullets if non-title layout and empty
    if not cleaned_bullets and layout not in ["title", "section_header", "ending"]:
        cleaned_bullets = [
            f"Key overview regarding {title}",
            "Core concept and practical application",
            "Next steps and future developments"
        ]

    # Handle Columns for two_column
    columns = None
    if layout == "two_column" or "columns" in raw_slide:
        raw_cols = raw_slide.get("columns", {})
        if isinstance(raw_cols, dict):
            c1_bullets = [sanitize_text(b) for b in raw_cols.get("col1_bullets", []) if b]
            c2_bullets = [sanitize_text(b) for b in raw_cols.get("col2_bullets", []) if b]
            columns = ColumnData(
                col1_title=sanitize_text(raw_cols.get("col1_title", "Perspective A")),
                col1_bullets=c1_bullets if c1_bullets else cleaned_bullets[:len(cleaned_bullets)//2 or 1],
                col2_title=sanitize_text(raw_cols.get("col2_title", "Perspective B")),
                col2_bullets=c2_bullets if c2_bullets else cleaned_bullets[len(cleaned_bullets)//2 or 1:]
            )

    # Handle Stats / KPIs
    stats = None
    if layout == "stats_kpi" or "stats" in raw_slide:
        raw_stats = raw_slide.get("stats", [])
        if isinstance(raw_stats, list) and raw_stats:
            stats_list = []
            for item in raw_stats:
                if isinstance(item, dict):
                    stats_list.append(KpiMetric(
                        label=sanitize_text(item.get("label", "Key Metric"), max_len=60),
                        value=sanitize_text(item.get("value", "100+"), max_len=30),
                        detail=sanitize_text(item.get("detail", ""), max_len=80)
                    ))
            stats = stats_list if stats_list else None

    # Handle Table
    table_data = None
    if layout == "table" or "table_data" in raw_slide:
        raw_tbl = raw_slide.get("table_data", {})
        if isinstance(raw_tbl, dict):
            headers = [sanitize_text(h, max_len=50) for h in raw_tbl.get("headers", [])]
            raw_rows = raw_tbl.get("rows", [])
            rows = []
            for r in raw_rows:
                if isinstance(r, list):
                    rows.append([sanitize_text(cell, max_len=100) for cell in r])
            if headers and rows:
                table_data = TableData(headers=headers, rows=rows)

    # Handle Chart
    chart_data = None
    if layout == "chart" or "chart_data" in raw_slide:
        raw_chart = raw_slide.get("chart_data", {})
        if isinstance(raw_chart, dict):
            c_type = sanitize_text(raw_chart.get("chart_type", "column")).lower()
            if c_type not in ["column", "bar", "line", "pie"]:
                c_type = "column"
            categories = [sanitize_text(cat, max_len=40) for cat in raw_chart.get("categories", [])]
            raw_series = raw_chart.get("series", [])
            series_list = []
            for s in raw_series:
                if isinstance(s, dict):
                    vals = s.get("values", [])
                    num_vals = []
                    for v in vals:
                        try:
                            num_vals.append(float(v))
                        except (ValueError, TypeError):
                            num_vals.append(0.0)
                    if num_vals:
                        series_list.append(ChartSeries(
                            name=sanitize_text(s.get("name", "Metric"), max_len=40),
                            values=num_vals
                        ))
            if categories and series_list:
                chart_data = ChartData(
                    chart_type=c_type,
                    title=sanitize_text(raw_chart.get("title", title)),
                    categories=categories,
                    series=series_list
                )

    # Handle Process Steps
    process_steps = None
    if layout == "process_flow" or "process_steps" in raw_slide:
        raw_steps = raw_slide.get("process_steps", [])
        if isinstance(raw_steps, list) and raw_steps:
            steps_list = []
            for i, stp in enumerate(raw_steps):
                if isinstance(stp, dict):
                    steps_list.append(ProcessStep(
                        step_number=int(stp.get("step_number", i + 1)),
                        title=sanitize_text(stp.get("title", f"Step {i + 1}"), max_len=50),
                        description=sanitize_text(stp.get("description", ""), max_len=150)
                    ))
            process_steps = steps_list if steps_list else None

    # Visual suggestions & Speaker notes
    visual_description = sanitize_text(raw_slide.get("visual_description", ""), max_len=250)
    image_query = sanitize_text(raw_slide.get("image_query", title), max_len=60)
    speaker_notes = sanitize_text(raw_slide.get("speaker_notes", ""), max_len=1000)

    return SlideContent(
        slide_id=index + 1,
        title=title,
        layout=layout,
        key_message=key_message,
        bullets=cleaned_bullets,
        columns=columns,
        stats=stats,
        table_data=table_data,
        chart_data=chart_data,
        process_steps=process_steps,
        visual_description=visual_description,
        image_query=image_query,
        speaker_notes=speaker_notes
    )


def validate_presentation_data(
    parsed_json: Dict[str, Any],
    requested_slides: int,
    topic: str,
    include_toc: bool = True,
    include_conclusion: bool = True,
    include_references: bool = False,
    include_title_slide: bool = True,
    include_ending_slide: bool = True
) -> PresentationData:
    """Validate, sanitize, and adapt a parsed JSON dict into a verified PresentationData model.

    Enforces slide counts, handles missing components, and ensures
    required structure is completely fulfilled.
    """
    title = sanitize_text(parsed_json.get("title", topic or "Presentation"), max_len=120)
    if not title:
        title = topic or "Untitled Presentation"

    subtitle = sanitize_text(parsed_json.get("subtitle", f"A Comprehensive Overview of {title}"), max_len=180)
    overview = sanitize_text(parsed_json.get("overview", ""), max_len=400)
    target_audience = sanitize_text(parsed_json.get("target_audience", "General Audience"), max_len=100)

    raw_objectives = parsed_json.get("key_objectives", [])
    if isinstance(raw_objectives, list):
        key_objectives = [sanitize_text(obj, max_len=120) for obj in raw_objectives if obj]
    else:
        key_objectives = [sanitize_text(raw_objectives, max_len=120)] if raw_objectives else []

    raw_slides = parsed_json.get("slides", [])
    if not isinstance(raw_slides, list):
        raw_slides = []

    validated_slides: List[SlideContent] = []
    for i, slide_dict in enumerate(raw_slides):
        if isinstance(slide_dict, dict):
            validated_slides.append(validate_slide_dict(slide_dict, i, title))

    # Adjust slide count to requested_slides
    # If the user requested N slides, ensure the generated deck matches N
    # 1. Title slide check
    has_title_slide = any(s.layout == "title" for s in validated_slides)
    if include_title_slide and not has_title_slide:
        title_slide = SlideContent(
            slide_id=1,
            title=title,
            layout="title",
            key_message=subtitle,
            bullets=[subtitle],
            speaker_notes=f"Welcome everyone. Today we are presenting on {title}."
        )
        validated_slides.insert(0, title_slide)
    elif not include_title_slide and has_title_slide:
        validated_slides = [s for s in validated_slides if s.layout != "title"]

    # 2. Table of contents / Agenda
    has_agenda = any(s.layout == "agenda" for s in validated_slides)
    if include_toc and not has_agenda:
        # Build agenda topics from other slides
        agenda_items = [s.title for s in validated_slides if s.layout not in ["title", "agenda", "ending"]][:6]
        if not agenda_items:
            agenda_items = ["Overview & Context", "Key Concepts", "Core Analysis", "Future Outlook"]
        agenda_slide = SlideContent(
            slide_id=2,
            title="Agenda & Key Topics",
            layout="agenda",
            key_message="Roadmap of key topics covered in this presentation.",
            bullets=agenda_items,
            speaker_notes="Here is an overview of the key topics we will be exploring today."
        )
        insert_idx = 1 if include_title_slide else 0
        validated_slides.insert(insert_idx, agenda_slide)

    # 3. Conclusion slide
    has_conclusion = any(s.layout == "conclusion" for s in validated_slides)
    if include_conclusion and not has_conclusion:
        conclusion_slide = SlideContent(
            slide_id=len(validated_slides) + 1,
            title="Conclusion & Key Takeaways",
            layout="conclusion",
            key_message="Summarizing core insights and future outlook.",
            bullets=[
                "Synthesized primary concepts and practical significance.",
                "Demonstrated actionable impact across key focus areas.",
                "Identified opportunities for continued growth and innovation."
            ],
            speaker_notes="To summarize our key takeaways, here are the core points to remember."
        )
        validated_slides.append(conclusion_slide)

    # 4. References slide
    has_references = any(s.layout == "references" for s in validated_slides)
    if include_references and not has_references:
        ref_slide = SlideContent(
            slide_id=len(validated_slides) + 1,
            title="References & Further Reading",
            layout="references",
            key_message="Citations, foundational research, and authoritative resources.",
            bullets=[
                f"Authoritative research & standards on {title}.",
                "Industry benchmarks, whitepapers, and technical documentation.",
                "Note: Please verify external citations independently."
            ],
            speaker_notes="Here are recommended references and sources for further study."
        )
        validated_slides.append(ref_slide)

    # 5. Ending slide
    has_ending = any(s.layout == "ending" for s in validated_slides)
    if include_ending_slide and not has_ending:
        ending_slide = SlideContent(
            slide_id=len(validated_slides) + 1,
            title="Thank You",
            layout="ending",
            key_message="Questions & Discussion",
            bullets=[
                f"Thank you for attending this session on {title}.",
                "We welcome any questions, thoughts, and discussion points.",
                "Contact: Connect via team channels or presentation resources."
            ],
            speaker_notes="Thank you for your time and engagement. I'd now like to open the floor to questions."
        )
        validated_slides.append(ending_slide)
    elif not include_ending_slide and has_ending:
        validated_slides = [s for s in validated_slides if s.layout != "ending"]

    # Trim or pad to requested_slides if different
    # Keep title at start and ending at end if present
    target_count = max(3, min(30, requested_slides))

    if len(validated_slides) > target_count:
        # Keep title at index 0 and ending at index -1 if present
        first = validated_slides[0] if validated_slides and validated_slides[0].layout == "title" else None
        last = validated_slides[-1] if validated_slides and validated_slides[-1].layout == "ending" else None

        middle = [s for s in validated_slides if s not in (first, last)]
        needed_middle = target_count - (1 if first else 0) - (1 if last else 0)
        selected_middle = middle[:max(1, needed_middle)]

        validated_slides = []
        if first:
            validated_slides.append(first)
        validated_slides.extend(selected_middle)
        if last:
            validated_slides.append(last)

    elif len(validated_slides) < target_count:
        # Pad with relevant content slides
        pad_needed = target_count - len(validated_slides)
        ending_slide_obj = None
        if validated_slides and validated_slides[-1].layout == "ending":
            ending_slide_obj = validated_slides.pop()

        for p in range(pad_needed):
            curr_idx = len(validated_slides) + 1
            padded = SlideContent(
                slide_id=curr_idx,
                title=f"{title}: Focus Dimension {p + 1}",
                layout="bullet_list",
                key_message=f"Deepening exploration of core dimension {p + 1}.",
                bullets=[
                    f"Examining foundational aspects of {title} in practice",
                    "Analyzing operational drivers and key implementation factors",
                    "Addressing challenges and capitalizing on strategic advantages"
                ],
                speaker_notes=f"Let's now dive deeper into dimension {p + 1} of {title}."
            )
            validated_slides.append(padded)

        if ending_slide_obj:
            validated_slides.append(ending_slide_obj)

    # Renumber slide IDs sequentially
    for idx, s in enumerate(validated_slides):
        s.slide_id = idx + 1

    return PresentationData(
        title=title,
        subtitle=subtitle,
        overview=overview,
        target_audience=target_audience,
        key_objectives=key_objectives,
        slides=validated_slides,
        metadata={
            "requested_slides": requested_slides,
            "actual_slides": len(validated_slides),
            "topic": topic
        }
    )


def parse_and_validate_response(
    raw_response: str,
    requested_slides: int,
    topic: str,
    include_toc: bool = True,
    include_conclusion: bool = True,
    include_references: bool = False,
    include_title_slide: bool = True,
    include_ending_slide: bool = True
) -> Tuple[Optional[PresentationData], Optional[str]]:
    """Parse raw LLM response text into a validated PresentationData object.

    Returns:
        (PresentationData, error_message)
    """
    if not raw_response or not raw_response.strip():
        return None, "Empty response received from AI model."

    json_str = extract_json_from_text(raw_response)
    if not json_str:
        return None, "No valid JSON structure found in AI response."

    parsed = None
    parse_error = None

    # First attempt: standard json.loads
    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        parse_error = str(e)
        # Second attempt: repair common syntax flaws
        try:
            repaired_str = repair_common_json_issues(json_str)
            parsed = json.loads(repaired_str)
            parse_error = None
        except json.JSONDecodeError as e2:
            parse_error = f"JSON parsing failed: {e2}"

    if parsed is None or not isinstance(parsed, dict):
        return None, f"Could not parse valid JSON object: {parse_error}"

    try:
        validated = validate_presentation_data(
            parsed_json=parsed,
            requested_slides=requested_slides,
            topic=topic,
            include_toc=include_toc,
            include_conclusion=include_conclusion,
            include_references=include_references,
            include_title_slide=include_title_slide,
            include_ending_slide=include_ending_slide
        )
        return validated, None
    except Exception as e:
        logger.exception("Error validating presentation schema")
        return None, f"Schema validation failed: {str(e)}"

