"""AI PPT Generator - Modern Production-Quality Streamlit Application.

Generates professional, editable PowerPoint presentations using Groq AI
and python-pptx, featuring real-time preview, slide editing, and diverse layouts.
"""

import io
import os
import json
import logging
import streamlit as st

import config
import importlib
import src.ai_service
importlib.reload(src.ai_service)

from src.ai_service import GroqAIService, generate_offline_sample
from src.content_schema import PresentationData, SlideContent
from src.pptx_generator import generate_presentation_pptx
from src.theme_manager import get_theme_palette, THEMES
from src.utils import sanitize_filename, export_presentation_to_json, import_presentation_from_json, verify_pptx_integrity

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AIPPTApp")

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI PPT Generator | Professional Presentations with Groq AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom Modern SaaS CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Font and Accent Styling */
    :root {
        --primary-blue: #2563EB;
        --primary-dark: #1E40AF;
        --primary-light: #EFF6FF;
        --border-color: #E2E8F0;
        --card-bg: #FFFFFF;
        --text-slate: #1E293B;
    }

    /* App Header Card */
    .app-header {
        text-align: center;
        padding: 2.2rem 1.5rem 1.8rem 1.5rem;
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.05);
    }
    .app-header h1 {
        font-size: 2.4rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .app-header p {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 0;
    }
    .badge-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    /* Section Cards */
    .settings-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Primary Generate Button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
    }

    /* Slide Preview Cards */
    .slide-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-left: 0.5rem;
    }
    .badge-blue { background-color: #DBEAFE; color: #1E40AF; }
    .badge-green { background-color: #D1FAE5; color: #065F46; }
    .badge-purple { background-color: #EDE9FE; color: #5B21B6; }

    /* Footer text */
    .app-footer {
        text-align: center;
        color: #94A3B8;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border-color);
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "presentation_data" not in st.session_state:
    st.session_state.presentation_data = None

if "pptx_bytes" not in st.session_state:
    st.session_state.pptx_bytes = None

if "current_filename" not in st.session_state:
    st.session_state.current_filename = "presentation.pptx"

if "last_settings" not in st.session_state:
    st.session_state.last_settings = {}

if "logo_bytes" not in st.session_state:
    st.session_state.logo_bytes = None

if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""


# -----------------------------------------------------------------------------
# Sidebar: Credentials, AI Models & Branding
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key Handling (Env or Manual Override)
    env_groq_key = config.GROQ_API_KEY
    api_key_input = st.text_input(
        "Groq API Key",
        value=env_groq_key,
        type="password",
        placeholder="gsk_...",
        help="Get your free key from https://console.groq.com/keys"
    )

    # Model Discovery & Selection
    if api_key_input:
        model_options = GroqAIService.get_available_models(api_key_input)
    else:
        model_options = config.SUPPORTED_GROQ_MODELS

    preferred_model = config.GROQ_MODEL or "openai/gpt-oss-120b"
    if preferred_model not in model_options:
        model_options.insert(0, preferred_model)

    default_model_idx = model_options.index(preferred_model) if preferred_model in model_options else 0

    selected_model = st.selectbox(
        "Groq Model",
        options=model_options,
        index=default_model_idx,
        help="Discovered active models on your Groq endpoint."
    )

    # API Connection Test
    col_test, col_demo = st.columns([1, 1])
    with col_test:
        if st.button("🔌 Test API", use_container_width=True):
            test_service = GroqAIService(api_key=api_key_input, model=selected_model)
            with st.spinner("Pinging Groq..."):
                is_ok, msg = test_service.verify_connection()
                if is_ok:
                    st.success(f"Connected: {selected_model}")
                else:
                    st.error(msg)

    with col_demo:
        use_offline_demo = st.checkbox("Offline Mode", value=False, help="Generate instantly without API keys or costs.")

    st.markdown("---")

    # Branding & Custom Logo
    st.subheader("🎨 Presentation Branding")
    logo_file = st.file_uploader(
        "Upload Brand Logo",
        type=["png", "jpg", "jpeg", "webp"],
        help="Optional logo stamped onto slide headers."
    )
    if logo_file:
        st.session_state.logo_bytes = logo_file.read()
        st.image(st.session_state.logo_bytes, caption="Uploaded Logo Preview", width=140)
    else:
        st.session_state.logo_bytes = None

    # JSON Import / Export
    st.markdown("---")
    st.subheader("📂 Deck Portability")
    imported_file = st.file_uploader("Import Deck (JSON)", type=["json"], help="Load an existing presentation outline.")
    if imported_file:
        try:
            content_str = imported_file.read().decode("utf-8")
            imported_deck, imp_err = import_presentation_from_json(content_str)
            if imported_deck:
                st.session_state.presentation_data = imported_deck
                st.session_state.current_filename = sanitize_filename(imported_deck.title)
                st.success(f"Imported: {imported_deck.title}")
            else:
                st.error(f"Import failed: {imp_err}")
        except Exception as e:
            st.error(f"Invalid JSON file: {e}")

    if st.button("🧹 Reset Presentation", use_container_width=True):
        st.session_state.presentation_data = None
        st.session_state.pptx_bytes = None
        st.rerun()


# -----------------------------------------------------------------------------
# Main Application Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <div class="badge-icon">📊</div>
    <h1>AI PPT Generator</h1>
    <p>Generate Professional PowerPoint Presentations using Groq AI</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Topic & Quick Presets
# -----------------------------------------------------------------------------
col_topic, col_presets = st.columns([3, 2])

with col_topic:
    topic_val = st.text_input(
        "Presentation Topic *",
        value=st.session_state.topic_input,
        placeholder="e.g. Artificial Intelligence & Robotics, Climate Tech, Q3 SaaS Financial Review",
        help="Enter the primary subject of your presentation."
    )

with col_presets:
    st.markdown("<p style='font-weight:600; font-size:0.9rem; color:#475569; margin-bottom:0.4rem;'>💡 Quick Example Presets:</p>", unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        if st.button("🤖 Generative AI", use_container_width=True):
            st.session_state.topic_input = "Generative AI in Modern Software Engineering"
            st.rerun()
        if st.button("⚡ Renewable Energy", use_container_width=True):
            st.session_state.topic_input = "Global Transition to Renewable Energy Systems"
            st.rerun()
    with p_col2:
        if st.button("🔐 Cybersecurity", use_container_width=True):
            st.session_state.topic_input = "Zero-Trust Cybersecurity Architecture"
            st.rerun()
        if st.button("🚀 Pitch Deck", use_container_width=True):
            st.session_state.topic_input = "NextGen FinTech Startup Investor Pitch Deck"
            st.rerun()

# Additional Custom Instructions
additional_instructions = st.text_area(
    "Additional Instructions (Optional)",
    placeholder="Specify target audience expectations, key concepts to highlight, statistical requirements, tone nuances, etc.",
    height=75
)

st.markdown("---")


# -----------------------------------------------------------------------------
# Presentation Settings: Two-Column Responsive Layout
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">⚙️ Presentation Settings</div>', unsafe_allow_html=True)

settings_col1, settings_col2 = st.columns(2)

with settings_col1:
    slides_count = st.slider(
        "Number of Slides",
        min_value=config.MIN_SLIDE_COUNT,
        max_value=config.MAX_SLIDE_COUNT,
        value=config.DEFAULT_SLIDE_COUNT,
        help="Configurable from 3 to 30 slides."
    )

    presentation_style = st.selectbox(
        "Presentation Style",
        options=config.PRESENTATION_STYLES,
        index=0,
        help="Influences AI tone, vocabulary, and structural layout choices."
    )

    theme_selection = st.selectbox(
        "Theme Palette",
        options=list(THEMES.keys()),
        index=0,
        help="Select light or dark high-contrast presentation color schemes."
    )

    target_audience = st.selectbox(
        "Target Audience",
        options=config.TARGET_AUDIENCES,
        index=0,
        help="Tailors language depth and conceptual explanations."
    )

    content_depth = st.selectbox(
        "Content Depth",
        options=config.CONTENT_DEPTHS,
        index=1,
        help="Concise: 3 punchy points; Balanced: 4 clear points; Detailed: 5 points with examples."
    )

with settings_col2:
    language = st.selectbox(
        "Language",
        options=config.SUPPORTED_LANGUAGES,
        index=0,
        help="AI generates all slide content and notes in this language."
    )

    font_family = st.selectbox(
        "Font Family",
        options=config.SUPPORTED_FONTS,
        index=0,
        help="Selectable typography supported natively by Microsoft PowerPoint."
    )

    font_size = st.slider(
        "Font Size Scale",
        min_value=18,
        max_value=32,
        value=config.DEFAULT_FONT_SIZE,
        help="Base body font size in points."
    )

    creativity = st.slider(
        "AI Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=config.DEFAULT_TEMPERATURE,
        step=0.05,
        help="Lower values yield factual and deterministic output; higher values increase variety."
    )

    aspect_ratio = st.radio(
        "Aspect Ratio",
        options=["16:9 (Widescreen)", "4:3 (Standard)"],
        index=0,
        horizontal=True
    )
    aspect_ratio_code = "16:9" if "16:9" in aspect_ratio else "4:3"


# -----------------------------------------------------------------------------
# Optional Elements / Toggles
# -----------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🧩 Presentation Components</div>', unsafe_allow_html=True)

tog_col1, tog_col2, tog_col3 = st.columns(3)

with tog_col1:
    include_title_slide = st.checkbox("Include Title Slide", value=True)
    include_toc = st.checkbox("Include Table of Contents (Agenda)", value=True)
    include_ending_slide = st.checkbox("Include Ending / Q&A Slide", value=True)

with tog_col2:
    include_conclusion = st.checkbox("Include Conclusion Slide", value=True)
    include_references = st.checkbox("Include References Slide", value=False)
    include_slide_numbers = st.checkbox("Include Slide Numbers", value=True)

with tog_col3:
    include_notes = st.checkbox("Include Speaker Notes", value=True)


# -----------------------------------------------------------------------------
# Primary Action Button
# -----------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀 Generate Presentation", type="primary", use_container_width=True)


# -----------------------------------------------------------------------------
# Generation Logic
# -----------------------------------------------------------------------------
if generate_btn:
    active_topic = topic_val.strip()

    if not active_topic:
        st.warning("⚠️ Please enter a presentation topic to begin.")
    else:
        st.session_state.topic_input = active_topic

        # Aggregate settings dictionary
        generation_settings = {
            "topic": active_topic,
            "additional_instructions": additional_instructions,
            "slides": slides_count,
            "style": presentation_style,
            "theme": theme_selection,
            "language": language,
            "font": font_family,
            "font_size": font_size,
            "creativity": creativity,
            "target_audience": target_audience,
            "content_depth": content_depth,
            "include_toc": include_toc,
            "include_conclusion": include_conclusion,
            "include_references": include_references,
            "speaker_notes": include_notes,
            "include_slide_numbers": include_slide_numbers,
            "include_title_slide": include_title_slide,
            "include_ending_slide": include_ending_slide,
            "aspect_ratio": aspect_ratio_code
        }

        # Progress tracker
        progress_bar = st.progress(0)
        status_text = st.empty()

        presentation_data = None
        error_msg = None

        try:
            if use_offline_demo or not api_key_input:
                status_text.text("⚡ Generating offline presentation template...")
                progress_bar.progress(35)
                presentation_data = generate_offline_sample(topic=active_topic, slide_count=slides_count)
            else:
                status_text.text("🤖 Connecting to Groq AI...")
                progress_bar.progress(20)

                ai_service = GroqAIService(api_key=api_key_input, model=selected_model)
                status_text.text(f"🧠 Synthesizing structured slide deck with {selected_model}...")
                progress_bar.progress(45)

                presentation_data, error_msg = ai_service.generate_presentation(generation_settings)

            if error_msg or not presentation_data:
                st.error(f"❌ Presentation Generation Failed: {error_msg}")
            else:
                status_text.text("🎨 Rendering PowerPoint layouts, shapes, and typography...")
                progress_bar.progress(75)

                # Generate PPTX binary stream
                pptx_stream = generate_presentation_pptx(
                    presentation_data=presentation_data,
                    theme=theme_selection,
                    font_name=font_family,
                    font_size=font_size,
                    aspect_ratio=aspect_ratio_code,
                    include_slide_numbers=include_slide_numbers,
                    logo_bytes=st.session_state.logo_bytes
                )

                # Save presentation in session state
                st.session_state.presentation_data = presentation_data
                st.session_state.pptx_bytes = pptx_stream
                st.session_state.current_filename = sanitize_filename(presentation_data.title)
                st.session_state.last_settings = generation_settings

                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                st.success("✅ Presentation generated successfully!")

        except Exception as exc:
            logger.exception("Unexpected error during presentation generation")
            st.error(f"An unexpected error occurred: {str(exc)}")
            progress_bar.empty()
            status_text.empty()


# -----------------------------------------------------------------------------
# Presentation Success & Preview Section
# -----------------------------------------------------------------------------
if st.session_state.presentation_data and st.session_state.pptx_bytes:
    pres: PresentationData = st.session_state.presentation_data

    st.markdown("---")
    st.markdown('<div class="section-title">📊 Generated Presentation</div>', unsafe_allow_html=True)

    # Presentation Summary Info Card
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    with info_col1:
        st.metric("Total Slides", len(pres.slides))
    with info_col2:
        st.metric("Theme", st.session_state.last_settings.get("theme", theme_selection))
    with info_col3:
        st.metric("Aspect Ratio", st.session_state.last_settings.get("aspect_ratio", aspect_ratio_code))
    with info_col4:
        st.metric("Language", st.session_state.last_settings.get("language", language))

    # Action Toolbar: Download, JSON Export, Re-render
    st.markdown("<br>", unsafe_allow_html=True)
    action_col1, action_col2, action_col3 = st.columns([2, 1, 1])

    with action_col1:
        st.download_button(
            label=f"📥 Download PowerPoint ({st.session_state.current_filename})",
            data=st.session_state.pptx_bytes.getvalue(),
            file_name=st.session_state.current_filename,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            type="primary",
            use_container_width=True
        )

    with action_col2:
        json_export = export_presentation_to_json(pres)
        st.download_button(
            label="📄 Export JSON",
            data=json_export,
            file_name=f"{st.session_state.current_filename.replace('.pptx', '')}.json",
            mime="application/json",
            use_container_width=True
        )

    with action_col3:
        if st.button("🔄 Apply Slide Edits", use_container_width=True, help="Re-renders PPTX with your edited text without re-calling Groq AI."):
            with st.spinner("Applying updates to PowerPoint..."):
                updated_pptx = generate_presentation_pptx(
                    presentation_data=pres,
                    theme=st.session_state.last_settings.get("theme", theme_selection),
                    font_name=st.session_state.last_settings.get("font", font_family),
                    font_size=st.session_state.last_settings.get("font_size", font_size),
                    aspect_ratio=st.session_state.last_settings.get("aspect_ratio", aspect_ratio_code),
                    include_slide_numbers=st.session_state.last_settings.get("include_slide_numbers", include_slide_numbers),
                    logo_bytes=st.session_state.logo_bytes
                )
                st.session_state.pptx_bytes = updated_pptx
                st.success("PowerPoint updated with your edits!")
                st.rerun()

    # -------------------------------------------------------------------------
    # Slide-by-Slide Interactive Preview & Editing
    # -------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📑 Slide Deck Inspector & Editor")
    st.caption("Expand any slide to review, edit bullet points, or regenerate individual slides.")

    for idx, slide_item in enumerate(pres.slides):
        slide_num = idx + 1
        layout_name = slide_item.layout.upper().replace("_", " ")

        with st.expander(f"Slide {slide_num}: {slide_item.title}  [{layout_name}]", expanded=(idx < 2)):
            col_preview_left, col_preview_right = st.columns([3, 2])

            with col_preview_left:
                # Editable Title
                new_title = st.text_input(
                    f"Slide {slide_num} Title",
                    value=slide_item.title,
                    key=f"title_{slide_num}"
                )
                slide_item.title = new_title

                # Editable Key Message
                new_key_msg = st.text_input(
                    f"Key Message / Takeaway",
                    value=slide_item.key_message or "",
                    key=f"msg_{slide_num}"
                )
                slide_item.key_message = new_key_msg

                # Editable Bullets (Joined by newlines for clean multi-line editing)
                bullets_joined = "\n".join(slide_item.bullets)
                new_bullets_text = st.text_area(
                    f"Bullet Points (one per line)",
                    value=bullets_joined,
                    height=120,
                    key=f"bullets_{slide_num}"
                )
                slide_item.bullets = [b.strip() for b in new_bullets_text.split("\n") if b.strip()]

            with col_preview_right:
                st.markdown(f"**Layout Type:** `{slide_item.layout}`")

                if slide_item.visual_description:
                    st.info(f"**Visual Concept:** {slide_item.visual_description}")

                # Editable Speaker Notes
                new_notes = st.text_area(
                    "Speaker Notes",
                    value=slide_item.speaker_notes or "",
                    height=100,
                    key=f"notes_{slide_num}"
                )
                slide_item.speaker_notes = new_notes

                # Single-Slide Regeneration
                if api_key_input and not use_offline_demo:
                    refine_prompt = st.text_input(
                        "Slide Refinement Prompt",
                        placeholder="e.g. Make it more technical, add 3 metric examples",
                        key=f"refine_prompt_{slide_num}"
                    )
                    if st.button(f"⚡ Regenerate Slide {slide_num}", key=f"btn_regen_{slide_num}"):
                        with st.spinner(f"Refining Slide {slide_num}..."):
                            ai_service = GroqAIService(api_key=api_key_input, model=selected_model)
                            updated_slide, regen_err = ai_service.regenerate_single_slide(
                                presentation_title=pres.title,
                                slide=slide_item,
                                feedback=refine_prompt
                            )
                            if updated_slide:
                                pres.slides[idx] = updated_slide
                                st.success(f"Slide {slide_num} updated!")
                                st.rerun()
                            else:
                                st.error(f"Failed to regenerate slide: {regen_err}")


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("""
<div class="app-footer">
    AI PPT Generator • Powered by Groq AI & python-pptx • Enterprise-Grade Presentation Builder
</div>
""", unsafe_allow_html=True)
