"""Utilities to load the Datapizza prompt context."""
from __future__ import annotations

from pathlib import Path
import zipfile


DEFAULT_STYLE_PROMPT = """# Datapizza Base Prompt

## Obiettivo
- Crea deck chiari, tech, diretti, con un solo messaggio per slide.
- Segui il principio data-ink ratio: poco rumore, molto significato.

## Branding
- Slide content title in blu Datapizza `#1B64F5`.
- Section/title slide con identita brand pulita e uso controllato del rosso `#C64336`.
- Testo base in navy `#111F2D` / `#0D1F2E`, sfondo bianco.

## Segmentazione
- H1 = slide `title` o `section`.
- H2/H3 = slide `content` o `bullets`.
- Massimo 5-6 slide per ogni H1 del markdown originale.
- Ultima slide sempre `closing`.

## Visual
- Ogni slide deve avere un `image_prompt` diverso.
- Per slide `content` e `bullets`, il visual deve essere un SVG flat, minimalista, vettoriale.
- Scrivi sempre nel prompt: `SVG 800x500px, viewBox 0 0 800 500`.
"""


def load_style_prompt(prompt_path: Path) -> str:
    """Return the content of the prompt file or a sensible default."""
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    return DEFAULT_STYLE_PROMPT


def load_datapizza_skill_context(skill_path: Path) -> str:
    """Extract the most relevant guidance from the packaged Datapizza skill zip."""
    if not skill_path.exists():
        return ""

    try:
        with zipfile.ZipFile(skill_path) as archive:
            skill_md = archive.read("datapizza-slides/SKILL.md").decode("utf-8").strip()
            style_md = archive.read(
                "datapizza-slides/resources/dp-01-style.md"
            ).decode("utf-8")
            workflow_md = archive.read(
                "datapizza-slides/resources/dp-03-workflow.md"
            ).decode("utf-8")
    except Exception:
        return ""

    style_excerpt = style_md[:5000].strip()
    workflow_excerpt = workflow_md[:3500].strip()
    return "\n\n".join(
        [
            "# Datapizza Skill Context",
            skill_md,
            "# Skill Style Excerpt",
            style_excerpt,
            "# Skill Workflow Excerpt",
            workflow_excerpt,
        ]
    )
