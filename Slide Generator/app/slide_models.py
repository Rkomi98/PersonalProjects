"""Typed models passed to datapizza's structured responses and PPT builder."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SlideVisual(BaseModel):
    """Describe a suggested visual asset for the slide."""

    type: str = Field(
        ...,
        description="Tipo di visual da usare (grafico, illustrazione, icona, quote, timeline).",
    )
    description: str = Field(
        ..., description="Spiega cosa dovrebbe mostrare il visual in massimo 2 frasi."
    )
    svg_markup: str | None = Field(
        default=None,
        description="SVG inline completo (<svg>...</svg>) in stile Datapizza o null se non necessario.",
    )
    caption: str | None = Field(
        default=None,
        description="Breve descrizione da mostrare in slide accanto all'SVG.",
    )


class SlideContent(BaseModel):
    """Single slide specification returned by the LLM."""

    layout: str = Field(
        default="split",
        description=(
            "Layout suggerito: 'text_only', 'split' (testo+visual) oppure 'visual_full' "
            "per slide guidata interamente dal visual."
        ),
    )
    title: str = Field(
        ..., description="Titolo della slide in sentence case massimo 8 parole."
    )
    key_message: str | None = Field(
        default=None,
        description="Frase incisiva che riassume il valore principale della slide.",
    )
    bullets: list[str] = Field(
        default_factory=list,
        description="Elenco di bullet point brevi (max 14 parole) già pronti per la slide.",
    )
    insights: list[str] | None = Field(
        default=None,
        description="Approfondimenti opzionali con dati/quote per dare autorevolezza alla slide.",
    )
    visual: SlideVisual | None = Field(
        default=None,
        description="Suggerimento del visual da inserire nella slide.",
    )
    speaker_notes: str | None = Field(
        default=None,
        description="Note per lo speaker con tono colloquiale (massimo 3 frasi).",
    )


class SlideDeck(BaseModel):
    """Overall structure of the deck produced by the LLM."""

    deck_title: str = Field(..., description="Titolo della presentazione per la cover.")
    subtitle: str | None = Field(
        default=None, description="Sottotitolo o payoff della presentazione."
    )
    summary: str = Field(
        ..., description="Paragrafo introduttivo di massimo 60 parole riassuntive."
    )
    slides: list[SlideContent] = Field(
        ..., description="Lista ordinata di slide dalla intro alla chiusura."
    )
    closing_message: str | None = Field(
        default=None, description="Ultimo messaggio o call-to-action della presentazione."
    )

    @property
    def cover_title(self) -> str:
        return self.deck_title

    @property
    def cover_subtitle(self) -> str:
        return self.subtitle or ""
