"""Utility functions for presentation export, filename sanitization, and verification."""

import io
import re
import json
import zipfile
import logging
from typing import Optional, Dict, Any, Tuple
from pptx import Presentation

from src.content_schema import PresentationData

logger = logging.getLogger(__name__)


def sanitize_filename(title: str, max_length: int = 80) -> str:
    """Convert an arbitrary presentation title into a safe, cross-platform filename.

    Args:
        title: Raw title text.
        max_length: Maximum filename length before extension.

    Returns:
        Safe filename string ending with .pptx
    """
    if not title or not title.strip():
        return "presentation.pptx"

    # Keep only alphanumeric, spaces, hyphens, and underscores
    cleaned = re.sub(r'[^a-zA-Z0-9\s\-_]', '', title.strip())
    # Replace whitespace and repeated punctuation with single underscore
    cleaned = re.sub(r'[\s\-_]+', '_', cleaned)
    # Trim leading/trailing dots or underscores
    cleaned = cleaned.strip('._')

    if not cleaned:
        cleaned = "presentation"

    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip('_')

    return f"{cleaned}.pptx"


def verify_pptx_integrity(pptx_bytes_or_path: Any) -> Tuple[bool, Optional[str]]:
    """Verify that a given byte stream or file path is a valid, uncorrupted PowerPoint presentation.

    Checks:
    1. Valid ZIP container (Office Open XML)
    2. Contains standard PowerPoint content types XML
    3. Re-openable by python-pptx without exception

    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    try:
        # Check ZIP structure
        if isinstance(pptx_bytes_or_path, io.BytesIO):
            stream = io.BytesIO(pptx_bytes_or_path.getvalue())
        elif isinstance(pptx_bytes_or_path, bytes):
            stream = io.BytesIO(pptx_bytes_or_path)
        else:
            with open(pptx_bytes_or_path, "rb") as f:
                stream = io.BytesIO(f.read())

        if not zipfile.is_zipfile(stream):
            return False, "File is not a valid ZIP container (corrupted Office Open XML)."

        with zipfile.ZipFile(stream, "r") as zf:
            file_list = zf.namelist()
            if "[Content_Types].xml" not in file_list:
                return False, "Archive is missing [Content_Types].xml required for PPTX."
            if not any(f.startswith("ppt/") for f in file_list):
                return False, "Archive missing ppt/ directory."

        # Verify python-pptx can open it
        stream.seek(0)
        prs = Presentation(stream)
        slide_count = len(prs.slides)
        return True, f"Verified valid PowerPoint presentation ({slide_count} slides)."

    except Exception as e:
        logger.exception("PPTX integrity check failed")
        return False, f"PPTX integrity check failed: {str(e)}"


def export_presentation_to_json(presentation: PresentationData) -> str:
    """Serialize PresentationData model to formatted JSON string."""
    return presentation.model_dump_json(indent=2)


def import_presentation_from_json(json_str: str) -> Tuple[Optional[PresentationData], Optional[str]]:
    """Parse and deserialize JSON string back into PresentationData model."""
    try:
        data_dict = json.loads(json_str)
        pres = PresentationData.model_validate(data_dict)
        return pres, None
    except Exception as e:
        return None, f"Failed to import presentation JSON: {str(e)}"
