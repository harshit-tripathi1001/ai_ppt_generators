"""Automated tests for AI service behavior, mocks, and fallback mechanisms."""

import pytest
from unittest.mock import MagicMock, patch
from src.ai_service import GroqAIService, generate_offline_sample
from src.image_service import ImageService


def test_missing_api_key_behavior():
    """Verify that calling generate_presentation with an empty key returns a clear error."""
    service = GroqAIService(api_key="")
    assert service.is_configured is False

    is_ok, msg = service.verify_connection()
    assert is_ok is False
    assert "missing" in msg.lower() or "not configured" in msg.lower()

    result, err = service.generate_presentation({"topic": "Blockchain"})
    assert result is None
    assert "missing" in err.lower()


def test_empty_topic_behavior():
    """Verify that passing an empty presentation topic is rejected with validation message."""
    service = GroqAIService(api_key="gsk_dummy_test_key_12345")
    result, err = service.generate_presentation({"topic": "   "})
    assert result is None
    assert "cannot be empty" in err.lower()


def test_mocked_groq_successful_generation():
    """Verify that a properly mocked Groq chat completion produces valid PresentationData."""
    mock_payload = {
        "title": "Autonomous Vehicles",
        "subtitle": "Navigating the Future of Mobility",
        "overview": "Overview of sensor fusion, computer vision, and safety.",
        "target_audience": "Engineers",
        "key_objectives": ["Sensor Fusion", "Localization", "Path Planning"],
        "slides": [
            {
                "title": "Autonomous Vehicles",
                "layout": "title",
                "key_message": "Transforming transportation with AI.",
                "bullets": ["Sensor fusion", "Edge compute", "Safety systems"]
            },
            {
                "title": "Perception & Vision",
                "layout": "bullet_list",
                "key_message": "Multi-modal cameras and LiDAR perception.",
                "bullets": [
                    "High-resolution cameras provide dense color information",
                    "LiDAR offers precise 3D spatial depth maps",
                    "Radar ensures all-weather obstacle detection capability"
                ]
            },
            {
                "title": "Conclusion",
                "layout": "conclusion",
                "key_message": "Autonomous safety requires robust verification.",
                "bullets": ["Redundancy is critical", "Simulation accelerates testing"]
            }
        ]
    }

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = f"```json\n{import_json_str(mock_payload)}\n```"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    service = GroqAIService(api_key="gsk_valid_mock_key")
    with patch.object(service, "_get_client", return_value=mock_client):
        presentation, err = service.generate_presentation({
            "topic": "Autonomous Vehicles",
            "slides": 3,
            "style": "Technical",
            "theme": "Blue Modern"
        })

        assert err is None
        assert presentation is not None
        assert presentation.title == "Autonomous Vehicles"
        assert len(presentation.slides) == 3


def test_image_service_graceful_fallback():
    """Verify that ImageService handles missing keys and providers gracefully without raising exceptions."""
    # Test Pexels without key
    img_service = ImageService(api_key="", provider="pexels")
    assert img_service.is_configured is False

    # Test Wikimedia without key (open access)
    wiki_service = ImageService(provider="wikimedia")
    assert wiki_service.is_configured is True


def import_json_str(data: dict) -> str:
    import json
    return json.dumps(data)

