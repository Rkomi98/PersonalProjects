"""Helpers to export Gemini prompt files and resolve generated SVG assets."""
from __future__ import annotations

import json
from pathlib import Path

from .slide_models import DatapizzaSlide


class GeminiAssetManager:
    """Create prompt files for Gemini and track expected SVG outputs."""

    def __init__(self, *, prompt_dir: Path, asset_dir: Path):
        self.prompt_dir = prompt_dir
        self.asset_dir = asset_dir

    def export(self, slides: list[DatapizzaSlide]) -> Path:
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
        self.asset_dir.mkdir(parents=True, exist_ok=True)

        manifest: list[dict] = []
        for index, slide in enumerate(slides, start=1):
            prompt_path = self.prompt_dir / f"slide_{index:02d}.txt"
            asset_path = self.asset_dir / f"slide_{index:02d}.svg"
            if slide.is_internal:
                prompt_path.write_text(slide.image_prompt.strip() + "\n", encoding="utf-8")
            manifest.append(
                {
                    "slide_number": index,
                    "slide_type": slide.slide_type.value,
                    "title": slide.title,
                    "prompt_file": str(prompt_path) if slide.is_internal else None,
                    "expected_svg_file": str(asset_path),
                    "uses_gemini_visual": slide.is_internal,
                }
            )

        manifest_path = self.prompt_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest_path

    def resolve_svg_for_slide(self, slide_index: int) -> Path | None:
        svg_path = self.asset_dir / f"slide_{slide_index:02d}.svg"
        return svg_path if svg_path.exists() else None
