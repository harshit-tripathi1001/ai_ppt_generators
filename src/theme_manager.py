"""Theme manager module for PowerPoint presentations.

Defines cohesive color palettes, typography scales, shape styling,
and visual aesthetics for light and dark presentation designs.
"""

from typing import Dict, List, NamedTuple
from pptx.dml.color import RGBColor


class ThemePalette(NamedTuple):
    """Color palette and visual styling configuration for a presentation theme."""
    name: str
    is_dark: bool
    bg_color: RGBColor
    card_bg: RGBColor
    card_border: RGBColor
    primary: RGBColor
    secondary: RGBColor
    title_text: RGBColor
    body_text: RGBColor
    muted_text: RGBColor
    accent_bar: RGBColor
    chart_palette: List[RGBColor]


# Themes definition
THEMES: Dict[str, ThemePalette] = {
    "Blue Modern": ThemePalette(
        name="Blue Modern",
        is_dark=False,
        bg_color=RGBColor(246, 249, 252),        # #F6F9FC Soft light blue-gray
        card_bg=RGBColor(255, 255, 255),         # #FFFFFF Crisp white
        card_border=RGBColor(226, 232, 240),     # #E2E8F0 Subtle border
        primary=RGBColor(30, 64, 175),           # #1E40AF Deep Navy Blue
        secondary=RGBColor(14, 165, 233),        # #0EA5E9 Sky Cyan
        title_text=RGBColor(15, 23, 42),         # #0F172A Near black
        body_text=RGBColor(51, 65, 85),          # #334155 Slate
        muted_text=RGBColor(100, 116, 139),      # #64748B Muted slate
        accent_bar=RGBColor(37, 99, 235),        # #2563EB Vivid Royal Blue
        chart_palette=[
            RGBColor(37, 99, 235),               # Royal Blue
            RGBColor(14, 165, 233),              # Sky Cyan
            RGBColor(99, 102, 241),              # Indigo
            RGBColor(16, 185, 129),              # Emerald
            RGBColor(245, 158, 11)               # Amber
        ]
    ),
    "Dark Elegance": ThemePalette(
        name="Dark Elegance",
        is_dark=True,
        bg_color=RGBColor(15, 23, 42),           # #0F172A Deep Midnight
        card_bg=RGBColor(30, 41, 59),            # #1E293B Dark Slate Card
        card_border=RGBColor(51, 65, 85),        # #334155 Border
        primary=RGBColor(129, 140, 248),         # #818CF8 Bright Indigo
        secondary=RGBColor(56, 189, 248),        # #38BDF8 Light Cyan
        title_text=RGBColor(248, 250, 252),      # #F8FAFC Off-white
        body_text=RGBColor(226, 232, 240),       # #E2E8F0 Soft light slate
        muted_text=RGBColor(148, 163, 184),      # #94A3B8 Muted slate
        accent_bar=RGBColor(99, 102, 241),       # #6366F1 Vivid Indigo
        chart_palette=[
            RGBColor(129, 140, 248),             # Indigo
            RGBColor(56, 189, 248),              # Cyan
            RGBColor(52, 211, 153),              # Emerald
            RGBColor(251, 146, 60),              # Orange
            RGBColor(244, 114, 182)              # Pink
        ]
    ),
    "Emerald Green": ThemePalette(
        name="Emerald Green",
        is_dark=False,
        bg_color=RGBColor(244, 249, 246),        # #F4F9F6 Mint whisper
        card_bg=RGBColor(255, 255, 255),         # #FFFFFF White card
        card_border=RGBColor(209, 231, 221),     # Soft mint border
        primary=RGBColor(6, 95, 70),             # #065F46 Deep Emerald
        secondary=RGBColor(16, 185, 129),        # #10B981 Emerald Accent
        title_text=RGBColor(6, 78, 59),          # #064E3B Dark Forest
        body_text=RGBColor(47, 79, 79),          # #2F4F4F Slate green
        muted_text=RGBColor(107, 142, 120),      # #6B8E78 Muted green
        accent_bar=RGBColor(5, 150, 105),        # #059669 Vibrant Emerald
        chart_palette=[
            RGBColor(5, 150, 105),               # Emerald
            RGBColor(16, 185, 129),              # Mint
            RGBColor(13, 148, 136),              # Teal
            RGBColor(132, 204, 22),              # Lime
            RGBColor(245, 158, 11)               # Amber
        ]
    ),
    "Royal Purple": ThemePalette(
        name="Royal Purple",
        is_dark=False,
        bg_color=RGBColor(249, 247, 254),        # Soft lilac tint
        card_bg=RGBColor(255, 255, 255),         # White
        card_border=RGBColor(233, 223, 248),     # Lilac border
        primary=RGBColor(107, 33, 168),          # #6B21A8 Royal Purple
        secondary=RGBColor(168, 85, 247),        # #A855F7 Bright violet
        title_text=RGBColor(59, 7, 100),         # #3B0764 Deep Violet
        body_text=RGBColor(74, 58, 92),          # Eggplant slate
        muted_text=RGBColor(139, 123, 158),      # Muted lavender
        accent_bar=RGBColor(126, 34, 206),       # Vivid purple
        chart_palette=[
            RGBColor(126, 34, 206),              # Purple
            RGBColor(168, 85, 247),              # Violet
            RGBColor(236, 72, 153),              # Pink
            RGBColor(79, 70, 229),               # Indigo
            RGBColor(14, 165, 233)               # Cyan
        ]
    ),
    "Sunset Warmth": ThemePalette(
        name="Sunset Warmth",
        is_dark=False,
        bg_color=RGBColor(254, 248, 245),        # Warm off-white
        card_bg=RGBColor(255, 255, 255),         # White
        card_border=RGBColor(254, 215, 195),     # Warm border
        primary=RGBColor(194, 65, 12),           # #C2410C Deep Orange
        secondary=RGBColor(249, 115, 22),        # #F97316 Vivid Coral
        title_text=RGBColor(67, 20, 7),          # #431407 Warm dark brown
        body_text=RGBColor(87, 43, 26),          # Warm slate
        muted_text=RGBColor(154, 103, 83),       # Muted terracotta
        accent_bar=RGBColor(234, 88, 12),        # Coral Orange
        chart_palette=[
            RGBColor(234, 88, 12),               # Coral
            RGBColor(245, 158, 11),              # Amber
            RGBColor(239, 68, 68),               # Crimson
            RGBColor(217, 119, 6),               # Warm Gold
            RGBColor(99, 102, 241)               # Indigo contrast
        ]
    ),
    "Crimson Slate": ThemePalette(
        name="Crimson Slate",
        is_dark=True,
        bg_color=RGBColor(24, 24, 27),           # #18181B Zinc Dark
        card_bg=RGBColor(39, 39, 42),            # #27272A Zinc Card
        card_border=RGBColor(63, 63, 70),        # Zinc Border
        primary=RGBColor(244, 63, 94),           # #F43F5E Rose Red
        secondary=RGBColor(251, 113, 133),       # #FB7185 Soft Rose
        title_text=RGBColor(250, 250, 250),      # Crisp White
        body_text=RGBColor(228, 228, 231),       # Soft Zinc
        muted_text=RGBColor(161, 161, 170),      # Muted Zinc
        accent_bar=RGBColor(225, 29, 72),        # Bold Rose
        chart_palette=[
            RGBColor(244, 63, 94),               # Rose
            RGBColor(251, 146, 60),              # Orange
            RGBColor(168, 85, 247),              # Purple
            RGBColor(56, 189, 248),              # Cyan
            RGBColor(52, 211, 153)               # Emerald
        ]
    ),
    "Light Minimal": ThemePalette(
        name="Light Minimal",
        is_dark=False,
        bg_color=RGBColor(255, 255, 255),        # Pure White
        card_bg=RGBColor(248, 250, 252),         # Subtle slate tint
        card_border=RGBColor(226, 232, 240),     # Slate border
        primary=RGBColor(15, 23, 42),            # Dark Charcoal
        secondary=RGBColor(71, 85, 105),         # Medium Slate
        title_text=RGBColor(15, 23, 42),         # Dark Charcoal
        body_text=RGBColor(51, 65, 85),          # Slate Body
        muted_text=RGBColor(148, 163, 184),      # Slate Muted
        accent_bar=RGBColor(37, 99, 235),        # Blue Accent
        chart_palette=[
            RGBColor(15, 23, 42),                # Charcoal
            RGBColor(71, 85, 105),               # Slate
            RGBColor(37, 99, 235),               # Royal Blue
            RGBColor(16, 185, 129),              # Emerald
            RGBColor(245, 158, 11)               # Amber
        ]
    )
}

# Alias mapping to ensure flexible selection from UI
THEME_ALIASES = {
    "blue": "Blue Modern",
    "dark": "Dark Elegance",
    "green": "Emerald Green",
    "purple": "Royal Purple",
    "sunset": "Sunset Warmth",
    "orange": "Sunset Warmth",
    "red": "Crimson Slate",
    "crimson": "Crimson Slate",
    "light": "Light Minimal",
    "minimalist": "Light Minimal"
}


def get_theme_palette(theme_name: str) -> ThemePalette:
    """Retrieve the ThemePalette matching the requested theme name.

    Defaults to 'Blue Modern' if not found.
    """
    if not theme_name:
        return THEMES["Blue Modern"]

    # Direct match
    if theme_name in THEMES:
        return THEMES[theme_name]

    # Alias / lowercase lookup
    cleaned = theme_name.strip().lower()
    for key, target in THEME_ALIASES.items():
        if key in cleaned:
            return THEMES[target]

    # Default fallback
    return THEMES["Blue Modern"]


def get_available_theme_names() -> List[str]:
    """Get list of displayable theme names."""
    return list(THEMES.keys())

