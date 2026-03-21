"""Aggregazione token e stima costi (opzionale) per le chiamate Gemini SVG."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class GeminiSvgApiUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    thinking_tokens: int = 0
    api_calls: int = 0
    last_stop_reason: str | None = None
    retried: bool = False

    def add_from_client_response(self, response: Any) -> None:
        self.api_calls += 1
        u = getattr(response, "usage", None)
        if u is None:
            self.last_stop_reason = getattr(response, "stop_reason", None)
            return
        self.prompt_tokens += int(getattr(u, "prompt_tokens", 0) or 0)
        self.completion_tokens += int(getattr(u, "completion_tokens", 0) or 0)
        self.cached_tokens += int(getattr(u, "cached_tokens", 0) or 0)
        self.thinking_tokens += int(getattr(u, "thinking_tokens", 0) or 0)
        self.last_stop_reason = getattr(response, "stop_reason", None)


@dataclass
class GeminiSvgSlideRecord:
    slide_index: int
    title: str
    prompt_tokens: int
    completion_tokens: int
    cached_tokens: int
    thinking_tokens: int
    api_calls: int
    stop_reason: str | None
    retried: bool
    fallback: bool


@dataclass
class GeminiSvgRunSummary:
    model_name: str
    generated_at: str
    records: list[GeminiSvgSlideRecord] = field(default_factory=list)

    def total_usage(self) -> GeminiSvgApiUsage:
        u = GeminiSvgApiUsage()
        for r in self.records:
            u.prompt_tokens += r.prompt_tokens
            u.completion_tokens += r.completion_tokens
            u.cached_tokens += r.cached_tokens
            u.thinking_tokens += r.thinking_tokens
            u.api_calls += r.api_calls
            if r.retried:
                u.retried = True
            u.last_stop_reason = r.stop_reason
        return u

    def estimated_cost_usd(self) -> float | None:
        inp = os.getenv("GEMINI_INPUT_USD_PER_MTOKEN", "").strip()
        out = os.getenv("GEMINI_OUTPUT_USD_PER_MTOKEN", "").strip()
        if not inp or not out:
            return None
        try:
            pin = float(inp)
            pout = float(out)
        except ValueError:
            return None
        t = self.total_usage()
        return (t.prompt_tokens * pin + t.completion_tokens * pout) / 1_000_000

    def format_console_line(self) -> str:
        t = self.total_usage()
        parts = [
            f"Gemini SVG ({self.model_name}): {len(self.records)} slide",
            f"{t.api_calls} chiamate API",
            f"{t.prompt_tokens} token prompt",
            f"{t.completion_tokens} token output",
        ]
        if t.thinking_tokens:
            parts.append(f"{t.thinking_tokens} thinking")
        est = self.estimated_cost_usd()
        if est is not None:
            parts.append(f"~${est:.4f} USD (stima da .env)")
        else:
            parts.append(
                "stima $: imposta GEMINI_INPUT_USD_PER_MTOKEN e GEMINI_OUTPUT_USD_PER_MTOKEN (USD per milione di token)"
            )
        return " | ".join(parts)

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        t = self.total_usage()
        payload = {
            "model": self.model_name,
            "generated_at": self.generated_at,
            "totals": {
                "prompt_tokens": t.prompt_tokens,
                "completion_tokens": t.completion_tokens,
                "cached_tokens": t.cached_tokens,
                "thinking_tokens": t.thinking_tokens,
                "api_calls": t.api_calls,
            },
            "estimated_cost_usd": self.estimated_cost_usd(),
            "slides": [asdict(r) for r in self.records],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
