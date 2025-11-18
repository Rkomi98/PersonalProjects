"""Application level configuration helpers."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppSettings:
    """Centralised configuration used across the slide generator."""

    base_dir: Path
    asset_dir: Path
    topic_dir: Path
    prompt_path: Path
    layout_plan_path: Path
    logo_path: Path
    cover_logo_path: Path
    output_dir: Path
    svg_output_dir: Path
    openai_api_key: str
    openai_model: str
    default_slide_count: int = 8
    temperature: float = 0.4


def load_settings(
    *,
    env_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    model_name: Optional[str] = None,
) -> AppSettings:
    """Load settings from the .env file and optional overrides."""

    base_dir = Path(__file__).resolve().parents[1]
    env_file = env_path or (base_dir / ".env")
    if env_file.exists():
        load_dotenv(env_file)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY non trovato. Imposta la variabile nell'.env o nell'ambiente."
        )

    selected_model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    asset_dir = base_dir / "Asset"
    topic_dir = base_dir / "Topic"
    prompt_path = asset_dir / "prompt.md"
    layout_plan_path = asset_dir / "layouts.json"
    logo_path = asset_dir / "datapizzaLogo.png"
    cover_logo_path = asset_dir / "datapizza.png"
    resolved_output_dir = output_dir or (base_dir / "output")
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    svg_output_dir = resolved_output_dir / "svg"
    svg_output_dir.mkdir(parents=True, exist_ok=True)

    return AppSettings(
        base_dir=base_dir,
        asset_dir=asset_dir,
        topic_dir=topic_dir,
        prompt_path=prompt_path,
        layout_plan_path=layout_plan_path,
        logo_path=logo_path,
        cover_logo_path=cover_logo_path,
        output_dir=resolved_output_dir,
        svg_output_dir=svg_output_dir,
        openai_api_key=api_key,
        openai_model=selected_model,
    )
