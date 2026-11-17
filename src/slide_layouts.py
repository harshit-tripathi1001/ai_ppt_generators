"""Slide layout rendering engine using python-pptx.

Implements professionally designed, accessible, and editable presentation slide layouts:
- Title Slide (Hero banner, tags, metadata, optional logo)
- Agenda / Table of Contents (Numbered grid cards)
- Title & Bullet Points (Styled cards with bullet icons)
- Two-Column Comparison (Split cards with headers)
- Statistics / KPI Cards (Large metric displays with subtitles)
- Image & Text (Visual asset + descriptive content)
- Process / Timeline Flow (Step sequences with connecting chevron cards)
- Genuine PowerPoint Tables (Styled headers, alternating rows)
- Genuine PowerPoint Charts (Column, Bar, Pie, Line charts)
- Section Divider (High-contrast full-bleed accent slide)
- Conclusion & Key Takeaways (Summary cards + action banner)
- References & Citations (Citation cards + disclaimer)
- Ending Slide (Thank You / Q&A layout)
"""

import io
from typing import Optional, List
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

from src.content_schema import SlideContent
from src.theme_manager import ThemePalette


class LayoutRenderer:
    """Renderer for slide layouts adhering to the selected theme and aspect ratio."""

    def __init__(
        self,
        presentation,
        theme: ThemePalette,
        font_name: str = "Calibri",
        font_size_base: int = 22,
        is_widescreen: bool = True,
        logo_bytes: Optional[bytes] = None
    ):
        self.prs = presentation
        self.theme = theme
        self.font_name = font_name
        self.font_size_base = font_size_base
        self.is_widescreen = is_widescreen
        self.logo_bytes = logo_bytes

        # Dimensions
        self.width = Inches(13.333) if is_widescreen else Inches(10.0)
        self.height = Inches(7.5)

        # Scale factor for 4:3 vs 16:9
        self.scale_x = 1.0 if is_widescreen else (10.0 / 13.333)

    def _add_background(self, slide):
        """Draw full slide background rectangle to guarantee theme color fidelity."""
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            0, 0, self.width, self.height
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = self.theme.bg_color
        bg_shape.line.fill.background()  # No border

    def _add_header(self, slide, title_text: str, category_tag: str = ""):
        """Standard slide header with title, accent bar, optional category, and optional logo."""
        margin_left = Inches(0.8 * self.scale_x)
        top = Inches(0.45)
        content_width = self.width - margin_left - Inches(1.0 * self.scale_x)

        # Category pill if provided
        if category_tag:
            pill = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                margin_left, top, Inches(1.8 * self.scale_x), Inches(0.32)
            )
            pill.fill.solid()
            pill.fill.fore_color.rgb = self.theme.primary
            pill.line.fill.background()
            tf_pill = pill.text_frame
            tf_pill.word_wrap = False
            p_pill = tf_pill.paragraphs[0]
            p_pill.text = category_tag.upper()
            p_pill.font.name = self.font_name
            p_pill.font.size = Pt(10)
            p_pill.font.bold = True
            p_pill.font.color.rgb = RGBColor(255, 255, 255)
            p_pill.alignment = PP_ALIGN.CENTER
            top += Inches(0.4)

        # Slide Title
        title_box = slide.shapes.add_textbox(
            margin_left, top, content_width - Inches(2.0), Inches(0.85)
        )
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = self.font_name
        p.font.size = Pt(self.font_size_base + 6)
        p.font.bold = True
        p.font.color.rgb = self.theme.title_text

        # Accent line under title
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            margin_left, top + Inches(0.78), Inches(1.6 * self.scale_x), Inches(0.04)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = self.theme.accent_bar
        line.line.fill.background()

        # Logo in top right if provided
        if self.logo_bytes:
            try:
                logo_stream = io.BytesIO(self.logo_bytes)
                logo_width = Inches(1.4 * self.scale_x)
                logo_left = self.width - logo_width - Inches(0.8 * self.scale_x)
                slide.shapes.add_picture(logo_stream, logo_left, Inches(0.4), width=logo_width)
            except Exception:
                pass

    def _add_footer(self, slide, current_slide: int, total_slides: int, include_slide_numbers: bool, topic: str):
        """Add subtle bottom footer with topic title and slide numbers."""
        bottom = self.height - Inches(0.5)
        margin_left = Inches(0.8 * self.scale_x)

        # Topic tag on bottom left
        if topic:
            left_box = slide.shapes.add_textbox(margin_left, bottom, Inches(6.0 * self.scale_x), Inches(0.35))
            tf_left = left_box.text_frame
            tf_left.margin_left = tf_left.margin_top = 0
            p_left = tf_left.paragraphs[0]
            p_left.text = topic
            p_left.font.name = self.font_name
            p_left.font.size = Pt(10)
            p_left.font.color.rgb = self.theme.muted_text

        # Slide number on bottom right
        if include_slide_numbers and total_slides > 0:
            num_width = Inches(2.0 * self.scale_x)
            num_left = self.width - num_width - Inches(0.8 * self.scale_x)
            right_box = slide.shapes.add_textbox(num_left, bottom, num_width, Inches(0.35))
            tf_right = right_box.text_frame
            tf_right.margin_right = tf_right.margin_top = 0
            p_right = tf_right.paragraphs[0]
            p_right.text = f"{current_slide} / {total_slides}"
            p_right.font.name = self.font_name
            p_right.font.size = Pt(10)
            p_right.font.color.rgb = self.theme.muted_text
            p_right.alignment = PP_ALIGN.RIGHT

    def _attach_speaker_notes(self, slide, notes_text: str):
        """Safely attach speaker notes to the slide."""
        if not notes_text:
            return
        try:
            notes_slide = slide.notes_slide
            tf = notes_slide.notes_text_frame
            tf.text = notes_text
        except Exception:
            pass

    # =========================================================================
    # LAYOUT 1: TITLE SLIDE
    # =========================================================================
    def render_title_slide(self, slide_data: SlideContent, presentation_title: str, subtitle: str, audience: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)

        # Decorative left accent stripe or card
        stripe_width = Inches(0.35 * self.scale_x)
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, stripe_width, self.height)
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = self.theme.accent_bar
        stripe.line.fill.background()

        # Center hero card
        card_width = self.width - Inches(2.2 * self.scale_x)
        card_height = Inches(5.2)
        card_left = Inches(1.1 * self.scale_x)
        card_top = Inches(1.15)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, card_top, card_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = self.theme.card_bg
        card.line.color.rgb = self.theme.card_border
        card.line.width = Pt(1.5)

        # Optional Top Banner inside card
        banner_height = Inches(0.08)
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_left, card_top, card_width, banner_height)
        banner.fill.solid()
        banner.fill.fore_color.rgb = self.theme.primary
        banner.line.fill.background()

        # Logo on Title slide if uploaded
        if self.logo_bytes:
            try:
                logo_stream = io.BytesIO(self.logo_bytes)
                slide.shapes.add_picture(logo_stream, card_left + Inches(0.6), card_top + Inches(0.5), height=Inches(0.8))
            except Exception:
                pass

        # Audience Pill
        if audience:
            pill_top = card_top + (Inches(1.5) if self.logo_bytes else Inches(0.7))
            pill = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                card_left + Inches(0.6), pill_top, Inches(2.6 * self.scale_x), Inches(0.35)
            )
            pill.fill.solid()
            pill.fill.fore_color.rgb = self.theme.primary
            pill.line.fill.background()
            p = pill.text_frame.paragraphs[0]
            p.text = f"FOR: {audience.upper()}"
            p.font.name = self.font_name
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            text_top = pill_top + Inches(0.55)
        else:
            text_top = card_top + (Inches(1.5) if self.logo_bytes else Inches(0.8))

        # Title Textbox
        tb = slide.shapes.add_textbox(card_left + Inches(0.6), text_top, card_width - Inches(1.2), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p_title = tf.paragraphs[0]
        p_title.text = slide_data.title or presentation_title
        p_title.font.name = self.font_name
        p_title.font.size = Pt(self.font_size_base + 16)
        p_title.font.bold = True
        p_title.font.color.rgb = self.theme.title_text

        # Subtitle
        sub_text = slide_data.key_message or subtitle or (slide_data.bullets[0] if slide_data.bullets else "")
        if sub_text:
            p_sub = tf.add_paragraph()
            p_sub.text = sub_text
            p_sub.font.name = self.font_name
            p_sub.font.size = Pt(self.font_size_base - 2)
            p_sub.font.color.rgb = self.theme.muted_text
            p_sub.space_before = Pt(12)

        # Footer inside card
        brand_box = slide.shapes.add_textbox(
            card_left + Inches(0.6), card_top + card_height - Inches(0.7), card_width - Inches(1.2), Inches(0.4)
        )
        p_brand = brand_box.text_frame.paragraphs[0]
        p_brand.text = "Generated with AI PPT Generator"
        p_brand.font.name = self.font_name
        p_brand.font.size = Pt(11)
        p_brand.font.color.rgb = self.theme.muted_text

        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 2: AGENDA / TABLE OF CONTENTS
    # =========================================================================
    def render_agenda_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title or "Table of Contents", "Overview")

        items = slide_data.bullets[:6] if slide_data.bullets else ["Introduction", "Core Framework", "Practical Insights", "Future Direction"]
        count = len(items)

        # Grid calculation: 2 columns
        start_top = Inches(1.9)
        margin_left = Inches(0.8 * self.scale_x)
        available_width = self.width - margin_left * 2
        col_width = (available_width - Inches(0.4 * self.scale_x)) / 2
        row_height = Inches(1.25)

        for i, item in enumerate(items):
            col_idx = i % 2
            row_idx = i // 2
            card_left = margin_left + col_idx * (col_width + Inches(0.4 * self.scale_x))
            card_top = start_top + row_idx * (row_height + Inches(0.3))

            # Agenda Item Card
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, card_top, col_width, row_height)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme.card_bg
            card.line.color.rgb = self.theme.card_border

            # Number badge
            badge_size = Inches(0.65)
            badge = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                card_left + Inches(0.2), card_top + (row_height - badge_size) / 2, badge_size, badge_size
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = self.theme.primary
            badge.line.fill.background()
            p_badge = badge.text_frame.paragraphs[0]
            p_badge.text = f"{i + 1:02d}"
            p_badge.font.name = self.font_name
            p_badge.font.size = Pt(16)
            p_badge.font.bold = True
            p_badge.font.color.rgb = RGBColor(255, 255, 255)
            p_badge.alignment = PP_ALIGN.CENTER

            # Text box
            tb = slide.shapes.add_textbox(
                card_left + Inches(1.0), card_top + Inches(0.15), col_width - Inches(1.2), row_height - Inches(0.3)
            )
            tf = tb.text_frame
            tf.word_wrap = True
            p_text = tf.paragraphs[0]
            p_text.text = item
            p_text.font.name = self.font_name
            p_text.font.size = Pt(self.font_size_base - 4)
            p_text.font.bold = True
            p_text.font.color.rgb = self.theme.title_text

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 3: BULLET LIST (TITLE AND CONTENT)
    # =========================================================================
    def render_bullet_list_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title, "Core Analysis")

        margin_left = Inches(0.8 * self.scale_x)
        content_width = self.width - margin_left * 2
        start_top = Inches(1.85)

        # Key message banner if present
        if slide_data.key_message:
            key_banner = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                margin_left, start_top, content_width, Inches(0.65)
            )
            key_banner.fill.solid()
            key_banner.fill.fore_color.rgb = self.theme.card_bg
            key_banner.line.color.rgb = self.theme.primary
            key_banner.line.width = Pt(1.5)

            p_key = key_banner.text_frame.paragraphs[0]
            p_key.text = f"💡 {slide_data.key_message}"
            p_key.font.name = self.font_name
            p_key.font.size = Pt(self.font_size_base - 5)
            p_key.font.bold = True
            p_key.font.color.rgb = self.theme.primary
            start_top += Inches(0.85)

        # Bullets as structured cards
        bullets = slide_data.bullets[:5] or ["Insight point 1", "Insight point 2", "Insight point 3"]
        available_height = self.height - start_top - Inches(0.7)
        card_h = min(Inches(0.9), (available_height - (len(bullets) - 1) * Inches(0.18)) / len(bullets))

        for i, bullet in enumerate(bullets):
            card_top = start_top + i * (card_h + Inches(0.18))

            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                margin_left, card_top, content_width, card_h
            )
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme.card_bg
            card.line.color.rgb = self.theme.card_border

            # Bullet dot / accent indicator
            dot = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                margin_left + Inches(0.25), card_top + (card_h - Inches(0.22)) / 2, Inches(0.22), Inches(0.22)
            )
            dot.fill.solid()
            dot.fill.fore_color.rgb = self.theme.accent_bar
            dot.line.fill.background()

            # Text
            tb = slide.shapes.add_textbox(
                margin_left + Inches(0.65), card_top + Inches(0.08), content_width - Inches(0.85), card_h - Inches(0.16)
            )
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = bullet
            p.font.name = self.font_name
            p.font.size = Pt(self.font_size_base - 4)
            p.font.color.rgb = self.theme.body_text

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 4: TWO-COLUMN COMPARISON
    # =========================================================================
    def render_two_column_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title, "Comparison")

        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        col_gap = Inches(0.4 * self.scale_x)
        col_w = (total_w - col_gap) / 2
        top = Inches(1.85)
        h = self.height - top - Inches(0.8)

        # Extract columns data
        c1_title = "Perspective 1"
        c2_title = "Perspective 2"
        c1_bullets = []
        c2_bullets = []

        if slide_data.columns:
            c1_title = slide_data.columns.col1_title or c1_title
            c2_title = slide_data.columns.col2_title or c2_title
            c1_bullets = slide_data.columns.col1_bullets
            c2_bullets = slide_data.columns.col2_bullets
        elif slide_data.bullets:
            half = max(1, len(slide_data.bullets) // 2)
            c1_bullets = slide_data.bullets[:half]
            c2_bullets = slide_data.bullets[half:]

        columns_data = [
            (c1_title, c1_bullets, margin_left, self.theme.primary),
            (c2_title, c2_bullets, margin_left + col_w + col_gap, self.theme.secondary)
        ]

        for col_t, col_b, col_x, accent_col in columns_data:
            # Column Box
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_x, top, col_w, h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme.card_bg
            card.line.color.rgb = self.theme.card_border

            # Header Banner inside column
            hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_x, top, col_w, Inches(0.65))
            hdr.fill.solid()
            hdr.fill.fore_color.rgb = accent_col
            hdr.line.fill.background()
            p_hdr = hdr.text_frame.paragraphs[0]
            p_hdr.text = col_t
            p_hdr.font.name = self.font_name
            p_hdr.font.size = Pt(self.font_size_base - 4)
            p_hdr.font.bold = True
            p_hdr.font.color.rgb = RGBColor(255, 255, 255)
            p_hdr.alignment = PP_ALIGN.CENTER

            # Column Bullets
            tb = slide.shapes.add_textbox(col_x + Inches(0.3), top + Inches(0.85), col_w - Inches(0.6), h - Inches(1.0))
            tf = tb.text_frame
            tf.word_wrap = True

            for idx, b_item in enumerate(col_b[:5]):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                p.text = f"•  {b_item}"
                p.font.name = self.font_name
                p.font.size = Pt(self.font_size_base - 5)
                p.font.color.rgb = self.theme.body_text
                p.space_after = Pt(10)

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 5: STATS / KPI CARDS
    # =========================================================================
    def render_stats_kpi_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title, "Key Metrics")

        stats = slide_data.stats or [
            {"value": "99.8%", "label": "System Reliability", "detail": "Measured across production workflows"},
            {"value": "10x", "label": "Performance Scale", "detail": "Accelerated output generation"},
            {"value": "45%", "label": "Efficiency Gain", "detail": "Operational overhead reduction"}
        ]

        num_cards = min(4, len(stats))
        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        card_gap = Inches(0.3 * self.scale_x)
        card_w = (total_w - (num_cards - 1) * card_gap) / num_cards
        card_h = Inches(3.6)
        card_top = Inches(2.2)

        for i in range(num_cards):
            item = stats[i]
            val = item.value if hasattr(item, "value") else item.get("value", "100+")
            lbl = item.label if hasattr(item, "label") else item.get("label", "Metric")
            det = item.detail if hasattr(item, "detail") else item.get("detail", "")

            cx = margin_left + i * (card_w + card_gap)

            # Card Container
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, card_top, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme.card_bg
            card.line.color.rgb = self.theme.card_border

            # Top accent bar on each card
            accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, card_top, card_w, Inches(0.08))
            accent_line.fill.solid()
            accent_line.fill.fore_color.rgb = self.theme.accent_bar
            accent_line.line.fill.background()

            # KPI Value (Large bold display)
            tb = slide.shapes.add_textbox(cx + Inches(0.2), card_top + Inches(0.4), card_w - Inches(0.4), card_h - Inches(0.6))
            tf = tb.text_frame
            tf.word_wrap = True

            p_val = tf.paragraphs[0]
            p_val.text = str(val)
            p_val.font.name = self.font_name
            p_val.font.size = Pt(self.font_size_base + 18)
            p_val.font.bold = True
            p_val.font.color.rgb = self.theme.primary
            p_val.alignment = PP_ALIGN.CENTER

            # Metric Label
            p_lbl = tf.add_paragraph()
            p_lbl.text = str(lbl)
            p_lbl.font.name = self.font_name
            p_lbl.font.size = Pt(self.font_size_base - 4)
            p_lbl.font.bold = True
            p_lbl.font.color.rgb = self.theme.title_text
            p_lbl.alignment = PP_ALIGN.CENTER
            p_lbl.space_before = Pt(8)

            # Detail subtext
            if det:
                p_det = tf.add_paragraph()
                p_det.text = str(det)
                p_det.font.name = self.font_name
                p_det.font.size = Pt(self.font_size_base - 8)
                p_det.font.color.rgb = self.theme.muted_text
                p_det.alignment = PP_ALIGN.CENTER
                p_det.space_before = Pt(6)

        # Bullets / takeaway underneath if bullets exist
        if slide_data.bullets:
            bot_box = slide.shapes.add_textbox(
                margin_left, card_top + card_h + Inches(0.2), total_w, Inches(0.6)
            )
            tf_b = bot_box.text_frame
            p_b = tf_b.paragraphs[0]
            p_b.text = f"Summary: {slide_data.bullets[0]}"
            p_b.font.name = self.font_name
            p_b.font.size = Pt(self.font_size_base - 6)
            p_b.font.color.rgb = self.theme.muted_text
            p_b.alignment = PP_ALIGN.CENTER

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 6: CONCEPT / FRAMEWORK CARD SLIDE
    # =========================================================================
    def render_image_text_slide(
        self,
        slide_data: SlideContent,
        image_result: Optional[Any] = None,
        current_idx: int = 1,
        total_slides: int = 1,
        topic: str = ""
    ):
        """Render a clean two-panel concept and analysis slide using native PowerPoint shapes."""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title, "Core Framework")

        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        gap = Inches(0.4 * self.scale_x)
        col_w = (total_w - gap) / 2
        top = Inches(1.85)
        h = self.height - top - Inches(0.8)

        # Left Column: Native Concept Architecture Card
        left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, margin_left, top, col_w, h)
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = self.theme.card_bg
        left_card.line.color.rgb = self.theme.card_border

        # Top banner on concept card
        banner_h = Inches(0.65)
        banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, margin_left, top, col_w, banner_h)
        banner.fill.solid()
        banner.fill.fore_color.rgb = self.theme.primary
        banner.line.fill.background()
        p_b = banner.text_frame.paragraphs[0]
        p_b.text = "📌 CONCEPT BLUEPRINT"
        p_b.font.name = self.font_name
        p_b.font.size = Pt(12)
        p_b.font.bold = True
        p_b.font.color.rgb = RGBColor(255, 255, 255)
        p_b.alignment = PP_ALIGN.CENTER

        # Concept center graphic container
        center_shape = slide.shapes.add_shape(
            MSO_SHAPE.DIAMOND,
            margin_left + (col_w - Inches(1.8)) / 2,
            top + Inches(1.1),
            Inches(1.8),
            Inches(1.8)
        )
        center_shape.fill.solid()
        center_shape.fill.fore_color.rgb = self.theme.secondary
        center_shape.line.fill.background()

        # Concept Description Textbox
        tb_concept = slide.shapes.add_textbox(
            margin_left + Inches(0.3),
            top + Inches(3.1),
            col_w - Inches(0.6),
            h - Inches(3.3)
        )
        tf_c = tb_concept.text_frame
        tf_c.word_wrap = True
        p_desc = tf_c.paragraphs[0]
        p_desc.text = slide_data.visual_description or slide_data.key_message or "System architecture and conceptual foundation."
        p_desc.font.name = self.font_name
        p_desc.font.size = Pt(self.font_size_base - 5)
        p_desc.font.color.rgb = self.theme.body_text
        p_desc.alignment = PP_ALIGN.CENTER

        # Right Column: Content card with bullets
        right_x = margin_left + col_w + gap
        right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, top, col_w, h)
        right_card.fill.solid()
        right_card.fill.fore_color.rgb = self.theme.card_bg
        right_card.line.color.rgb = self.theme.card_border

        tb = slide.shapes.add_textbox(right_x + Inches(0.35), top + Inches(0.3), col_w - Inches(0.7), h - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True

        if slide_data.key_message:
            p_msg = tf.paragraphs[0]
            p_msg.text = slide_data.key_message
            p_msg.font.name = self.font_name
            p_msg.font.size = Pt(self.font_size_base - 3)
            p_msg.font.bold = True
            p_msg.font.color.rgb = self.theme.primary
            p_msg.space_after = Pt(14)
            first_bullet = False
        else:
            first_bullet = True

        for i, bullet in enumerate(slide_data.bullets[:5]):
            p = tf.paragraphs[0] if first_bullet and i == 0 else tf.add_paragraph()
            p.text = f"•  {bullet}"
            p.font.name = self.font_name
            p.font.size = Pt(self.font_size_base - 5)
            p.font.color.rgb = self.theme.body_text
            p.space_after = Pt(10)

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    def _draw_vector_fallback(self, slide, x, y, w, h, visual_desc: str):
        """Draw an attractive native vector illustration/concept box as fallback."""
        inner_box = slide.shapes.add_shape(
            MSO_SHAPE.DIAMOND,
            x + (w - Inches(1.8)) / 2, y + Inches(0.8), Inches(1.8), Inches(1.8)
        )
        inner_box.fill.solid()
        inner_box.fill.fore_color.rgb = self.theme.primary
        inner_box.line.fill.background()

        tb = slide.shapes.add_textbox(x + Inches(0.3), y + Inches(2.9), w - Inches(0.6), Inches(1.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = "CONCEPT DIAGRAM"
        p1.font.name = self.font_name
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = self.theme.primary
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = visual_desc or "Interactive visual architectural blueprint and conceptual framework."
        p2.font.name = self.font_name
        p2.font.size = Pt(self.font_size_base - 7)
        p2.font.color.rgb = self.theme.muted_text
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(6)

    # =========================================================================
    # LAYOUT 7: PROCESS / TIMELINE FLOW
    # =========================================================================
    def render_process_flow_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title, "Process Flow")

        steps = slide_data.process_steps or [
            {"step_number": 1, "title": "Initiation", "description": "Formulate requirements and objectives."},
            {"step_number": 2, "title": "Execution", "description": "Deploy architecture and core models."},
            {"step_number": 3, "title": "Verification", "description": "Rigorous testing and metric benchmarking."},
            {"step_number": 4, "title": "Deployment", "description": "Rollout to production environments."}
        ]

        num_steps = min(5, len(steps))
        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        gap = Inches(0.25 * self.scale_x)
        step_w = (total_w - (num_steps - 1) * gap) / num_steps
        step_h = Inches(3.8)
        top = Inches(2.1)

        for i in range(num_steps):
            stp = steps[i]
            s_num = stp.step_number if hasattr(stp, "step_number") else stp.get("step_number", i + 1)
            s_title = stp.title if hasattr(stp, "title") else stp.get("title", f"Step {i + 1}")
            s_desc = stp.description if hasattr(stp, "description") else stp.get("description", "")

            sx = margin_left + i * (step_w + gap)

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, top, step_w, step_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme.card_bg
            card.line.color.rgb = self.theme.card_border

            # Number badge at top of step
            badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, sx + (step_w - Inches(0.7)) / 2, top + Inches(0.25), Inches(0.7), Inches(0.7))
            badge.fill.solid()
            badge.fill.fore_color.rgb = self.theme.primary
            badge.line.fill.background()
            p_badge = badge.text_frame.paragraphs[0]
            p_badge.text = str(s_num)
            p_badge.font.name = self.font_name
            p_badge.font.size = Pt(16)
            p_badge.font.bold = True
            p_badge.font.color.rgb = RGBColor(255, 255, 255)
            p_badge.alignment = PP_ALIGN.CENTER

            # Text inside step card
            tb = slide.shapes.add_textbox(sx + Inches(0.15), top + Inches(1.15), step_w - Inches(0.3), step_h - Inches(1.3))
            tf = tb.text_frame
            tf.word_wrap = True

            p_t = tf.paragraphs[0]
            p_t.text = s_title
            p_t.font.name = self.font_name
            p_t.font.size = Pt(self.font_size_base - 5)
            p_t.font.bold = True
            p_t.font.color.rgb = self.theme.title_text
            p_t.alignment = PP_ALIGN.CENTER

            if s_desc:
                p_d = tf.add_paragraph()
                p_d.text = s_desc
                p_d.font.name = self.font_name
                p_d.font.size = Pt(self.font_size_base - 8)
                p_d.font.color.rgb = self.theme.body_text
                p_d.alignment = PP_ALIGN.CENTER
                p_d.space_before = Pt(8)

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 8: TABLE SLIDE
    # =========================================================================
    def render_table_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title, "Tabular Data")

        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        top = Inches(1.9)

        # Fallback table if none provided
        tbl = slide_data.table_data
        headers = tbl.headers if tbl and tbl.headers else ["Category", "Dimension A", "Dimension B", "Assessment"]
        rows = tbl.rows if tbl and tbl.rows else [
            ["Framework 1", "High Accuracy", "Low Latency", "Recommended"],
            ["Framework 2", "Standard", "Medium", "Viable Alternative"],
            ["Framework 3", "Moderate", "High Throughput", "Specialized"]
        ]

        num_cols = len(headers)
        num_rows = len(rows) + 1
        table_h = min(Inches(4.5), Inches(0.7 * num_rows))

        table_shape = slide.shapes.add_table(num_rows, num_cols, margin_left, top, total_w, table_h)
        table = table_shape.table

        # Style Header Row
        for c_idx, h_text in enumerate(headers):
            cell = table.cell(0, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.theme.primary
            p = cell.text_frame.paragraphs[0]
            p.text = h_text
            p.font.name = self.font_name
            p.font.size = Pt(self.font_size_base - 5)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER

        # Style Body Rows
        for r_idx, row_data in enumerate(rows):
            is_even = (r_idx % 2 == 0)
            row_bg = self.theme.card_bg if is_even else self.theme.bg_color

            for c_idx in range(num_cols):
                cell = table.cell(r_idx + 1, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = row_bg
                p = cell.text_frame.paragraphs[0]
                cell_val = row_data[c_idx] if c_idx < len(row_data) else ""
                p.text = str(cell_val)
                p.font.name = self.font_name
                p.font.size = Pt(self.font_size_base - 7)
                p.font.color.rgb = self.theme.body_text
                p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.CENTER

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 9: CHART SLIDE (GENUINE EDITABLE PPTX CHART)
    # =========================================================================
    def render_chart_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title, "Data Visualization")

        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        top = Inches(1.85)

        # Build Chart Data
        c_data = slide_data.chart_data
        chart_type_str = c_data.chart_type if c_data else "column"
        categories = c_data.categories if c_data and c_data.categories else ["Q1", "Q2", "Q3", "Q4"]
        series_list = c_data.series if c_data and c_data.series else [
            type("Series", (), {"name": "Performance", "values": [35, 60, 75, 95]})()
        ]

        chart_data = CategoryChartData()
        chart_data.categories = categories

        for s in series_list:
            vals = s.values if hasattr(s, "values") else s.get("values", [])
            s_name = s.name if hasattr(s, "name") else s.get("name", "Metric")
            chart_data.add_series(s_name, tuple(vals))

        # Chart type mapping
        type_map = {
            "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "bar": XL_CHART_TYPE.BAR_CLUSTERED,
            "line": XL_CHART_TYPE.LINE_MARKERS,
            "pie": XL_CHART_TYPE.PIE
        }
        xl_type = type_map.get(chart_type_str.lower(), XL_CHART_TYPE.COLUMN_CLUSTERED)

        # Add genuine PowerPoint chart shape
        chart_w = total_w * 0.65
        chart_h = Inches(4.7)
        chart_shape = slide.shapes.add_chart(xl_type, margin_left, top, chart_w, chart_h, chart_data)
        chart = chart_shape.chart

        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.TOP
        chart.legend.include_in_layout = False

        # Right side insight card
        insight_x = margin_left + chart_w + Inches(0.3 * self.scale_x)
        insight_w = total_w - chart_w - Inches(0.3 * self.scale_x)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, insight_x, top, insight_w, chart_h)
        card.fill.solid()
        card.fill.fore_color.rgb = self.theme.card_bg
        card.line.color.rgb = self.theme.card_border

        tb = slide.shapes.add_textbox(insight_x + Inches(0.25), top + Inches(0.3), insight_w - Inches(0.5), chart_h - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p_hdr = tf.paragraphs[0]
        p_hdr.text = "📈 Chart Insights"
        p_hdr.font.name = self.font_name
        p_hdr.font.size = Pt(self.font_size_base - 4)
        p_hdr.font.bold = True
        p_hdr.font.color.rgb = self.theme.primary
        p_hdr.space_after = Pt(12)

        bullets = slide_data.bullets or ["Upward trend observed across all cycles.", "Growth velocity exceeds historical baseline."]
        for b in bullets[:4]:
            p = tf.add_paragraph()
            p.text = f"• {b}"
            p.font.name = self.font_name
            p.font.size = Pt(self.font_size_base - 6)
            p.font.color.rgb = self.theme.body_text
            p.space_after = Pt(8)

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 10: SECTION DIVIDER
    # =========================================================================
    def render_section_header_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])

        # Full-bleed primary theme color background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, self.width, self.height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = self.theme.primary
        bg.line.fill.background()

        # Accent box
        box_w = self.width - Inches(2.5 * self.scale_x)
        box_left = Inches(1.25 * self.scale_x)
        top = Inches(2.2)

        tb = slide.shapes.add_textbox(box_left, top, box_w, Inches(2.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p_num = tf.paragraphs[0]
        p_num.text = f"SECTION {current_idx:02d}"
        p_num.font.name = self.font_name
        p_num.font.size = Pt(14)
        p_num.font.bold = True
        p_num.font.color.rgb = self.theme.secondary
        p_num.alignment = PP_ALIGN.CENTER

        p_t = tf.add_paragraph()
        p_t.text = slide_data.title
        p_t.font.name = self.font_name
        p_t.font.size = Pt(self.font_size_base + 12)
        p_t.font.bold = True
        p_t.font.color.rgb = RGBColor(255, 255, 255)
        p_t.alignment = PP_ALIGN.CENTER
        p_t.space_before = Pt(10)

        if slide_data.key_message:
            p_m = tf.add_paragraph()
            p_m.text = slide_data.key_message
            p_m.font.name = self.font_name
            p_m.font.size = Pt(self.font_size_base - 4)
            p_m.font.color.rgb = RGBColor(230, 230, 230)
            p_m.alignment = PP_ALIGN.CENTER
            p_m.space_before = Pt(12)

        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 11: CONCLUSION SLIDE
    # =========================================================================
    def render_conclusion_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title or "Conclusion & Key Takeaways", "Summary")

        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        top = Inches(1.85)

        # 3 Key Takeaway Cards
        bullets = slide_data.bullets[:3] or [
            "Synthesized primary concepts and actionable insights.",
            "Demonstrated real-world applications and advantages.",
            "Prepared strategic roadmap for future developments."
        ]
        card_w = (total_w - Inches(0.4 * self.scale_x) * 2) / 3
        card_h = Inches(3.2)

        for i, b in enumerate(bullets):
            cx = margin_left + i * (card_w + Inches(0.4 * self.scale_x))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, top, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme.card_bg
            card.line.color.rgb = self.theme.card_border

            # Number badge
            badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx + Inches(0.25), top + Inches(0.25), Inches(0.55), Inches(0.55))
            badge.fill.solid()
            badge.fill.fore_color.rgb = self.theme.primary
            badge.line.fill.background()
            p_badge = badge.text_frame.paragraphs[0]
            p_badge.text = str(i + 1)
            p_badge.font.name = self.font_name
            p_badge.font.size = Pt(14)
            p_badge.font.bold = True
            p_badge.font.color.rgb = RGBColor(255, 255, 255)
            p_badge.alignment = PP_ALIGN.CENTER

            # Text
            tb = slide.shapes.add_textbox(cx + Inches(0.25), top + Inches(0.95), card_w - Inches(0.5), card_h - Inches(1.1))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = b
            p.font.name = self.font_name
            p.font.size = Pt(self.font_size_base - 5)
            p.font.color.rgb = self.theme.body_text

        # Call to Action Bottom Banner
        banner_top = top + card_h + Inches(0.35)
        banner_h = Inches(1.1)
        banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, margin_left, banner_top, total_w, banner_h)
        banner.fill.solid()
        banner.fill.fore_color.rgb = self.theme.card_bg
        banner.line.color.rgb = self.theme.accent_bar
        banner.line.width = Pt(1.5)

        tb_b = slide.shapes.add_textbox(margin_left + Inches(0.3), banner_top + Inches(0.15), total_w - Inches(0.6), Inches(0.8))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        p_call = tf_b.paragraphs[0]
        p_call.text = f"🎯 Strategic Takeaway: {slide_data.key_message or 'Continuous innovation and structured application drive measurable outcomes.'}"
        p_call.font.name = self.font_name
        p_call.font.size = Pt(self.font_size_base - 5)
        p_call.font.bold = True
        p_call.font.color.rgb = self.theme.primary
        p_call.alignment = PP_ALIGN.CENTER

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 12: REFERENCES SLIDE
    # =========================================================================
    def render_references_slide(self, slide_data: SlideContent, current_idx: int, total_slides: int, topic: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)
        self._add_header(slide, slide_data.title or "References & Citations", "Sources")

        margin_left = Inches(0.8 * self.scale_x)
        total_w = self.width - margin_left * 2
        top = Inches(1.85)

        # Disclaimer banner (Transparently acknowledging AI-generated citations)
        disc_h = Inches(0.65)
        disc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, margin_left, top, total_w, disc_h)
        disc.fill.solid()
        disc.fill.fore_color.rgb = self.theme.card_bg
        disc.line.color.rgb = self.theme.card_border
        p_disc = disc.text_frame.paragraphs[0]
        p_disc.text = "ℹ️ Note: References are generated for contextual research and should be verified independently."
        p_disc.font.name = self.font_name
        p_disc.font.size = Pt(11)
        p_disc.font.color.rgb = self.theme.muted_text
        p_disc.alignment = PP_ALIGN.LEFT

        # Reference citation cards
        ref_top = top + disc_h + Inches(0.2)
        refs = slide_data.bullets[:5] or [
            f"Authoritative Whitepaper & Industry Standards on {topic}",
            "Peer-reviewed engineering documentation and academic publications",
            "Official API specifications and reference implementations"
        ]

        card_h = Inches(0.7)
        for i, ref_item in enumerate(refs):
            cy = ref_top + i * (card_h + Inches(0.15))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, margin_left, cy, total_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme.card_bg
            card.line.color.rgb = self.theme.card_border

            tb = slide.shapes.add_textbox(margin_left + Inches(0.2), cy + Inches(0.08), total_w - Inches(0.4), card_h - Inches(0.16))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = f"[{i + 1}]  {ref_item}"
            p.font.name = self.font_name
            p.font.size = Pt(self.font_size_base - 6)
            p.font.color.rgb = self.theme.body_text

        self._add_footer(slide, current_idx, total_slides, True, topic)
        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

    # =========================================================================
    # LAYOUT 13: ENDING SLIDE
    # =========================================================================
    def render_ending_slide(self, slide_data: SlideContent, presentation_title: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self._add_background(slide)

        card_w = self.width - Inches(2.5 * self.scale_x)
        card_left = Inches(1.25 * self.scale_x)
        card_h = Inches(4.8)
        card_top = Inches(1.35)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, card_top, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = self.theme.card_bg
        card.line.color.rgb = self.theme.card_border

        # Top accent bar
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_left, card_top, card_w, Inches(0.08))
        accent.fill.solid()
        accent.fill.fore_color.rgb = self.theme.primary
        accent.line.fill.background()

        tb = slide.shapes.add_textbox(card_left + Inches(0.5), card_top + Inches(0.8), card_w - Inches(1.0), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True

        p_thx = tf.paragraphs[0]
        p_thx.text = slide_data.title or "Thank You!"
        p_thx.font.name = self.font_name
        p_thx.font.size = Pt(self.font_size_base + 16)
        p_thx.font.bold = True
        p_thx.font.color.rgb = self.theme.title_text
        p_thx.alignment = PP_ALIGN.CENTER

        p_sub = tf.add_paragraph()
        p_sub.text = slide_data.key_message or "Questions & Discussion"
        p_sub.font.name = self.font_name
        p_sub.font.size = Pt(self.font_size_base - 2)
        p_sub.font.bold = True
        p_sub.font.color.rgb = self.theme.primary
        p_sub.alignment = PP_ALIGN.CENTER
        p_sub.space_before = Pt(12)

        # Bullets / Contact Details
        for b in slide_data.bullets[:3]:
            p_b = tf.add_paragraph()
            p_b.text = b
            p_b.font.name = self.font_name
            p_b.font.size = Pt(self.font_size_base - 6)
            p_b.font.color.rgb = self.theme.muted_text
            p_b.alignment = PP_ALIGN.CENTER
            p_b.space_before = Pt(8)

        self._attach_speaker_notes(slide, slide_data.speaker_notes)
        return slide

