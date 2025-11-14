"""Slide generation package wiring datapizza-AI with custom PPT output."""

from .settings import AppSettings, load_settings
from .slide_models import SlideContent, SlideDeck, SlideVisual
from .slide_service import SlideGenerationService
from .ppt_builder import SlideDeckWriter, SlideStyle
from .prompts import load_style_prompt

__all__ = [
    "AppSettings",
    "SlideContent",
    "SlideDeck",
    "SlideDeckWriter",
    "SlideGenerationService",
    "SlideStyle",
    "SlideVisual",
    "load_settings",
    "load_style_prompt",
]
