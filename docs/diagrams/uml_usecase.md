# UML Use Case Diagram

## Figure 11 — System Use Cases

```mermaid
flowchart TD
    User(["👤 User"])
    Groq(["☁️ Groq API\n(External System)"])

    UC1["Configure API Key"]
    UC2["Select Groq Model"]
    UC3["Enter Presentation Topic"]
    UC4["Configure Settings\n(slides, theme, font,\nstyle, language, depth)"]
    UC5["Generate Presentation"]
    UC6["Preview Slides\n(text summary)"]
    UC7["Edit Individual Slide\n(in-browser editor)"]
    UC8["Download PPTX"]
    UC9["Export JSON Schema"]
    UC10["Import JSON Schema"]
    UC11["Use Offline Sample\n(no API key)"]
    UC12["Call LLM Inference"]
    UC13["Return Structured JSON"]

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11

    UC5 -->|"includes"| UC12
    UC12 -->|"invokes"| Groq
    Groq -->|"returns"| UC13
    UC13 -->|"feeds"| UC5

    UC11 -.->|"extends"| UC5
    UC6 -.->|"extends"| UC5
    UC7 -.->|"extends"| UC6
    UC8 -.->|"extends"| UC5
    UC9 -.->|"extends"| UC5
    UC10 -.->|"extends"| UC5
```

---

## Figure 12 — Actor Responsibilities

| Actor | Role | Interactions |
|---|---|---|
| **User** | End user operating the web UI | Configures settings, triggers generation, downloads output |
| **Groq Cloud API** | External LLM inference service | Receives prompt, returns structured JSON |
| **Wikimedia API** | External image source (optional / fallback) | Returns image URLs for `image_text` layout |
| **Streamlit Runtime** | Web server framework | Renders UI components, manages session state |

