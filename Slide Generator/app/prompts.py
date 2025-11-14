"""Utilities to work with the slide style prompt."""
from __future__ import annotations

from pathlib import Path


DEFAULT_STYLE_PROMPT = """# Caratteristiche delle slides\nSfondo bianco (#FFFFFF) e stile minimal.\nColori: accento rosso scuro (#C12A22), titoli #1E293B, corpo #475569.\nTipografia: Titoli in Poppins Bold, testo in Lato Regular.\nSentence case per tutti i titoli di slide."""


def load_style_prompt(prompt_path: Path) -> str:
    """Return the content of the prompt file or a sensible default."""
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()

    return DEFAULT_STYLE_PROMPT
