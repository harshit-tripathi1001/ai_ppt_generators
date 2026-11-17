# System Architecture Diagrams

## Figure 1 — High-Level System Architecture

```mermaid
flowchart TD
    User["👤 End User\n(Browser)"]
    UI["app.py\nStreamlit UI Layer"]
    CFG["config.py\nConfiguration Module"]
    AI["src/ai_service.py\nGroqAIService"]
    Groq["☁️ Groq Cloud API\n(LLM Inference)"]
    VAL["src/content_validator.py\nContentValidator"]
    SCH["src/content_schema.py\nPydantic Schema"]
    GEN["src/pptx_generator.py\nPresentationGenerator"]
    LAY["src/slide_layouts.py\nLayoutRenderer (×13)"]
    THM["src/theme_manager.py\nThemeManager"]
    UTL["src/utils.py\nUtility Functions"]
    IMG["src/image_service.py\nImageService (Wikimedia)"]
    OUT["📄 .pptx Binary\n(BytesIO)"]

    User -->|"Settings + Topic"| UI
    UI --> CFG
    UI -->|"Prompt + Config"| AI
    AI -->|"HTTP POST"| Groq
    Groq -->|"JSON string"| AI
    AI --> VAL
    VAL --> SCH
    SCH -->|"PresentationData"| GEN
    GEN --> LAY
    GEN --> THM
    GEN --> IMG
    LAY --> UTL
    GEN --> OUT
    OUT -->|"st.download_button"| User
```

---

## Figure 2 — Module Dependency Graph

```mermaid
flowchart LR
    app["app.py"]
    cfg["config.py"]
    ai["ai_service.py"]
    cv["content_validator.py"]
    cs["content_schema.py"]
    pg["pptx_generator.py"]
    sl["slide_layouts.py"]
    tm["theme_manager.py"]
    img["image_service.py"]
    util["utils.py"]

    app --> cfg
    app --> ai
    app --> pg
    app --> util
    ai --> cv
    ai --> cs
    cv --> cs
    pg --> sl
    pg --> tm
    pg --> img
    pg --> util
    sl --> tm
    sl --> cs
```

---

## Figure 3 — Presentation Generation Pipeline

```mermaid
flowchart TD
    A["User submits settings\n& topic"] --> B["Build LLM prompt\n(ai_service.py)"]
    B --> C["POST to Groq API\n(HTTP/1.1 with retry)"]
    C --> D{"HTTP 200?"}
    D -- No / 404 --> E["Auto-fallback to\nnext available model"]
    E --> C
    D -- Yes --> F["Extract raw JSON\nfrom response text"]
    F --> G["Regex fence stripping\n& JSON repair"]
    G --> H["Pydantic validation\n(PresentationData)"]
    H --> I{"Valid?"}
    I -- No --> J["Field defaulting\n& slide count enforcement"]
    J --> H
    I -- Yes --> K["Iterate slides\n(pptx_generator.py)"]
    K --> L["Select LayoutRenderer\nby layout type"]
    L --> M["Apply ThemePalette\ncolors & fonts"]
    M --> N["Write shapes to\npython-pptx Slide"]
    N --> O{"More slides?"}
    O -- Yes --> K
    O -- No --> P["Save to BytesIO\n→ st.download_button"]
```

---

## Figure 4 — Deployment Architecture

```mermaid
flowchart LR
    subgraph Local["Local Machine / Cloud VM"]
        SL["Streamlit Server\n(localhost:8501)"]
        PY["Python 3.15\n.venv environment"]
        FS["File System\n.env · .pptx output"]
        SL --> PY
        PY --> FS
    end
    subgraph Cloud["External Services"]
        GROQ["Groq API\napi.groq.com"]
        WK["Wikimedia API\nwikipedia.org"]
    end
    Browser["🌐 User Browser"] -->|"HTTP"| SL
    PY -->|"HTTPS REST"| GROQ
    PY -->|"HTTPS REST"| WK
```

