"""Groq AI presentation generation service.

Interacts with the official Groq Python SDK to generate structured,
validated presentation outlines, layouts, and slide content.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from groq import Groq, GroqError, APIConnectionError, RateLimitError, AuthenticationError

from src.content_schema import PresentationData, SlideContent
from src.content_validator import parse_and_validate_response

logger = logging.getLogger(__name__)


class GroqAIService:
    """Service for orchestrating AI generation with Groq."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Groq client with environment fallback."""
        self.api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
        self.model = (model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")).strip()
        self._client: Optional[Groq] = None

    @staticmethod
    def get_available_models(api_key: Optional[str] = None) -> List[str]:
        """Fetch list of active chat completion models from Groq API."""
        default_models = [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768"
        ]
        key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
        if not key:
            return default_models

        try:
            client = Groq(api_key=key)
            models_data = client.models.list().data
            # Filter chat models, exclude whisper, prompt-guard, safeguard, embeddings
            chat_models = [
                m.id for m in models_data
                if not any(ex in m.id.lower() for ex in ["whisper", "prompt-guard", "safeguard", "guard", "embed"])
            ]
            if chat_models:
                priority = [
                    "openai/gpt-oss-120b",
                    "llama-3.3-70b-versatile",
                    "qwen/qwen3.8-27b",
                    "openai/gpt-oss-20b",
                    "llama-3.1-8b-instant"
                ]
                ordered = [p for p in priority if p in chat_models]
                for m in chat_models:
                    if m not in ordered:
                        ordered.append(m)
                return ordered
        except Exception as e:
            logger.warning("Could not dynamically query Groq models: %s", e)

        return default_models

    @property
    def is_configured(self) -> bool:
        """Check if an API key is available."""
        return bool(self.api_key)

    def _get_client(self) -> Groq:
        """Lazily initialize and return the Groq client."""
        if not self.is_configured:
            raise ValueError("Groq API Key is not configured. Please supply an API key.")
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def verify_connection(self) -> Tuple[bool, str]:
        """Test API credentials and model availability."""
        if not self.is_configured:
            return False, "Groq API Key is missing. Please enter your key in settings or .env file."
        try:
            client = self._get_client()
            # Fast ping with 1 token
            client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                temperature=0.0
            )
            return True, f"Connected to Groq ({self.model})"
        except AuthenticationError:
            return False, "Authentication failed: The provided Groq API Key is invalid."
        except RateLimitError:
            return False, "Groq API rate limit reached. Please wait a moment and try again."
        except APIConnectionError:
            return False, "Network connection error while connecting to Groq API."
        except GroqError as ge:
            return False, f"Groq API Error: {str(ge)}"
        except Exception as e:
            return False, f"Connection check failed: {str(e)}"

    def _build_system_prompt(self) -> str:
        """Construct the system instructions enforcing pure, valid JSON output."""
        return (
            "You are an elite executive presentation designer and subject matter expert. "
            "Your task is to produce a comprehensive, structured PowerPoint presentation outline. "
            "You MUST output STRICT, VALID JSON ONLY. Do not write any markdown outside the JSON, "
            "no conversational text, no preambles, and no closing remarks.\n\n"
            "JSON SCHEMA REQUIREMENT:\n"
            "{\n"
            '  "title": "Presentation Title",\n'
            '  "subtitle": "Informative Subtitle",\n'
            '  "overview": "2-3 sentence executive summary",\n'
            '  "target_audience": "Intended audience category",\n'
            '  "key_objectives": ["Objective 1", "Objective 2", "Objective 3"],\n'
            '  "slides": [\n'
            "    {\n"
            '      "title": "Slide Title",\n'
            '      "layout": "bullet_list" | "two_column" | "stats_kpi" | "image_text" | "process_flow" | "table" | "chart" | "conclusion" | "references",\n'
            '      "key_message": "One concise takeaway sentence (max 15 words)",\n'
            '      "bullets": [\n'
            '        "Short bullet point 1 (8-14 words)",\n'
            '        "Short bullet point 2 (8-14 words)",\n'
            '        "Short bullet point 3 (8-14 words)"\n'
            "      ],\n"
            '      "columns": {"col1_title": "Aspect A", "col1_bullets": ["Point A1", "Point A2"], "col2_title": "Aspect B", "col2_bullets": ["Point B1", "Point B2"]},\n'
            '      "stats": [{"label": "Metric Name", "value": "99.4%", "detail": "Subtext"}],\n'
            '      "table_data": {"headers": ["Header 1", "Header 2", "Header 3"], "rows": [["R1C1", "R1C2", "R1C3"], ["R2C1", "R2C2", "R2C3"]]},\n'
            '      "chart_data": {"chart_type": "column", "title": "Chart Title", "categories": ["Cat 1", "Cat 2", "Cat 3"], "series": [{"name": "Metric", "values": [40, 70, 95]}]},\n'
            '      "process_steps": [{"step_number": 1, "title": "Phase 1", "description": "Details of phase 1"}],\n'
            '      "visual_description": "Conceptual architectural description",\n'
            '      "speaker_notes": "2-3 sentences of speaking script for presenter"\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    def _build_user_prompt(self, settings: Dict[str, Any]) -> str:
        """Construct the prompt detailing presentation parameters."""
        topic = settings.get("topic", "").strip()
        additional_instructions = settings.get("additional_instructions", "").strip()
        slides_count = settings.get("slides", 10)
        style = settings.get("style", "Professional")
        theme = settings.get("theme", "Blue Modern")
        language = settings.get("language", "English")
        target_audience = settings.get("target_audience", "General Audience")
        content_depth = settings.get("content_depth", "Balanced")
        include_toc = settings.get("include_toc", True)
        include_conclusion = settings.get("include_conclusion", True)
        include_references = settings.get("include_references", False)
        include_notes = settings.get("speaker_notes", True)

        # Depth instructions
        if content_depth == "Concise":
            depth_guide = "3 punchy, high-impact bullet points per slide (6-10 words each). Very direct."
        elif content_depth == "Detailed":
            depth_guide = "4-5 comprehensive bullet points per slide (10-16 words each) with concrete examples."
        else:
            depth_guide = "3-4 balanced, informative bullet points per slide (8-14 words each)."

        # Structural distribution guidelines
        prompt = (
            f"Generate a {slides_count}-slide presentation on the following topic:\n"
            f"TOPIC: {topic}\n\n"
            f"PRESENTATION SPECIFICATIONS:\n"
            f"- Requested Total Slides: {slides_count}\n"
            f"- Presentation Style: {style}\n"
            f"- Target Audience: {target_audience}\n"
            f"- Language: {language} (ALL title, bullet points, headers, and notes must be in {language})\n"
            f"- Content Depth: {content_depth} -> {depth_guide}\n"
            f"- Theme Aesthetic: {theme}\n"
            f"- Include Table of Contents: {include_toc}\n"
            f"- Include Conclusion Slide: {include_conclusion}\n"
            f"- Include References Slide: {include_references}\n"
            f"- Include Speaker Notes: {include_notes}\n\n"
        )

        if additional_instructions:
            prompt += f"USER'S ADDITIONAL INSTRUCTIONS:\n{additional_instructions}\n\n"

        prompt += (
            "LAYOUT DIVERSITY RULES:\n"
            "Do NOT use 'bullet_list' on every slide. Incorporate an engaging variety of layouts:\n"
            "- Use 'two_column' for comparisons, trade-offs, or dual aspects.\n"
            "- Use 'stats_kpi' when presenting key metrics, milestones, or percentages.\n"
            "- Use 'table' or 'chart' when showing data, timelines, or benchmarks.\n"
            "- Use 'process_flow' when detailing a step-by-step roadmap or pipeline.\n"
            "- Use 'image_text' for slides requiring strong visual anchoring.\n"
            "- Never produce empty bullet lists.\n"
            "- Never output markdown code fences or commentary outside the JSON.\n"
            "Begin JSON output now:"
        )

        return prompt

    def generate_presentation(self, settings: Dict[str, Any]) -> Tuple[Optional[PresentationData], Optional[str]]:
        """Call Groq AI to generate presentation content.

        Returns:
            (PresentationData, error_message)
        """
        if not self.is_configured:
            return None, "Groq API Key is missing. Please provide it in the sidebar or your .env file."

        topic = settings.get("topic", "").strip()
        if not topic:
            return None, "Presentation topic cannot be empty."

        requested_slides = int(settings.get("slides", 10))
        creativity = float(settings.get("creativity", 0.7))
        # Clamp temperature between 0.0 and 1.0
        creativity = max(0.0, min(1.0, creativity))

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(settings)

        client = self._get_client()

        # Bounded retry mechanism (max 2 attempts for transient flaws)
        for attempt in range(2):
            try:
                logger.info("Calling Groq API (attempt %s) with model %s", attempt + 1, self.model)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=creativity,
                    max_tokens=8192,
                    response_format={"type": "json_object"}
                )

                raw_content = response.choices[0].message.content
                if not raw_content:
                    if attempt == 0:
                        continue
                    return None, "AI model returned an empty message."

                # Validate and parse
                presentation_data, val_err = parse_and_validate_response(
                    raw_response=raw_content,
                    requested_slides=requested_slides,
                    topic=topic,
                    include_toc=settings.get("include_toc", True),
                    include_conclusion=settings.get("include_conclusion", True),
                    include_references=settings.get("include_references", False),
                    include_title_slide=settings.get("include_title_slide", True),
                    include_ending_slide=settings.get("include_ending_slide", True)
                )

                if presentation_data:
                    return presentation_data, None

                logger.warning("Attempt %s JSON parsing failed: %s. Retrying...", attempt + 1, val_err)
                if attempt == 1:
                    return None, f"Could not generate valid presentation schema: {val_err}"

            except AuthenticationError:
                return None, "Groq Authentication Error: Invalid API key. Please check your credentials."
            except RateLimitError:
                return None, "Groq Rate Limit Exceeded: Please wait a few seconds before trying again."
            except APIConnectionError:
                return None, "Network Connection Error: Could not establish connection to Groq API."
            except GroqError as ge:
                err_str = str(ge)
                if ("model_not_found" in err_str or "does not exist" in err_str) and attempt == 0:
                    avail = self.get_available_models(self.api_key)
                    fallback_models = [m for m in avail if m != self.model]
                    if fallback_models:
                        fallback_model = fallback_models[0]
                        logger.warning(
                            "Model '%s' not found on endpoint. Automatically switching to '%s' and retrying...",
                            self.model, fallback_model
                        )
                        self.model = fallback_model
                        continue
                    return None, f"Model '{self.model}' is not available on this Groq account. Available models: {', '.join(avail[:5])}"
                return None, f"Groq Service Error: {err_str}"
            except Exception as e:
                logger.exception("Unexpected error during Groq generation")
                return None, f"Presentation generation failed: {str(e)}"

        return None, "Failed to generate presentation after multiple attempts."

    def regenerate_single_slide(
        self,
        presentation_title: str,
        slide: SlideContent,
        feedback: str = ""
    ) -> Tuple[Optional[SlideContent], Optional[str]]:
        """Regenerate a single slide with optional user feedback."""
        if not self.is_configured:
            return None, "Groq API Key is missing."

        prompt = (
            f"You are refining a single slide for the presentation '{presentation_title}'.\n"
            f"CURRENT SLIDE:\n"
            f"- Title: {slide.title}\n"
            f"- Current Layout: {slide.layout}\n"
            f"- Current Bullets: {json.dumps(slide.bullets)}\n\n"
            f"USER REFINEMENT INSTRUCTIONS: {feedback or 'Improve clarity, conciseness, and presentation quality.'}\n\n"
            "Return a single JSON object for this slide matching this schema:\n"
            "{\n"
            '  "title": "Refined Slide Title",\n'
            '  "layout": "bullet_list",\n'
            '  "key_message": "Core takeaway",\n'
            '  "bullets": ["Point 1", "Point 2", "Point 3"],\n'
            '  "speaker_notes": "Refined speaker script"\n'
            "}"
        )

        try:
            client = self._get_client()
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional presentation editor. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            raw = resp.choices[0].message.content
            from src.content_validator import extract_json_from_text, validate_slide_dict
            json_text = extract_json_from_text(raw)
            if json_text:
                slide_dict = json.loads(json_text)
                updated_slide = validate_slide_dict(slide_dict, (slide.slide_id or 1) - 1, presentation_title)
                return updated_slide, None
            return None, "Failed to parse single slide JSON."
        except Exception as e:
            return None, f"Slide regeneration failed: {str(e)}"


def generate_offline_sample(topic: str = "Artificial Intelligence", slide_count: int = 10) -> PresentationData:
    """Generate a high-quality offline sample presentation for tests or keyless preview."""
    from src.content_schema import (
        PresentationData, SlideContent, KpiMetric, ColumnData, TableData, ChartData, ChartSeries, ProcessStep
    )

    clean_topic = topic.strip() or "Modern AI Architectures"

    slides: List[SlideContent] = [
        SlideContent(
            slide_id=1,
            title=f"{clean_topic}: Strategic Overview",
            layout="title",
            key_message="Foundational principles, real-world deployment, and future horizon.",
            bullets=["A Comprehensive Technical & Strategic Presentation"],
            speaker_notes=f"Welcome. Today we will explore {clean_topic} in depth, from core mechanisms to scalable impact."
        ),
        SlideContent(
            slide_id=2,
            title="Agenda & Discussion Topics",
            layout="agenda",
            key_message="Roadmap of key dimensions covered across this presentation.",
            bullets=[
                "Executive Summary & Landscape",
                "Architectural Foundations",
                "Key Metrics & Operational Benchmarks",
                "Comparison: Traditional vs Next-Gen",
                "Step-by-Step Implementation Flow",
                "Strategic Outlook & Next Steps"
            ],
            speaker_notes="Here is an overview of our agenda covering core concepts, metrics, comparisons, and roadmaps."
        ),
        SlideContent(
            slide_id=3,
            title="Foundational Concepts & Principles",
            layout="bullet_list",
            key_message="Establishing the primary operational pillars and technological drivers.",
            bullets=[
                f"Distributed processing enables rapid parallel execution across {clean_topic} workloads.",
                "Automated feature extraction removes manual bottlenecks and human bias.",
                "Continuous feedback loops ensure adaptive accuracy and domain alignment.",
                "Standards-compliant integration allows seamless embedding into legacy stacks."
            ],
            speaker_notes="Let us review the foundational principles that empower modern scalable systems."
        ),
        SlideContent(
            slide_id=4,
            title="Performance Metrics & Benchmarks",
            layout="stats_kpi",
            key_message="Measurable efficiency and scalability validated across production environments.",
            stats=[
                KpiMetric(label="Inference Velocity", value="10x", detail="Speedup across enterprise clusters"),
                KpiMetric(label="Classification Accuracy", value="99.2%", detail="Benchmarked on industry datasets"),
                KpiMetric(label="Operational Cost", value="-45%", detail="Infrastructure optimization savings")
            ],
            bullets=["Quantifiable performance improvements observed across all operational tiers."],
            speaker_notes="Notice the quantifiable gains in velocity, accuracy, and overall cost reduction."
        ),
        SlideContent(
            slide_id=5,
            title="Architectural Comparison",
            layout="two_column",
            key_message="Evaluating traditional methodologies versus modern AI approaches.",
            columns=ColumnData(
                col1_title="Conventional Approach",
                col1_bullets=[
                    "Heuristic-based rule definitions with high manual tuning",
                    "Rigid schemas unable to gracefully absorb novel inputs",
                    "High maintenance overhead as complexity scales"
                ],
                col2_title="Modern Intelligent Framework",
                col2_bullets=[
                    "Self-optimizing representations derived directly from data",
                    "Dynamic contextual understanding and natural adaptability",
                    "Automated learning cycles with minimal manual intervention"
                ]
            ),
            speaker_notes="Here we juxtapose legacy rule systems with modern adaptive AI architectures."
        ),
        SlideContent(
            slide_id=6,
            title="Implementation Roadmap",
            layout="process_flow",
            key_message="Sequential milestones for deployment and continuous monitoring.",
            process_steps=[
                ProcessStep(step_number=1, title="Discovery", description="Analyze data readiness and requirements."),
                ProcessStep(step_number=2, title="Prototyping", description="Build validation model and baseline."),
                ProcessStep(step_number=3, title="Integration", description="Deploy containerized pipeline into staging."),
                ProcessStep(step_number=4, title="Optimization", description="Monitor real-time metrics and fine-tune.")
            ],
            speaker_notes="Following this four-stage pipeline guarantees robust and verifiable deployment."
        ),
        SlideContent(
            slide_id=7,
            title="Framework Evaluation Matrix",
            layout="table",
            key_message="Structured comparison of prominent platform characteristics.",
            table_data=TableData(
                headers=["Platform", "Latency", "Throughput", "Ease of Adoption"],
                rows=[
                    ["Enterprise Core", "< 15 ms", "10k req/sec", "High"],
                    ["Open Solution", "~ 30 ms", "4k req/sec", "Moderate"],
                    ["Custom Engine", "< 10 ms", "15k req/sec", "Specialized"]
                ]
            ),
            speaker_notes="This evaluation matrix summarizes latency, throughput, and developer ergonomics."
        ),
        SlideContent(
            slide_id=8,
            title="Growth & Adoption Trends",
            layout="chart",
            key_message="Tracking adoption velocity and computational throughput quarterly.",
            chart_data=ChartData(
                chart_type="column",
                title="Quarterly Adoption Volume",
                categories=["Q1", "Q2", "Q3", "Q4"],
                series=[
                    ChartSeries(name="Adoption Rate (%)", values=[32.0, 54.0, 78.0, 95.0])
                ]
            ),
            bullets=[
                "Consistent double-digit quarterly acceleration.",
                "Adoption inflection point achieved in Q3 across key verticals."
            ],
            speaker_notes="Adoption trends reflect sustained demand and compounding ecosystem value."
        ),
        SlideContent(
            slide_id=9,
            title="Conclusion & Strategic Takeaways",
            layout="conclusion",
            key_message="Key insights, operational recommendations, and future trajectory.",
            bullets=[
                f"{clean_topic} unlocks exponential productivity when strategically integrated.",
                "Disciplined architectural standards safeguard maintainability and compliance.",
                "Continuous iteration and metric tracking ensure compounding competitive advantage."
            ],
            speaker_notes="To wrap up, structured implementation and continuous iteration deliver sustained ROI."
        ),
        SlideContent(
            slide_id=10,
            title="Thank You & Q&A",
            layout="ending",
            key_message="Questions & Open Discussion",
            bullets=[
                f"Thank you for attending this session on {clean_topic}.",
                "We welcome your questions, thoughts, and technical discussions.",
                "Documentation & presentation resources are available upon request."
            ],
            speaker_notes="Thank you all for your time and active engagement. I invite your questions now."
        )
    ]

    # Trim or pad to requested slide count
    if slide_count < len(slides):
        title_slide = slides[0]
        end_slide = slides[-1]
        mid = slides[1:-1][:max(1, slide_count - 2)]
        slides = [title_slide] + mid + [end_slide]
    elif slide_count > len(slides):
        for extra_idx in range(len(slides), slide_count):
            slides.append(
                SlideContent(
                    slide_id=extra_idx + 1,
                    title=f"Strategic Insight {extra_idx + 1}",
                    layout="bullet_list",
                    key_message=f"Detailed perspective on dimension {extra_idx + 1}.",
                    bullets=[
                        f"Operational insight regarding {clean_topic}",
                        "Implementation best practice and risk mitigation",
                        "Key performance indicators for continuous verification"
                    ],
                    speaker_notes="Reviewing additional operational insights."
                )
            )

    # Renumber sequentially
    for i, s in enumerate(slides):
        s.slide_id = i + 1

    return PresentationData(
        title=clean_topic,
        subtitle=f"A Strategic Deep Dive into {clean_topic}",
        overview=f"Executive briefing on {clean_topic} architecture, deployment, and future potential.",
        target_audience="General Audience",
        key_objectives=[
            "Understand foundational concepts and mechanics",
            "Evaluate production metrics and benchmark data",
            "Establish an actionable implementation roadmap"
        ],
        slides=slides,
        metadata={"is_offline_sample": True, "slide_count": len(slides)}
    )

