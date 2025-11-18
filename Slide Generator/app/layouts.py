"""Layout configuration utilities loaded from JSON."""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_LAYOUT_DATA: Dict[str, Any] = {
    "templates": {
        "split_story": {
            "description": "Bullets a sinistra e visual a destra, come nelle slide Datapizza.",
            "aliases": ["split", "split_left"],
            "decorations": {"circle": "bottom_right", "underline": True, "key_box": True},
            "blocks": [
                {"type": "bullets", "x": 0.8, "y": 3.0, "width": 6.3, "style": "badges", "max_items": 5},
                {"type": "visual", "x": 7.8, "y": 2.8, "width": 4.6, "height": 3.8},
                {"type": "insights", "x": 0.8, "y": 6.5, "width": 6.3, "height": 1.6},
            ],
        },
        "text_story": {
            "description": "Slide narrativa solo testo con bullets e note finali.",
            "aliases": ["text_only", "text"],
            "decorations": {"circle": "top_left", "underline": True, "key_box": True},
            "blocks": [
                {"type": "bullets", "x": 0.8, "y": 3.0, "width": 11.0, "style": "simple", "max_items": 6},
                {"type": "insights", "x": 0.8, "y": 6.8, "width": 11.0, "height": 1.5},
            ],
        },
        "visual_showcase": {
            "description": "Slide focalizzata sul visual SVG con caption e micro bullets.",
            "aliases": ["visual_full", "visual", "svg_only"],
            "decorations": {"circle": "bottom_left", "underline": True, "key_box": False},
            "blocks": [
                {"type": "visual", "x": 0.8, "y": 2.2, "width": 11.5, "height": 4.5},
                {"type": "bullets", "x": 0.8, "y": 6.9, "width": 11.5, "style": "simple", "max_items": 3},
            ],
        },
        "card_grid": {
            "description": "Matrice di card con icona per raccontare componenti o fasi.",
            "aliases": ["cards", "highlights"],
            "decorations": {"circle": "bottom_right", "underline": True, "key_box": True},
            "blocks": [
                {"type": "cards", "x": 0.8, "y": 3.0, "width": 11.0, "columns": 2, "card_height": 2.1, "max_items": 4}
            ],
        },
    },
    "slide_plan": {
        "default": "split_story",
        "overrides": {"1": "split_story", "2": "text_story", "3": "visual_showcase", "4": "card_grid"},
        "plan_title": "Baseline split layout",
        "notes": "Layout iniziale usato come fallback nel caso non sia disponibile un piano personalizzato.",
    },
}


@dataclass(frozen=True)
class LayoutBlock:
    type: str
    x: float
    y: float
    width: float
    height: Optional[float] = None
    style: Optional[str] = None
    columns: Optional[int] = None
    card_height: Optional[float] = None
    max_items: Optional[int] = None


@dataclass(frozen=True)
class LayoutTemplate:
    name: str
    description: Optional[str]
    blocks: List[LayoutBlock]
    decorations: Dict[str, Any]
    aliases: List[str]


@dataclass(frozen=True)
class LayoutPlan:
    templates: Dict[str, LayoutTemplate]
    default_template: str
    overrides: Dict[int, str]
    alias_map: Dict[str, str]
    plan_title: Optional[str] = None
    notes: Optional[str] = None

    def resolve_template(self, slide_index: int, requested_layout: Optional[str]) -> LayoutTemplate:
        candidate = self.overrides.get(slide_index)
        if not candidate and requested_layout:
            normalized = requested_layout.lower().strip()
            candidate = self.alias_map.get(normalized, normalized)
        if not candidate or candidate not in self.templates:
            candidate = self.default_template
        return self.templates[candidate]

    def summary_lines(self) -> List[str]:
        title = self.plan_title or "Piano layout non specificato"
        lines = [title, f"Default layout: {self.default_template}"]
        if self.overrides:
            override_bits = ", ".join(
                f"Slide {idx}->{name}" for idx, name in sorted(self.overrides.items())
            )
            lines.append(f"Overrides: {override_bits}")
        else:
            lines.append("Overrides: nessuno")
        if self.notes:
            lines.append(f"Note: {self.notes}")
        return lines


def _parse_block(name: str, raw_block: Dict[str, Any]) -> LayoutBlock:
    max_items = raw_block.get("max_items")
    if isinstance(max_items, str) and max_items.isdigit():
        max_items = int(max_items)
    columns = raw_block.get("columns")
    if isinstance(columns, str) and columns.isdigit():
        columns = int(columns)
    return LayoutBlock(
        type=raw_block.get("type", "bullets"),
        x=float(raw_block.get("x", 0.8)),
        y=float(raw_block.get("y", 3.0)),
        width=float(raw_block.get("width", 10.0)),
        height=(float(raw_block["height"]) if "height" in raw_block else None),
        style=raw_block.get("style"),
        columns=columns,
        card_height=(float(raw_block["card_height"]) if "card_height" in raw_block else None),
        max_items=max_items,
    )


def parse_layout_data(data: Dict[str, Any]) -> LayoutPlan:
    templates_raw = data.get("templates", {})
    templates: Dict[str, LayoutTemplate] = {}
    alias_map: Dict[str, str] = {}

    for name, raw_template in templates_raw.items():
        blocks = [_parse_block(name, block) for block in raw_template.get("blocks", [])]
        decorations = raw_template.get("decorations", {})
        aliases = [alias.lower() for alias in raw_template.get("aliases", [])]
        template = LayoutTemplate(
            name=name,
            description=raw_template.get("description"),
            blocks=blocks,
            decorations=decorations,
            aliases=aliases,
        )
        templates[name] = template
        alias_map[name.lower()] = name
        for alias in aliases:
            alias_map[alias] = name

    if not templates:
        raise ValueError("Nessun template layout definito nel JSON.")

    plan_raw = data.get("slide_plan", {})
    default_candidate = plan_raw.get("default")
    if default_candidate:
        default_candidate = alias_map.get(default_candidate.lower(), default_candidate)
    default_template = default_candidate or (next(iter(templates)) if templates else "")
    overrides: Dict[int, str] = {}
    for idx, value in plan_raw.get("overrides", {}).items():
        resolved = alias_map.get(value.lower(), value)
        if resolved in templates:
            overrides[int(idx)] = resolved

    if default_template not in templates:
        default_template = next(iter(templates))

    return LayoutPlan(
        templates=templates,
        default_template=default_template,
        overrides=overrides,
        alias_map=alias_map,
        plan_title=plan_raw.get("plan_title"),
        notes=plan_raw.get("notes"),
    )


def load_layout_plan(path: Path) -> LayoutPlan:
    if not path.exists():
        raise FileNotFoundError(f"Layout plan non trovato: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    return parse_layout_data(data)


def load_layout_data_or_default(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return copy.deepcopy(DEFAULT_LAYOUT_DATA)
