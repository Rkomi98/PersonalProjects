"""PPTX builder backed by PptxGenJS to preserve SVG assets in the package."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class PptxGenJSWriter:
    """Write a PPTX by delegating to the local Node/PptxGenJS builder."""

    script_path: Path
    logo_path: Path
    cover_logo_path: Path
    gemini_asset_dir: Path

    def build(self, *, slides_json_path: Path, output_path: Path) -> Path:
        node_bin = shutil.which("node")
        if not node_bin:
            raise RuntimeError("Node.js non trovato nel PATH.")
        if not self.script_path.exists():
            raise RuntimeError(f"Builder PptxGenJS non trovato: {self.script_path}")

        target = output_path if output_path.suffix else output_path.with_suffix(".pptx")
        target.parent.mkdir(parents=True, exist_ok=True)

        command = [
            node_bin,
            str(self.script_path),
            str(slides_json_path),
            str(target),
            str(self.logo_path),
            str(self.cover_logo_path),
            str(self.gemini_asset_dir),
        ]
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(stderr or "Builder PptxGenJS fallito.")
        if not target.exists():
            raise RuntimeError("Il builder PptxGenJS non ha prodotto il file PPTX atteso.")
        return target
