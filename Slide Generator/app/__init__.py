"""Slide generation package wiring datapizza-AI with custom PPT output."""

from .settings import AppSettings, load_settings
from .layouts import load_layout_plan
from .gemini_assets import GeminiAssetManager
from .gemini_service import GeminiGeneratorConfig, GeminiSVGService
from .slide_models import DatapizzaSlide, SlideDeck, SlideType
from .slide_service import SlideGenerationService
from .ppt_builder import SlideDeckWriter, SlideStyle
from .pptxgen_writer import PptxGenJSWriter
from .prompts import load_datapizza_skill_context, load_style_prompt

__all__ = [
    "AppSettings",
    "DatapizzaSlide",
    "GeminiAssetManager",
    "GeminiGeneratorConfig",
    "GeminiSVGService",
    "SlideDeck",
    "SlideDeckWriter",
    "SlideGenerationService",
    "SlideStyle",
    "SlideType",
    "PptxGenJSWriter",
    "load_datapizza_skill_context",
    "load_settings",
    "load_style_prompt",
    "load_layout_plan",
]
