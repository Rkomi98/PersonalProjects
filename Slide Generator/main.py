#!/usr/bin/env python3
"""CLI che genera slide Datapizza JSON + PPTX usando datapizza-AI."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from app import (
    GeminiAssetManager,
    SlideDeckWriter,
    SlideGenerationService,
    SlideStyle,
    load_datapizza_skill_context,
    load_settings,
    load_style_prompt,
)
from app.slide_service import SlideGeneratorConfig


def _discover_topic_file(topic_dir: Path) -> Optional[Path]:
    candidates = sorted(topic_dir.glob("*"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _read_topic_text(args: argparse.Namespace, topic_dir: Path) -> str:
    if args.topic:
        return args.topic

    topic_path = args.topic_file or _discover_topic_file(topic_dir)
    if topic_path is None or not topic_path.exists():
        raise FileNotFoundError(
            "Nessun brief trovato. Usa --topic oppure indica un file con --topic-file."
        )

    return topic_path.read_text(encoding="utf-8").strip()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera slide Datapizza da Markdown")
    parser.add_argument("--topic", type=str, help="Testo Markdown del brief")
    parser.add_argument(
        "--topic-file",
        type=Path,
        help="File Markdown da cui leggere il brief (default: primo file nella cartella Topic)",
    )
    parser.add_argument(
        "--slides",
        type=int,
        help="Numero indicativo di slide target",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="Italiano",
        help="Lingua della presentazione",
    )
    parser.add_argument("--model", type=str, help="Override del modello OpenAI")
    parser.add_argument("--output", type=Path, help="Percorso output PPTX")
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Percorso output del JSON slide",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Stampa solo l'array JSON generato",
    )
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    settings = load_settings(model_name=args.model)
    markdown_text = _read_topic_text(args, settings.topic_dir)
    requested_slides = args.slides or SlideGenerationService.suggest_slide_count(markdown_text)

    style_prompt = load_style_prompt(settings.prompt_path)
    skill_context = load_datapizza_skill_context(settings.datapizza_skill_path)

    config = SlideGeneratorConfig(
        api_key=settings.openai_api_key,
        model_name=args.model or settings.openai_model,
        system_prompt=(
            "Sei un assistente specializzato nella creazione di presentazioni Datapizza. "
            "Produci esclusivamente output strutturato, sintetico e pronto per un deck PPTX."
        ),
        temperature=settings.temperature,
        style_prompt=style_prompt,
        skill_context=skill_context,
    )

    service = SlideGenerationService(config)
    deck = service.generate(
        markdown_text=markdown_text,
        requested_slides=requested_slides,
        language=args.language,
    )

    slide_array = deck.as_output_array()
    if args.dry_run:
        print(json.dumps(slide_array, ensure_ascii=False, indent=2))
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    json_output_path = args.json_output or (settings.output_dir / f"slides_{timestamp}.json")
    json_output_path.write_text(
        json.dumps(slide_array, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    gemini_manager = GeminiAssetManager(
        prompt_dir=settings.gemini_prompt_dir,
        asset_dir=settings.gemini_asset_dir,
    )
    manifest_path = gemini_manager.export(deck.slides)

    writer = SlideDeckWriter(
        style=SlideStyle(),
        logo_path=settings.logo_path,
        cover_logo_path=settings.cover_logo_path,
        svg_output_dir=settings.svg_output_dir,
        gemini_asset_manager=gemini_manager,
    )
    output_path = args.output or (settings.output_dir / f"deck_{timestamp}.pptx")
    pptx_path = writer.build(deck, output_path)

    print(f"JSON slide salvato in: {json_output_path}")
    print(f"Prompt Gemini salvati in: {settings.gemini_prompt_dir}")
    print(f"Manifest Gemini salvato in: {manifest_path}")
    print(f"SVG Gemini attesi in: {settings.gemini_asset_dir}")
    print(f"Presentazione salvata in: {pptx_path}")


if __name__ == "__main__":
    main()
