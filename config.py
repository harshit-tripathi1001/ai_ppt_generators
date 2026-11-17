"""Configuration module for AI PPT Generator.

Handles environment variables, default settings, and application constants.
Safe to import even if environment variables are not yet configured.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if present (with fallback if python-dotenv is not yet installed)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

# Groq AI Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()

# Available Groq Models (curated default list; dynamically updated if API key is provided)
SUPPORTED_GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

# Ensure configured model is always in options
if GROQ_MODEL and GROQ_MODEL not in SUPPORTED_GROQ_MODELS:
    SUPPORTED_GROQ_MODELS.insert(0, GROQ_MODEL)

# Image Provider Configuration (Optional)
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY", "").strip() or os.getenv("PEXELS_API_KEY", "").strip()
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "pexels").strip().lower()

# Application Defaults
DEFAULT_SLIDE_COUNT = 10
MIN_SLIDE_COUNT = 3
MAX_SLIDE_COUNT = 30
DEFAULT_TEMPERATURE = 0.7
DEFAULT_FONT = "Calibri"
DEFAULT_FONT_SIZE = 22
DEFAULT_THEME = "Blue Modern"
DEFAULT_LANGUAGE = "English"

# Supported Presentation Styles
PRESENTATION_STYLES = [
    "Professional",
    "Academic",
    "Corporate",
    "Educational",
    "Minimalist",
    "Creative",
    "Pitch Deck",
    "Technical",
    "Research"
]

# Supported Target Audiences
TARGET_AUDIENCES = [
    "General Audience",
    "Students",
    "Teachers & Educators",
    "Software Developers & Engineers",
    "Business Executives & C-Suite",
    "Clients & Investors",
    "Researchers & Scientists",
    "Custom"
]

# Supported Content Depths
CONTENT_DEPTHS = [
    "Concise",
    "Balanced",
    "Detailed"
]

# Supported Languages
SUPPORTED_LANGUAGES = [
    "English",
    "Hindi",
    "Hinglish",
    "Spanish",
    "French",
    "German",
    "Japanese",
    "Chinese",
    "Portuguese",
    "Italian",
    "Arabic"
]

# Supported Fonts in PowerPoint
SUPPORTED_FONTS = [
    "Calibri",
    "Arial",
    "Helvetica",
    "Trebuchet MS",
    "Georgia",
    "Garamond",
    "Verdana",
    "Tahoma"
]

# Output Directory
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

