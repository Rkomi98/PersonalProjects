#!/usr/bin/env python3
"""CLI che genera una presentazione PPTX usando datapizza-AI e OpenAI."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from app import (
    SlideDeckWriter,
    SlideGenerationService,
    SlideStyle,
    load_settings,
    load_style_prompt,
)
from app.layout_planner import (
    LayoutPlanGenerator,
    LayoutPlanGeneratorConfig,
    describe_proposal,
    proposal_to_plan_data,
)
from app.layouts import LayoutPlan, load_layout_data_or_default, parse_layout_data
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

    topic_path: Optional[Path] = None
    if args.topic_file:
        topic_path = args.topic_file
    else:
        topic_path = _discover_topic_file(topic_dir)

    if topic_path is None or not topic_path.exists():
        raise FileNotFoundError(
            "Nessun brief trovato. Usa --topic oppure indica un file con --topic-file."
        )

    return topic_path.read_text(encoding="utf-8").strip()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera slide brandizzate Datapizza")
    parser.add_argument(
        "--topic",
        type=str,
        help="Testo del brief. Se fornito ha priorità sul file",
    )
    parser.add_argument(
        "--topic-file",
        type=Path,
        help="File da cui leggere il brief (default: primo file nella cartella Topic)",
    )
    parser.add_argument(
        "--slides",
        type=int,
        help="Numero di slide (default definito nelle impostazioni)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="Italiano",
        help="Lingua della presentazione",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Override del modello OpenAI",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Percorso di output del file PPTX",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Stampa il JSON generato senza creare il PPT",
    )
    parser.add_argument(
        "--layout-plan",
        type=Path,
        help="File JSON con i template layout da applicare (default: Asset/layouts.json)",
    )
    return parser


def _ask_yes_no(question: str, *, default: bool = True) -> bool:
    default_hint = "Y/n" if default else "y/N"
    answer = input(f"{question} [{default_hint}]: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes", "s", "si", "sì"}


def _print_plan_summary(plan: LayoutPlan, plan_path: Path) -> None:
    print(f"\nLayout plan: {plan_path}")
    for line in plan.summary_lines():
        print(f"  - {line}")
    print()


def _generate_layout_plan_with_llm(
    *,
    layout_path: Path,
    layout_data: dict,
    template_plan: LayoutPlan,
    topic_text: str,
    requested_slides: int,
    config: SlideGeneratorConfig,
) -> LayoutPlan:
    print("Creo un nuovo layout plan con l'LLM...")
    generator = LayoutPlanGenerator(
        LayoutPlanGeneratorConfig(
            api_key=config.api_key,
            model_name=config.model_name,
            temperature=config.temperature,
        )
    )
    proposal = generator.generate(
        topic=topic_text,
        requested_slides=requested_slides,
        template_options=template_plan.templates,
    )
    print(describe_proposal(proposal))
    if not _ask_yes_no("Vuoi salvare questo piano layout e procedere?", default=True):
        raise SystemExit("Esecuzione annullata: layout plan non confermato.")

    new_data = proposal_to_plan_data(
        proposal=proposal,
        existing_templates=layout_data.get("templates", {}),
        requested_slides=requested_slides,
    )
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    layout_path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2))
    print(f"Nuovo layout salvato in: {layout_path}\n")
    return parse_layout_data(new_data)


def _prepare_layout_plan(
    *,
    layout_path: Path,
    topic_text: str,
    requested_slides: int,
    config: SlideGeneratorConfig,
) -> LayoutPlan:
    layout_data = load_layout_data_or_default(layout_path)
    plan = parse_layout_data(layout_data)
    if layout_path.exists():
        _print_plan_summary(plan, layout_path)
        if _ask_yes_no("Utilizzare questo layout plan?", default=True):
            return plan
        print("Rigenerazione layout richiesta dall'utente.")
    else:
        print("Nessun layout plan trovato. Verrà generato automaticamente.")

    new_plan = _generate_layout_plan_with_llm(
        layout_path=layout_path,
        layout_data=layout_data,
        template_plan=plan,
        topic_text=topic_text,
        requested_slides=requested_slides,
        config=config,
    )
    _print_plan_summary(new_plan, layout_path)
    return new_plan


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    settings = load_settings(model_name=args.model)
    topic_text = _read_topic_text(args, settings.topic_dir)
    requested_slides = args.slides or settings.default_slide_count

    style_prompt = load_style_prompt(settings.prompt_path)
    config = SlideGeneratorConfig(
        api_key=settings.openai_api_key,
        model_name=args.model or settings.openai_model,
        system_prompt=(
            "Sei una presentation designer senior. Costruisci deck coerenti, data-driven, "
            "con tono consulenziale e messaggi chiari."
        ),
        temperature=settings.temperature,
        style_prompt=style_prompt,
    )

    layout_plan_path = args.layout_plan or settings.layout_plan_path
    layout_plan = _prepare_layout_plan(
        layout_path=layout_plan_path,
        topic_text=topic_text,
        requested_slides=requested_slides,
        config=config,
    )

    service = SlideGenerationService(config)
    deck = service.generate(
        topic=topic_text,
        requested_slides=requested_slides,
        language=args.language,
    )

    if args.dry_run:
        print(json.dumps(deck.model_dump(), ensure_ascii=False, indent=2))
        return

    writer = SlideDeckWriter(
        style=SlideStyle(),
        logo_path=settings.logo_path,
        cover_logo_path=settings.cover_logo_path,
        svg_output_dir=settings.svg_output_dir,
        layout_plan=layout_plan,
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = args.output or (settings.output_dir / f"deck_{timestamp}.pptx")
    pptx_path = writer.build(deck, output_path)
    print(f"Presentazione salvata in: {pptx_path}")


if __name__ == "__main__":
    main()
