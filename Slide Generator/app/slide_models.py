"""Typed models for Datapizza slide generation and PPT assembly."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class SlideType(str, Enum):
    """Supported Datapizza slide categories."""

    TITLE = "title"
    SECTION = "section"
    CONTENT = "content"
    BULLETS = "bullets"
    CLOSING = "closing"


class DatapizzaSlide(BaseModel):
    """Single slide in the Claude/Gemini handoff format requested by the user."""

    slide_type: SlideType = Field(..., description="Tipo della slide.")
    title: str = Field(..., description="Titolo della slide.")
    subtitle: str | None = Field(
        default=None,
        description="Sottotitolo opzionale, usato solo per title o section.",
    )
    body: str | None = Field(
        default=None,
        description="Testo principale della slide, massimo 3 righe per una content slide.",
    )
    bullets: list[str] = Field(
        default_factory=list,
        description="Elenco puntato, massimo 4 elementi.",
    )
    speaker_notes: str = Field(
        ...,
        description="Note per il relatore, aggiuntive rispetto al contenuto visivo.",
    )
    image_prompt: str = Field(
        ...,
        description=(
            "Prompt dettagliato per generare un SVG illustrativo in stile Datapizza. "
            "Deve includere canvas 'SVG 800x500px, viewBox 0 0 800 500'."
        ),
    )

    @property
    def is_internal(self) -> bool:
        return self.slide_type in {SlideType.CONTENT, SlideType.BULLETS}

    @model_validator(mode="after")
    def validate_shape(self) -> "DatapizzaSlide":
        if self.slide_type in {SlideType.TITLE, SlideType.SECTION}:
            self.bullets = []
            self.body = self.body or None
        if self.slide_type == SlideType.CONTENT:
            self.bullets = []
        if self.slide_type == SlideType.BULLETS:
            self.body = self.body or None
            self.bullets = self.bullets[:4]
        if self.slide_type == SlideType.CLOSING:
            self.subtitle = self.subtitle or None
            self.bullets = []
            self.body = self.body or None
        return self


class SlideDeck(BaseModel):
    """Structured container returned by datapizza-AI."""

    slides: list[DatapizzaSlide] = Field(
        ...,
        description="Array ordinato delle slide della presentazione.",
    )

    def as_output_array(self) -> list[dict]:
        """Return the exact array shape expected downstream."""
        return [slide.model_dump(mode="json") for slide in self.slides]
