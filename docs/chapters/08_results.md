# Chapter 8 — Results and Discussion

## 8.1 Summary of Outcomes

The AI PPT Generator successfully achieves all seven primary objectives defined in
Chapter 2. The following table summarises the achievement status of each objective:

| Objective | Status | Evidence |
|---|---|---|
| Accept rich user configuration (20 settings) | ✅ Achieved | `app.py` — 20 configurable settings exposed in sidebar |
| Generate structured JSON via Groq AI | ✅ Achieved | `ai_service.py` — Groq API integration working |
| Validate and repair AI output | ✅ Achieved | `content_validator.py` — 6 validation tests passing |
| Render editable PPTX with 13 layouts | ✅ Achieved | `slide_layouts.py` — all 13 layouts tested |
| Interactive browser UI with download | ✅ Achieved | Streamlit app at localhost:8501 |
| Offline and model-fallback modes | ✅ Achieved | Offline sample + 404 auto-fallback |
| Comprehensive test coverage | ✅ Achieved | 18/18 pytest tests passing |

---

## 8.2 Generated Presentation Quality

Based on manual review of generated presentations using the live Groq API
(`openai/gpt-oss-120b` model):

### Content Quality
- Slide content is contextually relevant, well-structured, and uses appropriate
  vocabulary for the selected target audience and depth level.
- The model correctly applies language selection: generating complete Hindi or
  Spanish content when those languages are selected, while maintaining English
  JSON keys.
- The speaker notes (when enabled) provide useful talking points that expand on
  the slide bullet points rather than merely repeating them.

### Layout Diversity
- For a 10-slide Professional-style presentation, the AI typically generates:
  1 title slide, 1 agenda, 5–6 bullet/two-column content slides, 1 stats/KPI,
  1 conclusion, and 1 ending slide — a realistic and varied layout distribution.

### PPTX Fidelity
- All generated `.pptx` files open correctly in Microsoft PowerPoint 2016+ and
  LibreOffice Impress 7.0+.
- Text, colours, fonts, and layout are preserved exactly as rendered by python-pptx.
- Tables and bar charts are fully editable within PowerPoint.

---

## 8.3 Performance Measurements

The following measurements were recorded on the development machine (Intel Core
processor, 16 GB RAM, broadband internet):

| Operation | Typical Duration |
|---|---|
| Groq API call (10 slides, `openai/gpt-oss-120b`) | 4–8 seconds |
| Groq API call (30 slides, `openai/gpt-oss-120b`) | 10–18 seconds |
| JSON validation + repair | < 50 ms |
| PPTX generation (10 slides) | 0.8–1.5 seconds |
| PPTX generation (30 slides) | 2.0–4.0 seconds |
| Total end-to-end (10 slides) | 5–10 seconds |
| Total end-to-end (30 slides) | 12–22 seconds |

All measurements are within the 30-second NFR-01 limit.

---

## 8.4 Comparison: Proposed vs Existing Systems

| Feature | AI PPT Generator | Gamma | Beautiful.ai | SlidesAI |
|---|---|---|---|---|
| Native `.pptx` output | ✅ Yes | ❌ No | ❌ No | ⚠️ Partial |
| Editable in PowerPoint | ✅ Yes | ❌ No | ❌ No | ⚠️ Partial |
| Open source | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Offline mode | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Custom layouts (count) | ✅ 13 | ✅ Many | ✅ Many | ⚠️ Limited |
| Custom themes | ✅ 7 | ✅ Yes | ✅ Yes | ⚠️ Limited |
| Multiple languages | ✅ 11+ | ⚠️ Partial | ⚠️ Partial | ❌ English only |
| Programmatic API | ✅ JSON import | ❌ No | ❌ No | ❌ No |
| Free to use | ✅ Yes (self-hosted) | ⚠️ Freemium | ⚠️ Freemium | ⚠️ Freemium |

---

## 8.5 Screenshots

> **Note**: Screenshots of the running application were not captured during the
> project development phase. The following describes the UI as implemented in `app.py`:

**Screen 1 — Main Settings Page**: A sidebar containing the Groq API key field,
model selector, and API status badge. The main content area shows a centred header
with a chart icon, the application title, and a subtitle. Below the header, a
two-column grid of settings cards contains all 20 configuration controls.

**Screen 2 — Generation Progress**: After clicking "Generate Presentation", a
spinner with the message "Generating your presentation with Groq AI..." is displayed
while the API call is in progress.

**Screen 3 — Results Page**: After successful generation, a green success banner
shows the model used and slide count. Below, a tabbed slide preview shows each slide
with its title and content. A prominent "Download PPTX" button and a "Expand Editor"
button are displayed.

**Screen 4 — Slide Editor**: An accordion-style editor shows one text area per
slide for each editable field (title, bullets, body, speaker notes). Changes are
applied to the in-memory `PresentationData` and the PPTX can be re-downloaded.

---

## 8.6 Limitations

The following limitations are identified based on the actual implementation:

### L-01: Model Availability Dependency
The application's AI generation quality depends on which models are enabled on
the user's Groq account. The fallback mechanism handles unavailable models, but
the quality of smaller fallback models (e.g., `openai/gpt-oss-20b`) may be lower.

### L-02: No Image Generation
The image retrieval feature (Wikimedia API) is available but was originally
unreliable for Pexels/Unsplash due to API key requirements. Image placement in
`image_text` slides uses a native coloured shape placeholder rather than a real
photograph.

### L-03: Session State Volatility
All presentation data is held in Streamlit's `st.session_state`. A browser page
refresh or server restart clears the state, and the generated PPTX must be
re-downloaded or the session recreated. The JSON export/import feature partially
mitigates this.

### L-04: Token Limit for Large Decks
Presentations of 25–30 slides may approach the context window limit of smaller
models, potentially causing the AI to truncate the JSON response. The slide count
enforcement in the validator pads truncated outputs, but the padded slides contain
minimal content.

### L-05: No Authentication
The application has no user authentication. In a multi-user deployment, all users
share the same application instance and session state is not isolated between users.
Single-user local deployment is the recommended mode.

### L-06: No PDF Export
The application generates only `.pptx` output. PDF conversion would require
Microsoft Office, LibreOffice, or a third-party library and is not implemented.

