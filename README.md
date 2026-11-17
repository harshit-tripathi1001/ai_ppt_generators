# AI PPT Generator 📊

An enterprise-ready, professional PowerPoint generation web application built with **Streamlit**, **Groq AI (Llama 3.3 / 3.1)**, and **python-pptx**. 

AI PPT Generator turns any presentation topic into an editable, high-impact, beautifully themed presentation in seconds. It goes beyond basic bullet points on plain white slides by generating diverse visual layouts (KPI metrics, two-column comparisons, genuine PowerPoint tables, interactive charts, and process timelines), complete with speaker notes, agenda roadmaps, and optional royalty-free imagery.

---

## ✨ Features

- **High-Velocity AI Generation**: Powered by Groq's low-latency inference engine utilizing `llama-3.3-70b-versatile` and `llama-3.1-8b-instant`.
- **20 Working Presentation Controls**:
  1. *Presentation Topic*: Required topic or keyword.
  2. *Quick Topic Presets*: One-click starters (Generative AI, Cybersecurity, Clean Energy, Pitch Deck).
  3. *Additional Instructions*: Fine-tune focus, tone, or specific slide constraints.
  4. *Language Support*: English, Hindi, Hinglish, Spanish, French, German, Japanese, and more.
  5. *Configurable Slide Counts*: 3 to 30 slides with automatic padding or trimming.
  6. *Presentation Styles*: Professional, Academic, Corporate, Educational, Minimalist, Creative, Pitch Deck, Technical, Research.
  7. *Polished Themes*: Blue Modern, Dark Elegance, Emerald Green, Royal Purple, Sunset Warmth, Crimson Slate, and Light Minimal.
  8. *Native Typography*: Calibri, Arial, Helvetica, Trebuchet MS, Georgia, Garamond, Verdana.
  9. *Font Size Scaling*: Configurable base size with automatic visual hierarchy scaling.
  10. *AI Creativity Control*: Temperature slider from 0.0 (deterministic) to 1.0 (creative).
  11. *Target Audience Tailoring*: Students, Developers, Executives, Clients, Researchers, or Custom.
  12. *Content Depth*: Concise (3 punchy points), Balanced (4 clear points), Detailed (5 comprehensive points).
  13. *Table of Contents*: Generates an agenda roadmap slide.
  14. *Conclusion Slide*: Generates 3 synthesized key takeaways and a strategic call-to-action banner.
  15. *References & Citations*: Formatted reference slide with verification notices.
  16. *Speaker Notes*: Comprehensive speaking scripts embedded into PowerPoint's native notes pane.
  17. *Visual Suggestions & Image Retrieval*: Optional Pexels API integration with graceful native vector fallback.
  18. *Slide Numbers*: Clean, formatted `X / Total` numbering.
  19. *Configurable Title & Ending Slides*: Optional hero banner and Thank You / Q&A slide.
  20. *Aspect Ratio*: 16:9 widescreen (13.33" x 7.5") or 4:3 standard (10.0" x 7.5").
  21. *Custom Brand Logo Upload*: Stamped onto slide headers and title cards.
- **Rich PowerPoint Layout Variety**:
  - *Title Slide*: Hero card, accent lines, target audience badge, optional logo.
  - *Agenda / TOC*: Numbered visual grid cards.
  - *Title & Bullets*: Styled cards with custom bullet indicators.
  - *Two-Column Comparison*: Side-by-side cards with distinct headers.
  - *Statistics / KPI Cards*: Large-type metric values (e.g. `99.4%`, `10x`) with subtext.
  - *Image & Text*: Image container paired with structured takeaways.
  - *Process / Timeline Flow*: Chevron step sequence (1 → 2 → 3 → 4).
  - *Genuine PowerPoint Tables*: Real Office Open XML tables with styled headers and alternating rows.
  - *Genuine PowerPoint Charts*: Editable column, bar, line, and pie charts.
  - *Section Dividers*: High-contrast full-bleed accent slides.
  - *Conclusion*: 3 key takeaway boxes + closing action quote.
  - *References*: Citation cards with transparency disclaimer.
  - *Ending Slide*: Thank You and Q&A layout with contact placeholders.
- **Interactive Deck Editor & Per-Slide Regeneration**:
  - Expand any slide in Streamlit to inspect titles, key messages, bullets, and speaker notes.
  - Edit text directly in the browser and click **"Apply Slide Edits"** to instantly update the `.pptx` file in memory without re-calling the AI!
  - Regenerate single slides on demand using natural language refinement prompts.
- **Offline / Keyless Demo Mode**:
  - Test or demonstrate the full presentation rendering engine offline without requiring an active Groq API key or incurring token costs.
- **Deck Portability**:
  - One-click `.pptx` download generated in-memory via `io.BytesIO`.
  - Export and Import presentation schemas in structured JSON format.

---

## 📸 Screenshots

To add application screenshots:
1. Launch the application: `streamlit run app.py`
2. Take a screenshot of the main configuration panel and the generated slide inspector.
3. Save the image to `assets/app_screenshot.png`.

```markdown
![AI PPT Generator Dashboard](assets/app_screenshot.png)
```

---

## 🛠️ Project Structure

```
ai-ppt-generator/
├── app.py                      # Streamlit web application & UI layer
├── config.py                   # Centralized application constants & configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variable template
├── .gitignore                  # Git ignore rules (secrets, output, caches)
├── README.md                   # Documentation & execution guide
├── src/
│   ├── __init__.py             # Package marker
│   ├── ai_service.py           # Groq API client, prompt engineering & offline generator
│   ├── content_schema.py       # Pydantic data models for slides, metrics, tables & charts
│   ├── content_validator.py    # Resilient JSON parsing, schema repair & sanitization
│   ├── pptx_generator.py       # Independent python-pptx orchestration engine
│   ├── slide_layouts.py        # 13 distinctive slide layout renderers
│   ├── theme_manager.py        # Color palettes & typography definitions
│   ├── image_service.py        # Optional Pexels image retrieval with Pillow validation
│   └── utils.py                # Filename sanitization, PPTX verification, JSON export/import
├── assets/
│   └── README.md               # Asset storage instructions
└── tests/
    ├── test_content_validator.py  # Validation & JSON repair unit tests
    ├── test_pptx_generator.py     # PowerPoint layout, theme & integrity tests
    ├── test_ai_service.py         # AI service & mock response tests
    └── test_utils.py              # Filename & JSON import/export tests
```

---

## ⚙️ Prerequisites

- **Python 3.11+** installed (`python --version`)
- A free **Groq API Key** from [console.groq.com/keys](https://console.groq.com/keys)
- (Optional) A free **Pexels API Key** from [pexels.com/api](https://www.pexels.com/api/) for automatic slide photography

---

## 🚀 Installation & Local Execution

### 1. Clone or Open Workspace
Open your terminal in the project directory:
```powershell
cd "d:\Sem 7\ROSPL\AI_PPT"
```

### 2. Create and Activate Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Open `.env` in any text editor and add your Groq API key:
```ini
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
IMAGE_API_KEY=
```
*(Note: You can also enter or override your Groq API key directly in the web app sidebar at runtime.)*

### 5. Launch the Web Application
```powershell
streamlit run app.py
```
Streamlit will open the application automatically at `http://localhost:8501`.

---

## 🧪 Automated Testing

All core modules have comprehensive unit and integration tests covering:
- JSON extraction and repair of malformed LLM responses
- Slide count enforcement and missing field defaults
- Offline PowerPoint creation and 16:9 vs 4:3 aspect ratios
- Theme color rendering (light and dark modes)
- PPTX Open XML archive integrity and python-pptx re-opening
- Missing API key and network fallback handling

To execute the test suite:
```powershell
python -m pytest tests -v
```

Expected result:
```
============================= 18 passed in 5.63s ==============================
```

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

1. Push your code to a GitHub repository (ensure `.env` is ignored by `.gitignore`).
2. Log into [share.streamlit.io](https://share.streamlit.io).
3. Select **New App** and choose your repository, branch, and `app.py`.
4. Under **Advanced settings** -> **Secrets**, paste your configuration:
   ```toml
   GROQ_API_KEY = "gsk_..."
   GROQ_MODEL = "llama-3.3-70b-versatile"
   PEXELS_API_KEY = ""
   ```
5. Click **Deploy!**

---

## 🛡️ Reliability & Error Handling

- **Missing or Invalid API Key**: Clear guidance in the sidebar with a real-time connection diagnostic tester.
- **Malformed JSON from AI**: Regex bracket extraction, trailing comma cleanup, and automated schema repair.
- **Image API Rate Limits or Network Failures**: The generator never aborts presentation creation; it falls back to native vector shape illustrations and concept boxes automatically.
- **Session State Preservation**: Expanding slide cards or navigating UI tabs does not trigger unwanted deck regenerations.
- **In-Memory Generation**: Presentations are built and downloaded using `io.BytesIO` streams, eliminating disk clutter and orphaned temporary files.

---

## 💡 Cost & Rate-Limit Considerations

- Groq provides free-tier rate limits with generous token allowances for models such as `llama-3.3-70b-versatile` and `llama-3.1-8b-instant`.
- A 10-slide presentation generation typically consumes 1,500 to 3,000 output tokens.
- For high-volume generation, consider selecting `llama-3.1-8b-instant` in the sidebar for maximum speed and token economy.

---

## 📄 License
MIT License. Free for academic, personal, and commercial presentation generation.

