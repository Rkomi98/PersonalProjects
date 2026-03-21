"""Generate SVG assets for slides using datapizza's Google client."""
from __future__ import annotations

from dataclasses import dataclass
import html
import logging
from pathlib import Path
import re

from .gemini_usage import GeminiSvgApiUsage, GeminiSvgRunSummary, GeminiSvgSlideRecord, utc_now_iso
from .slide_models import DatapizzaSlide

try:  # pragma: no cover
    from datapizza.clients.google import GoogleClient
except Exception:  # pragma: no cover
    GoogleClient = None


log = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeminiGeneratorConfig:
    api_key: str
    model_name: str
    temperature: float = 0.2
    # Prima era 2500: risposte con <style>/@import venivano troncate senza </svg>.
    max_output_tokens: int = 16384


class GeminiSVGService:
    """Create SVG files for internal slides via datapizza's GoogleClient."""

    def __init__(self, config: GeminiGeneratorConfig, *, asset_dir: Path):
        self.config = config
        self.asset_dir = asset_dir
        if GoogleClient is None:
            raise RuntimeError(
                "Il Google client di datapizza-ai non è installato. "
                "Installa `datapizza-ai-clients-google` nel venv."
            )
        self.client = GoogleClient(
            api_key=config.api_key,
            model=config.model_name,
            system_prompt=(
                "Sei il Datapizza Visual Architect. "
                "Restituisci solo SVG validi, puliti, flat e minimalisti. "
                "Niente <style>, niente @import, niente URL esterni nel markup."
            ),
            temperature=config.temperature,
        )

    def generate_for_slides(
        self,
        slides: list[DatapizzaSlide],
        *,
        overwrite: bool = False,
    ) -> tuple[list[Path], GeminiSvgRunSummary]:
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []
        summary = GeminiSvgRunSummary(model_name=self.config.model_name, generated_at=utc_now_iso())
        for index, slide in enumerate(slides, start=1):
            if not slide.is_internal:
                continue
            target = self.asset_dir / f"slide_{index:02d}.svg"
            if target.exists() and not overwrite:
                generated.append(target)
                continue
            raw_text: str | None = None
            had_request_error = False
            usage_acc = None
            try:
                svg, raw_text, usage_acc = self._generate_svg(slide)
            except Exception as exc:
                had_request_error = True
                log.warning(
                    "Gemini generation failed for slide %s (%s): %s",
                    index,
                    slide.title,
                    exc,
                )
                svg = None
            used_fallback = not svg
            if not svg:
                if raw_text:
                    debug_path = self.asset_dir / f"slide_{index:02d}.raw.txt"
                    debug_path.write_text(raw_text, encoding="utf-8")
                if had_request_error:
                    log.warning(
                        "Using local fallback for slide %s (%s) because Gemini request failed",
                        index,
                        slide.title,
                    )
                else:
                    log.warning(
                        "Gemini returned no valid SVG for slide %s (%s), using local fallback",
                        index,
                        slide.title,
                    )
                svg = self._build_fallback_svg(slide)
            target.write_text(svg, encoding="utf-8")
            generated.append(target)
            if usage_acc is not None:
                log.info(
                    "Gemini slide %s: prompt=%s output=%s stop=%s%s",
                    index,
                    usage_acc.prompt_tokens,
                    usage_acc.completion_tokens,
                    usage_acc.last_stop_reason,
                    " (retry)" if usage_acc.retried else "",
                )
                summary.records.append(
                    GeminiSvgSlideRecord(
                        slide_index=index,
                        title=slide.title,
                        prompt_tokens=usage_acc.prompt_tokens,
                        completion_tokens=usage_acc.completion_tokens,
                        cached_tokens=usage_acc.cached_tokens,
                        thinking_tokens=usage_acc.thinking_tokens,
                        api_calls=usage_acc.api_calls,
                        stop_reason=usage_acc.last_stop_reason,
                        retried=usage_acc.retried,
                        fallback=used_fallback,
                    )
                )
        return generated, summary

    @staticmethod
    def _svg_instruction_block() -> str:
        return (
            "Restituisci SOLO markup SVG valido.\n"
            "Inizia con <svg e termina con </svg>.\n"
            "Nessun markdown (niente ```), nessun commento, nessun testo prima o dopo l'SVG.\n"
            "Non usare foreignObject.\n"
            "Usa text e tspan per tutto il testo.\n"
            "Mantieni il canvas 800x500.\n"
            "Usa font-family='Poppins, sans-serif' per il testo.\n"
            "Non usare tag <style>, non usare @import, non caricare font da URL.\n"
            "Mantieni l'SVG compatto: niente griglie <pattern>, niente texture ripetute; "
            "al massimo un <marker> freccia riusato su più linee.\n"
        )

    @staticmethod
    def _minimal_retry_block() -> str:
        return (
            "La risposta precedente era incompleta o troppo lunga. "
            "Ripeti lo STESSO concetto come SVG MINIMO sotto ~3500 caratteri: "
            "solo rect/line/circle/text essenziali, un solo marker freccia se serve, "
            "chiudi OBBLIGATORIAMENTE con </svg>."
        )

    def _generate_svg(self, slide: DatapizzaSlide) -> tuple[str | None, str | None, GeminiSvgApiUsage]:
        usage = GeminiSvgApiUsage()
        base = f"{self._sanitize_prompt(slide.image_prompt)}\n\n{self._svg_instruction_block()}"
        response = self.client.invoke(
            input=base,
            max_tokens=self.config.max_output_tokens,
        )
        usage.add_from_client_response(response)
        raw = response.text
        svg = self._extract_svg(raw)
        if svg is None and self._should_retry_svg(raw, response.stop_reason):
            usage.retried = True
            log.info("Gemini SVG slide retry (output troncato o stop su token)")
            response2 = self.client.invoke(
                input=f"{base}\n\n{self._minimal_retry_block()}",
                max_tokens=self.config.max_output_tokens,
            )
            usage.add_from_client_response(response2)
            raw = response2.text
            svg = self._extract_svg(raw)
        return svg, raw, usage

    @staticmethod
    def _sanitize_prompt(prompt: str, max_words: int = 140) -> str:
        cleaned = re.sub(r"\s+", " ", prompt.strip())
        words = cleaned.split()
        if len(words) <= max_words:
            return cleaned
        return " ".join(words[:max_words]).strip()

    @staticmethod
    def _strip_markdown_and_xml_decl(text: str) -> str:
        t = text.strip()
        m = re.match(
            r"^\s*```(?:xml|svg|html)?\s*\r?\n([\s\S]*?)\r?\n```\s*$",
            t,
            re.IGNORECASE,
        )
        if m:
            t = m.group(1).strip()
        elif "```" in t:
            t = "\n".join(
                line for line in t.splitlines() if not re.match(r"^\s*```", line)
            ).strip()
        t = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", t, flags=re.IGNORECASE)
        return t.strip()

    @staticmethod
    def _should_retry_svg(raw: str | None, stop_reason: str | None) -> bool:
        if not raw:
            return False
        sr = (stop_reason or "").lower()
        if "max" in sr and "token" in sr:
            return True
        lo = raw.lower()
        return "<svg" in lo and "</svg>" not in lo

    @staticmethod
    def _repair_truncated_svg(cleaned: str) -> str | None:
        """Se il modello taglia a metà tag, elimina l'apertura incompleta e chiude </svg>."""
        if "</svg>" in cleaned.lower():
            return None
        lo = cleaned.lower()
        if "<svg" not in lo:
            return None
        t = cleaned.rstrip()
        last_lt = t.rfind("<")
        last_gt = t.rfind(">")
        if last_lt > last_gt:
            t = t[:last_lt].rstrip()
        if "</svg>" not in t.lower():
            t = t + "\n</svg>"
        return t

    @classmethod
    def _extract_svg(cls, text: str | None) -> str | None:
        if not text:
            return None
        cleaned = cls._strip_markdown_and_xml_decl(text)
        match = re.search(r"(<svg[\s\S]*?</svg>)", cleaned, re.IGNORECASE)
        if match:
            svg = match.group(1).strip()
            if "<foreignObject" in svg:
                return None
            return svg
        repaired = cls._repair_truncated_svg(cleaned)
        if not repaired:
            return None
        match2 = re.search(r"(<svg[\s\S]*?</svg>)", repaired, re.IGNORECASE)
        if not match2:
            return None
        svg = match2.group(1).strip()
        if "<foreignObject" in svg:
            return None
        log.info("SVG Gemini riparato (risposta troncata: rimosso tag incompleto e aggiunto </svg>)")
        return svg

    @staticmethod
    def _plain(text: str | None) -> str:
        if not text:
            return ""
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    @staticmethod
    def _wrap_text(text: str, width: int = 26, max_lines: int = 4) -> list[str]:
        words = GeminiSVGService._plain(text).split()
        if not words:
            return []
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if len(candidate) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
                if len(lines) >= max_lines - 1:
                    break
        if len(lines) < max_lines:
            lines.append(current)
        return lines[:max_lines]

    @classmethod
    def _svg_text(cls, x: int, y: int, lines: list[str], *, size: int = 16, color: str = "#0D1F2E", weight: int = 400) -> str:
        escaped = [html.escape(line) for line in lines if line]
        if not escaped:
            return ""
        tspans = []
        for idx, line in enumerate(escaped):
            dy = "0" if idx == 0 else "22"
            tspans.append(f'<tspan x="{x}" dy="{dy}">{line}</tspan>')
        return (
            f'<text x="{x}" y="{y}" fill="{color}" font-family="Poppins, sans-serif" '
            f'font-size="{size}" font-weight="{weight}">' + "".join(tspans) + "</text>"
        )

    @classmethod
    def _svg_start(cls) -> list[str]:
        return [
            '<svg width="800" height="500" viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">',
            '<!-- source: local-fallback -->',
            '<rect width="800" height="500" fill="#FFFFFF"/>',
        ]

    @classmethod
    def _svg_title(cls, parts: list[str], title: str, *, subtitle: str | None = None) -> None:
        parts.extend(
            [
                '<rect x="28" y="24" width="744" height="82" rx="20" fill="#F4F7FB"/>',
                '<rect x="28" y="24" width="10" height="82" rx="5" fill="#C64336"/>',
                cls._svg_text(58, 58, cls._wrap_text(title, width=46, max_lines=2), size=24, color="#1B64F5", weight=700),
            ]
        )
        if subtitle:
            parts.append(
                cls._svg_text(60, 88, cls._wrap_text(subtitle, width=68, max_lines=2), size=11, color="#737373", weight=400)
            )

    @classmethod
    def _causal_labels(cls, slide: DatapizzaSlide) -> tuple[str, list[str], str]:
        text = " ".join(
            [
                cls._plain(slide.title).lower(),
                cls._plain(slide.body).lower(),
                cls._plain(slide.speaker_notes).lower(),
                " ".join(cls._plain(bullet).lower() for bullet in slide.bullets[:4]),
            ]
        )
        if "ricette" in text or "ingredienti" in text:
            return "solo titolo", ["titolo", "ingredienti", "varianti"], "match migliore"
        if "hybrid" in text or "retrieval" in text:
            return "solo keyword", ["keyword", "dense", "sparse"], "fusione robusta"
        if "provider" in text:
            return "solo ranking", ["ranking", "dense", "metadata"], "risposta stabile"
        return "solo segnale", ["keyword", "intent", "metadata"], "output corretto"

    @classmethod
    def _build_comparison_svg(cls, slide: DatapizzaSlide) -> str:
        bullets = slide.bullets[:4] or cls._wrap_text(slide.body or slide.speaker_notes, width=16, max_lines=4)
        colors = ["#1B64F5", "#398C4B", "#C86E3E", "#7C3AED"]
        parts = cls._svg_start()
        cls._svg_title(parts, slide.title)
        card_w = 168 if len(bullets) == 4 else 220
        gap = 16
        total_w = len(bullets) * card_w + max(0, len(bullets) - 1) * gap
        start_x = (800 - total_w) // 2
        for idx, bullet in enumerate(bullets):
            x = start_x + idx * (card_w + gap)
            y = 150
            color = colors[idx % len(colors)]
            parts.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{card_w}" height="230" rx="22" fill="#FFFFFF" stroke="#D0D5DD" stroke-width="2"/>',
                    f'<rect x="{x}" y="{y}" width="{card_w}" height="12" rx="6" fill="{color}"/>',
                    f'<circle cx="{x + card_w/2:.0f}" cy="{y + 56}" r="22" fill="{color}" opacity="0.12"/>',
                    f'<circle cx="{x + card_w/2:.0f}" cy="{y + 56}" r="10" fill="{color}"/>',
                    cls._svg_text(x + 18, y + 108, cls._wrap_text(str(bullet), width=16, max_lines=3), size=16, color="#111F2D", weight=700),
                ]
            )
            if slide.speaker_notes:
                note = cls._wrap_text(slide.speaker_notes, width=18, max_lines=4)
                parts.append(cls._svg_text(x + 18, y + 164, note, size=11, color="#737373", weight=400))
        parts.append("</svg>")
        return "".join(parts)

    @classmethod
    def _build_workflow_svg(cls, slide: DatapizzaSlide) -> str:
        bullets = slide.bullets[:4]
        colors = ["#1B64F5", "#C86E3E", "#E8A317", "#398C4B"]
        parts = cls._svg_start()
        cls._svg_title(parts, slide.title)
        parts.extend(
            [
                '<rect x="44" y="136" width="210" height="310" rx="26" fill="#F4F7FB"/>',
                '<rect x="62" y="156" width="86" height="26" rx="13" fill="#C64336" opacity="0.12"/>',
                cls._svg_text(74, 174, ["CONTESTO"], size=12, color="#C64336", weight=700),
                cls._svg_text(62, 214, cls._wrap_text(slide.speaker_notes or slide.body or slide.title, width=24, max_lines=8), size=15, color="#111F2D", weight=500),
                '<line x1="308" y1="156" x2="308" y2="412" stroke="#D0D5DD" stroke-width="4" stroke-dasharray="8 8"/>',
            ]
        )
        for idx, bullet in enumerate(bullets):
            y = 160 + idx * 68
            color = colors[idx % len(colors)]
            parts.extend(
                [
                    f'<circle cx="308" cy="{y}" r="22" fill="{color}"/>',
                    f'<text x="308" y="{y + 7}" text-anchor="middle" fill="#FFFFFF" font-family="Poppins, sans-serif" font-size="16" font-weight="700">{idx + 1}</text>',
                    f'<rect x="344" y="{y - 28}" width="386" height="58" rx="18" fill="#FFFFFF" stroke="{color}" stroke-width="2"/>',
                    f'<rect x="344" y="{y - 28}" width="8" height="58" rx="4" fill="{color}"/>',
                    cls._svg_text(368, y - 3, cls._wrap_text(bullet, width=30, max_lines=2), size=15, color="#111F2D", weight=600),
                ]
            )
        parts.append("</svg>")
        return "".join(parts)

    @classmethod
    def _build_causal_svg(cls, slide: DatapizzaSlide) -> str:
        parts = cls._svg_start()
        cls._svg_title(parts, slide.title)
        left_signal, right_items, output_label = cls._causal_labels(slide)
        summary = cls._wrap_text(slide.body or slide.speaker_notes or slide.title, width=70, max_lines=2)
        parts.extend(
            [
                '<rect x="54" y="146" width="178" height="230" rx="26" fill="#FFFFFF" stroke="#D7342B" stroke-width="2"/>',
                '<rect x="54" y="146" width="178" height="12" rx="6" fill="#D7342B"/>',
                '<circle cx="143" cy="218" r="48" fill="#D7342B" opacity="0.12"/>',
                '<circle cx="143" cy="218" r="24" fill="#D7342B"/>',
                cls._svg_text(88, 292, ["1 SEGNALE"], size=13, color="#C64336", weight=700),
                cls._svg_text(86, 326, cls._wrap_text(left_signal, width=14, max_lines=2), size=18, color="#111F2D", weight=700),
                '<path d="M232 220 C292 220, 312 220, 364 220" stroke="#1B64F5" stroke-width="6" fill="none"/>',
                '<path d="M232 260 C292 260, 312 260, 364 260" stroke="#1B64F5" stroke-width="6" fill="none"/>',
                '<path d="M232 300 C292 300, 312 300, 364 300" stroke="#1B64F5" stroke-width="6" fill="none"/>',
                '<polygon points="364,176 430,260 364,344" fill="#E8A317"/>',
                cls._svg_text(456, 190, ["COLLASSO"], size=14, color="#C64336", weight=700),
                cls._svg_text(454, 224, ["ambiguita", "sinonimi", "rumore"], size=13, color="#737373", weight=500),
                '<rect x="538" y="148" width="120" height="62" rx="20" fill="#FFFFFF" stroke="#1B64F5" stroke-width="2"/>',
                '<rect x="574" y="228" width="120" height="62" rx="20" fill="#FFFFFF" stroke="#7C3AED" stroke-width="2"/>',
                '<rect x="538" y="308" width="120" height="62" rx="20" fill="#FFFFFF" stroke="#C86E3E" stroke-width="2"/>',
                cls._svg_text(570, 185, cls._wrap_text(right_items[0], width=10, max_lines=2), size=14, color="#1B64F5", weight=700),
                cls._svg_text(606, 265, cls._wrap_text(right_items[1], width=10, max_lines=2), size=14, color="#7C3AED", weight=700),
                cls._svg_text(570, 345, cls._wrap_text(right_items[2], width=10, max_lines=2), size=14, color="#C86E3E", weight=700),
                '<path d="M430 260 L522 180" stroke="#398C4B" stroke-width="5" fill="none"/>',
                '<path d="M430 260 L558 258" stroke="#398C4B" stroke-width="5" fill="none"/>',
                '<path d="M430 260 L522 340" stroke="#398C4B" stroke-width="5" fill="none"/>',
                '<rect x="654" y="406" width="112" height="44" rx="16" fill="#398C4B"/>',
                cls._svg_text(676, 433, cls._wrap_text(output_label, width=12, max_lines=2), size=13, color="#FFFFFF", weight=700),
                cls._svg_text(60, 430, summary, size=13, color="#737373", weight=400),
            ]
        )
        parts.append("</svg>")
        return "".join(parts)

    @classmethod
    def _build_architecture_svg(cls, slide: DatapizzaSlide) -> str:
        parts = cls._svg_start()
        cls._svg_title(parts, slide.title)
        labels = slide.bullets[:3]
        if not labels:
            labels = ["Input", "Fusion", "Output"]
        labels = labels[:3]
        colors = ["#1B64F5", "#7C3AED", "#398C4B"]
        xs = [70, 300, 530]
        parts.extend(
            [
                '<path d="M220 252 L300 252" stroke="#1B64F5" stroke-width="5" fill="none"/>',
                '<polygon points="292,244 312,252 292,260" fill="#1B64F5"/>',
                '<path d="M450 252 L530 252" stroke="#1B64F5" stroke-width="5" fill="none"/>',
                '<polygon points="522,244 542,252 522,260" fill="#1B64F5"/>',
            ]
        )
        for idx, (x, label, color) in enumerate(zip(xs, labels, colors)):
            parts.extend(
                [
                    f'<rect x="{x}" y="172" width="160" height="160" rx="26" fill="#FFFFFF" stroke="#D0D5DD" stroke-width="2"/>',
                    f'<rect x="{x}" y="172" width="160" height="14" rx="7" fill="{color}"/>',
                    f'<circle cx="{x + 80}" cy="228" r="24" fill="{color}" opacity="0.16"/>',
                    f'<circle cx="{x + 80}" cy="228" r="10" fill="{color}"/>',
                    cls._svg_text(x + 24, 278, cls._wrap_text(label, width=14, max_lines=3), size=18, color="#111F2D", weight=700),
                ]
            )
        note = cls._wrap_text(slide.body or slide.speaker_notes, width=68, max_lines=2)
        parts.append(cls._svg_text(74, 404, note, size=14, color="#737373", weight=400))
        parts.append("</svg>")
        return "".join(parts)

    @classmethod
    def _build_concept_svg(cls, slide: DatapizzaSlide) -> str:
        parts = cls._svg_start()
        cls._svg_title(parts, slide.title)
        body_lines = cls._wrap_text(slide.body or slide.speaker_notes, width=34, max_lines=4)
        parts.extend(
            [
                '<rect x="56" y="148" width="290" height="250" rx="28" fill="#F4F7FB"/>',
                cls._svg_text(84, 198, body_lines, size=18, color="#111F2D", weight=500),
                '<rect x="406" y="148" width="338" height="250" rx="28" fill="#FFFFFF" stroke="#D0D5DD" stroke-width="2"/>',
                '<circle cx="510" cy="220" r="38" fill="#1B64F5" opacity="0.18"/>',
                '<circle cx="638" cy="220" r="38" fill="#C86E3E" opacity="0.18"/>',
                '<circle cx="574" cy="320" r="38" fill="#398C4B" opacity="0.18"/>',
                '<circle cx="510" cy="220" r="16" fill="#1B64F5"/>',
                '<circle cx="638" cy="220" r="16" fill="#C86E3E"/>',
                '<circle cx="574" cy="320" r="16" fill="#398C4B"/>',
                '<line x1="526" y1="228" x2="558" y2="304" stroke="#1B64F5" stroke-width="5"/>',
                '<line x1="622" y1="228" x2="590" y2="304" stroke="#C86E3E" stroke-width="5"/>',
                '<line x1="526" y1="220" x2="622" y2="220" stroke="#7C3AED" stroke-width="5"/>',
            ]
        )
        parts.append("</svg>")
        return "".join(parts)

    @classmethod
    def _build_fallback_svg(cls, slide: DatapizzaSlide) -> str:
        title = cls._plain(slide.title).lower()
        text = " ".join([title, cls._plain(slide.body), cls._plain(slide.speaker_notes), " ".join(map(cls._plain, slide.bullets[:4]))])
        if any(keyword in text for keyword in ["provider", "famiglie", "confronto", "elasticsearch", "opensearch", "pinecone", "qdrant", "weaviate", "azure"]):
            return cls._build_comparison_svg(slide)
        if any(keyword in text for keyword in ["dipende da un solo segnale", "failure", "single signal", "principio di progettazione", "non fidarti"]):
            return cls._build_causal_svg(slide)
        if slide.bullets:
            return cls._build_workflow_svg(slide)
        if any(keyword in text for keyword in ["architettura", "pipeline", "retrieval", "hybrid", "bm25", "semantic", "reranking", "dense", "sparse"]):
            return cls._build_architecture_svg(slide)
        return cls._build_concept_svg(slide)
