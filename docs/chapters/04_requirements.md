# Chapter 4 — System Requirements

## 4.1 Functional Requirements

### FR-01: Presentation Topic Input
The system SHALL accept a free-text presentation topic of 1–500 characters as the
primary content driver. The topic field SHALL be mandatory; the system SHALL display
a validation error if it is empty when the user attempts to generate a presentation.

### FR-02: Configuration Settings
The system SHALL expose the following presentation settings to the user:

| ID | Setting | Type | Range / Options |
|---|---|---|---|
| S-01 | Topic | Text | 1–500 chars (required) |
| S-02 | Additional Instructions | Multiline Text | Optional |
| S-03 | Language | Select | English, Hindi, Hinglish, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese |
| S-04 | Number of Slides | Slider | 3–30, default 10 |
| S-05 | Presentation Style | Select | Professional, Academic, Corporate, Educational, Minimalist, Creative, Pitch Deck, Technical, Research |
| S-06 | Theme | Select | Blue Modern, Dark Elegance, Emerald Green, Royal Purple, Sunset Warmth, Crimson Slate, Light Minimal |
| S-07 | Font Family | Select | Calibri, Arial, Times New Roman, Georgia, Helvetica Neue, Trebuchet MS |
| S-08 | Font Size | Slider | 16–36 pt, default 20 pt |
| S-09 | AI Creativity | Slider | 0.0–1.0, default 0.7 |
| S-10 | Target Audience | Select | Students, Teachers, Developers, Executives, Clients, Researchers, General Public |
| S-11 | Content Depth | Select | Concise, Balanced, Detailed |
| S-12 | Aspect Ratio | Select | 16:9, 4:3 |
| S-13 | Include Table of Contents | Checkbox | Default: True |
| S-14 | Include Conclusion | Checkbox | Default: True |
| S-15 | Include References | Checkbox | Default: False |
| S-16 | Include Speaker Notes | Checkbox | Default: False |
| S-17 | Groq API Key | Password | Optional (falls back to env var) |
| S-18 | Groq Model | Select | Dynamically fetched from API |
| S-19 | Slide Editor | Inline UI | Post-generation editing |
| S-20 | JSON Export / Import | Button | Round-trip editing |

### FR-03: AI Content Generation
The system SHALL submit a structured prompt to the Groq API and retrieve a JSON
slide outline. The prompt SHALL embed all S-01 through S-16 settings.

### FR-04: JSON Validation and Repair
The system SHALL parse the raw LLM response, extract JSON from markdown fences if
present, attempt to repair common JSON errors (trailing commas, unbalanced brackets),
and validate the result against the `PresentationData` Pydantic schema.

### FR-05: Slide Count Enforcement
The system SHALL trim or pad the slide list to match the user-requested slide count.
Padding SHALL use a generic `bullet_list` layout. The mandatory title slide and
ending slide SHALL be preserved during trimming.

### FR-06: PPTX Generation
The system SHALL generate a binary `.pptx` file using python-pptx. Each slide SHALL
use the layout specified in the validated JSON, with the theme palette and font
settings applied.

### FR-07: PPTX Download
The system SHALL provide a download button that delivers the generated `.pptx` file
to the user's browser as a binary attachment.

### FR-08: Slide Preview
The system SHALL display a text-based slide-by-slide preview after successful
generation, showing the slide title and key content.

### FR-09: Slide Editor
The system SHALL allow the user to edit the title, bullet points, body text, and
speaker notes of each slide in-browser after generation and before download.

### FR-10: Offline Mode
The system SHALL function without a live Groq API key by generating a pre-defined
sample presentation, clearly indicating to the user that the output is a demo.

### FR-11: Model Auto-Fallback
The system SHALL automatically retry the API call with the next available model if
the configured model returns HTTP 404, without requiring user intervention.

### FR-12: JSON Export / Import
The system SHALL allow the user to export the current presentation data as a JSON
file and import a previously exported JSON file to regenerate or re-edit a
presentation.

---

## 4.2 Non-Functional Requirements

### NFR-01: Performance
- Presentation generation (API call + PPTX rendering) SHALL complete within 30
  seconds for a 10-slide presentation under normal network conditions.
- PPTX file generation for 30 slides SHALL complete within 5 seconds on the target
  machine (Python 3.15 on modern hardware).

### NFR-02: Reliability
- The application SHALL not crash on malformed LLM responses; instead, it SHALL
  display a user-readable error and fall back to offline mode where possible.
- All 18 automated tests SHALL pass on the target platform before deployment.

### NFR-03: Usability
- The interface SHALL be operable by a non-technical user without documentation.
- All settings SHALL have sensible defaults such that the user needs only to enter
  a topic to generate a presentation.

### NFR-04: Maintainability
- The codebase SHALL follow a modular architecture with no module exceeding 600 lines
  of code (excluding `slide_layouts.py`, which is inherently larger due to 13
  individual renderers).
- All public functions SHALL have docstrings.

### NFR-05: Portability
- The application SHALL run on Windows, macOS, and Linux with Python 3.11+.
- All dependencies SHALL be installable via `pip install -r requirements.txt`.

### NFR-06: Security
- The Groq API key SHALL never be logged or displayed in the UI.
- The API key SHALL be read from environment variables (`.env`) or a password-masked
  input field.

### NFR-07: Compatibility
- Generated `.pptx` files SHALL be compatible with Microsoft PowerPoint 2016+ and
  LibreOffice Impress 7.0+.

---

## 4.3 Hardware and Software Requirements

### 4.3.1 Minimum Hardware
| Component | Requirement |
|---|---|
| CPU | Any modern x86-64 processor |
| RAM | 4 GB (8 GB recommended) |
| Storage | 500 MB for Python environment + dependencies |
| Network | Broadband internet connection (for Groq API) |

### 4.3.2 Software Requirements
| Software | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| Streamlit | ≥ 1.35.0 | Web UI framework |
| groq | ≥ 0.9.0 | Groq AI SDK |
| python-pptx | ≥ 1.0.0 | PPTX generation |
| python-dotenv | ≥ 1.0.0 | Environment variable loading |
| requests | ≥ 2.31.0 | HTTP image fetching |
| Pillow | ≥ 10.0.0 | Image processing |
| pydantic | ≥ 2.0.0 | Data validation |
| pytest | ≥ 8.0.0 | Automated testing |

### 4.3.3 External Services
| Service | URL | Purpose |
|---|---|---|
| Groq Cloud API | `api.groq.com` | LLM inference |
| Wikimedia REST API | `en.wikipedia.org/api/rest_v1` | Image retrieval (optional) |
| Wikimedia Commons API | `commons.wikimedia.org/w/api.php` | Image fallback (optional) |

