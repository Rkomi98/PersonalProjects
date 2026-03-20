"""High level orchestration that asks datapizza/OpenAI to author Datapizza slides."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from datapizza.clients.openai import OpenAIClient

from .slide_models import DatapizzaSlide, SlideDeck, SlideType


@dataclass
class SlideGeneratorConfig:
    api_key: str
    model_name: str
    system_prompt: str
    temperature: float
    style_prompt: str
    skill_context: str = ""


class SlideGenerationService:
    """Generate structured Datapizza slides leveraging datapizza's OpenAI client."""

    def __init__(self, config: SlideGeneratorConfig):
        self.config = config
        self.client = OpenAIClient(
            api_key=config.api_key,
            model=config.model_name,
            system_prompt=config.system_prompt,
            temperature=config.temperature,
        )
        self._schema = json.dumps(SlideDeck.model_json_schema(), ensure_ascii=False)

    @staticmethod
    def suggest_slide_count(markdown_text: str) -> int:
        """Estimate a sensible default slide count from the Markdown outline."""
        outline = SlideGenerationService._analyze_markdown(markdown_text)
        h2_count = len(outline["h2_sections"])
        h3_count = len(outline["h3_sections"])
        workflow_count = len(outline["workflow_sections"])
        long_sections = len(
            [section for section in outline["h2_sections"] if section["word_count"] >= 220]
        )
        suggested = 2 + h2_count + h3_count + workflow_count + min(3, long_sections)
        return max(10, min(28, suggested))

    @staticmethod
    def _analyze_markdown(markdown_text: str) -> dict:
        """Extract a lightweight outline to force topic coverage."""
        sections: list[dict] = []
        current: dict | None = None
        heading_re = re.compile(r"^(#{1,3})\s+(.*)$")

        for raw_line in markdown_text.splitlines():
            line = raw_line.rstrip()
            match = heading_re.match(line)
            if match:
                current = {
                    "level": len(match.group(1)),
                    "title": match.group(2).strip(),
                    "body_lines": [],
                }
                sections.append(current)
                continue
            if current is not None:
                current["body_lines"].append(line)

        for section in sections:
            body = "\n".join(section["body_lines"]).strip()
            section["body"] = body
            section["word_count"] = len(body.split())

        workflow_keywords = re.compile(
            r"\b(esercizi|esercizio|workflow|pipeline|come si costruisce|step|passo|misurare|valutare|costi|provider)\b",
            re.IGNORECASE,
        )
        h2_sections = [section for section in sections if section["level"] == 2]
        workflow_sections = [
            section
            for section in sections
            if section["level"] in {2, 3}
            if workflow_keywords.search(section["title"])
            or workflow_keywords.search(section["body"])
        ]

        return {
            "h1_titles": [section["title"] for section in sections if section["level"] == 1],
            "h2_sections": h2_sections,
            "h3_sections": [section for section in sections if section["level"] == 3],
            "workflow_sections": workflow_sections,
        }

    @staticmethod
    def _normalize_title(text: str) -> str:
        cleaned = re.sub(r"[^a-z0-9àèéìòù ]+", " ", text.lower())
        return " ".join(cleaned.split())

    @classmethod
    def _section_is_covered(cls, section_title: str, slides: list[DatapizzaSlide]) -> bool:
        section_norm = cls._normalize_title(section_title)
        section_tokens = {token for token in section_norm.split() if len(token) > 3}
        for slide in slides:
            title_norm = cls._normalize_title(slide.title)
            if section_norm in title_norm or title_norm in section_norm:
                return True
            title_tokens = {token for token in title_norm.split() if len(token) > 3}
            if len(section_tokens & title_tokens) >= 2:
                return True
        return False

    @staticmethod
    def _shorten_sentence(text: str, max_words: int) -> str:
        words = text.split()
        return " ".join(words[:max_words]).strip().rstrip(",;:")

    @classmethod
    def _extract_workflow_bullets(cls, body: str) -> list[str]:
        patterns = [
            r"Il primo passo[^.]*\.",
            r"Il secondo passo[^.]*\.",
            r"Il terzo passo[^.]*\.",
            r"Il quarto passo[^.]*\.",
        ]
        matches: list[str] = []
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                matches.append(match.group(0))
        if not matches:
            sentences = re.split(r"(?<=[.!?])\s+", body)
            matches = [sentence for sentence in sentences if sentence.strip()][:4]
        bullets: list[str] = []
        for sentence in matches[:4]:
            cleaned = re.sub(r"^(Il|La|Un|Una)\s+", "", sentence.strip(), flags=re.IGNORECASE)
            cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
            bullets.append(cls._shorten_sentence(cleaned, 10))
        return [bullet for bullet in bullets if bullet]

    @classmethod
    def _extract_body(cls, body: str) -> str:
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", body) if sentence.strip()]
        excerpt = " ".join(sentences[:2]) if sentences else body.strip()
        return cls._shorten_sentence(excerpt, 28)

    @staticmethod
    def _build_image_prompt(
        *,
        title: str,
        body: str | None,
        is_workflow: bool,
        is_architecture: bool,
    ) -> str:
        base = (
            "SVG 800x500px, viewBox 0 0 800 500. "
            "Stile Datapizza, flat, minimalista, vettoriale, senza ombre o gradienti. "
            "Palette: sfondo bianco #FFFFFF, blu #1B64F5, rosso #C64336, testo #111F2D e #0D1F2E, "
            "grigi #ECEFF2 e #737373, verde #398C4B per esiti positivi. "
        )
        if is_workflow:
            return (
                base
                + f"Schema 'Divide et Impera' per '{title}': lato sinistro con contesto iniziale e problema, "
                "centro con freccia di transizione blu, lato destro con timeline verticale numerata e step operativi. "
                "Usa card pulite, etichette uppercase e badge essenziali."
            )
        if is_architecture:
            return (
                base
                + f"Schema 'Datapizza Visual Architect' per '{title}': architettura a blocchi o pipeline, "
                "nodi rettangolari con angoli arrotondati, frecce sottili blu, gerarchia chiara, ampio whitespace, "
                f"metti in evidenza: {body or title}."
            )
        return (
            base
            + f"Visual concettuale sobrio per '{title}', con card o metafora astratta coerente con il contenuto: "
            f"{body or title}. Evita icone stock o clipart."
        )

    @classmethod
    def _build_fallback_slide(cls, section: dict) -> DatapizzaSlide:
        title = section["title"].strip()
        body = section.get("body", "")
        workflow_keywords = re.compile(
            r"\b(esercizi|esercizio|workflow|pipeline|step|passo|misurare|valutare|provider|costi)\b",
            re.IGNORECASE,
        )
        is_workflow = bool(workflow_keywords.search(title) or workflow_keywords.search(body))
        architecture_keywords = re.compile(
            r"\b(architettura|retrieval|bm25|semantic search|hybrid search|reranking|provider|sparse|dense|pipeline)\b",
            re.IGNORECASE,
        )
        is_architecture = bool(architecture_keywords.search(title) or architecture_keywords.search(body))

        if is_workflow:
            bullets = cls._extract_workflow_bullets(body)
            return DatapizzaSlide(
                slide_type=SlideType.BULLETS,
                title=title,
                bullets=bullets[:4],
                speaker_notes=f"Slide aggiunta per coprire la sezione '{title}' del documento.",
                image_prompt=cls._build_image_prompt(
                    title=title,
                    body=body,
                    is_workflow=True,
                    is_architecture=is_architecture,
                ),
            )

        short_body = cls._extract_body(body)
        return DatapizzaSlide(
            slide_type=SlideType.CONTENT,
            title=title,
            body=short_body,
            speaker_notes=f"Slide aggiunta per coprire la sezione '{title}' del documento.",
            image_prompt=cls._build_image_prompt(
                title=title,
                body=short_body,
                is_workflow=False,
                is_architecture=is_architecture,
            ),
        )

    @classmethod
    def _restyle_image_prompt(cls, slide: DatapizzaSlide) -> DatapizzaSlide:
        title = slide.title
        body = slide.body or " ".join(slide.bullets[:2])
        is_workflow = slide.slide_type == SlideType.BULLETS or bool(
            re.search(r"\b(esercizi|esercizio|workflow|pipeline|step|passo|misurare|valutare|provider|costi)\b", title, re.IGNORECASE)
        )
        is_architecture = bool(
            re.search(r"\b(architettura|retrieval|bm25|semantic|hybrid|reranking|dense|sparse|provider)\b", f"{title} {body}", re.IGNORECASE)
        )
        return DatapizzaSlide(
            **{
                **slide.model_dump(mode="python"),
                "image_prompt": cls._build_image_prompt(
                    title=title,
                    body=body,
                    is_workflow=is_workflow,
                    is_architecture=is_architecture,
                ),
            }
        )

    @classmethod
    def _repair_deck_against_outline(
        cls,
        markdown_text: str,
        slides: list[DatapizzaSlide],
    ) -> list[DatapizzaSlide]:
        outline = cls._analyze_markdown(markdown_text)
        if not slides:
            return slides

        intro = [cls._restyle_image_prompt(slide) for slide in slides[0:1]]
        content_slides = [slide for slide in slides[1:] if slide.slide_type != SlideType.CLOSING]
        closing = [slide for slide in slides if slide.slide_type == SlideType.CLOSING]

        for section in outline["h2_sections"] + outline["h3_sections"]:
            if not cls._section_is_covered(section["title"], content_slides):
                content_slides.append(cls._build_fallback_slide(section))

        restyled = [cls._restyle_image_prompt(slide) for slide in content_slides]
        closing_slide = closing[-1] if closing else DatapizzaSlide(
            slide_type=SlideType.CLOSING,
            title="Grazie",
            speaker_notes="Chiudi richiamando il messaggio chiave della presentazione.",
            image_prompt=cls._build_image_prompt(
                title="Grazie",
                body="Chiusura della presentazione",
                is_workflow=False,
                is_architecture=False,
            ),
        )
        return intro + restyled + [cls._restyle_image_prompt(closing_slide)]

    def _build_prompt(
        self,
        *,
        markdown_text: str,
        requested_slides: int | None,
        language: str,
    ) -> str:
        outline = self._analyze_markdown(markdown_text)
        coverage_sections = outline["h2_sections"] + outline["h3_sections"]
        h2_lines = "\n".join(
            f"- {section['title']} ({section['word_count']} parole circa)"
            for section in coverage_sections
        ) or "- Nessun H2 rilevato"
        workflow_lines = "\n".join(
            f"- {section['title']}" for section in outline["workflow_sections"]
        ) or "- Nessuna sezione operativa rilevata"
        slide_limit_rule = (
            f"- Genera circa {requested_slides} slide totali, senza comprimere sezioni importanti.\n"
            if requested_slides
            else ""
        )

        return (
            f"Trasforma un documento Markdown in una presentazione Datapizza in {language}.\n\n"
            "OBIETTIVO\n"
            "---------\n"
            "Devi riorganizzare il contenuto del Markdown in slide concise, pronte per essere "
            "usate da Claude per il JSON e da Gemini per i visual SVG delle slide interne.\n\n"
            "VINCOLI DI CONTENUTO\n"
            "--------------------\n"
            "- Non aggiungere contenuto che non sia ricavabile dal Markdown.\n"
            "- Mantieni la lingua originale del documento.\n"
            "- Tono professionale, diretto, da community tech.\n"
            "- Ogni slide deve avere un solo concetto principale.\n"
            "- Se un paragrafo contiene piu concetti, splittalo in piu slide.\n"
            "- H1 -> slide 'title' o 'section'.\n"
            "- H2/H3 -> slide 'content' o 'bullets'.\n"
            "- Non saltare argomenti chiave: tutti gli H2 e H3 devono comparire almeno una volta.\n"
            "- Per sezioni molto dense puoi usare fino a 2 slide sullo stesso heading.\n"
            "- Ultima slide sempre di tipo 'closing' con titolo 'Grazie' o equivalente.\n"
            f"{slide_limit_rule}"
            "\n"
            "COPERTURA OBBLIGATORIA DEL DOCUMENTO\n"
            "-----------------------------------\n"
            "Questi heading H2/H3 DEVONO essere coperti nel deck:\n"
            f"{h2_lines}\n\n"
            "Queste sezioni hanno natura operativa e vanno trattate come esercizi/workflow o spiegazioni step-by-step, non come semplice riassunto:\n"
            f"{workflow_lines}\n\n"
            "VINCOLI DI FORMATO\n"
            "------------------\n"
            "- Usa esattamente i tipi slide: title, section, content, bullets, closing.\n"
            "- 'subtitle' solo per title o section.\n"
            "- 'body' solo quando serve davvero; nelle content slide massimo 3 righe.\n"
            "- 'bullets' solo per slide bullets: massimo 4 punti, ciascuno massimo 10 parole.\n"
            "- NON usare prefissi tipo [icon:warning] o tag simili nei bullet.\n"
            "- 'speaker_notes' devono aggiungere contesto orale, senza ripetere banalmente la slide.\n"
            "- Ogni slide deve avere un 'image_prompt' diverso e specifico.\n"
            "\n"
            "REGOLE IMAGE PROMPT DATAPIZZA\n"
            "-----------------------------\n"
            "- Ogni prompt deve includere esattamente: 'SVG 800x500px, viewBox 0 0 800 500'.\n"
            "- Stile sempre flat, minimalista, vettoriale, senza ombre o gradienti.\n"
            "- Usa il visual language dei prompt Datapizza inviati dall'utente, non icone generiche.\n"
            "- Palette Datapizza: blu #1B64F5, rosso #C64336, testo #111F2D/#0D1F2E, grigio #ECEFF2/#737373, verde #398C4B, sfondo #FFFFFF.\n"
            "- Slide tecniche: preferisci architetture a blocchi, pipeline, confronti, stack o flow diagram.\n"
            "- Slide concettuali: preferisci metafore astratte sobrie, non clipart o icone stock.\n"
            "- Se la slide deriva da una sezione operativa/how-to/esercizio, usa esplicitamente lo stile 'Divide et Impera': contesto iniziale a sinistra, transizione al centro, timeline o step a destra.\n"
            "- Se la slide descrive architetture o confronti tecnici, usa lo stile 'Datapizza Visual Architect' con card, nodi e frecce pulite.\n"
            "- Massimo 120 parole.\n"
            "\n"
            "OUTPUT\n"
            "------\n"
            f"Rispetta esattamente questo schema JSON: {self._schema}\n"
            "Rispondi esclusivamente con JSON valido, senza markdown, senza commenti, senza testo extra.\n\n"
            "STILE DATAPIZZA\n"
            "---------------\n"
            f"{self.config.style_prompt}\n\n"
            "SKILL DATAPIZZA\n"
            "---------------\n"
            f"{self.config.skill_context}\n\n"
            "MARKDOWN DI PARTENZA\n"
            "--------------------\n"
            f"{markdown_text.strip()}\n"
        )

    def _normalize_slide(self, slide: DatapizzaSlide, is_last: bool) -> DatapizzaSlide:
        data = slide.model_dump()
        slide_type = SlideType(data["slide_type"])
        icon_prefix_re = re.compile(r"\[icon:[^\]]+\]\s*", re.IGNORECASE)

        if slide_type == SlideType.BULLETS:
            normalized_bullets: list[str] = []
            for bullet in data.get("bullets", [])[:4]:
                cleaned = icon_prefix_re.sub("", bullet).strip()
                words = cleaned.split()
                normalized_bullets.append(" ".join(words[:10]).strip())
            data["bullets"] = normalized_bullets
            data["body"] = None
        elif slide_type == SlideType.CONTENT:
            data["bullets"] = []
        elif slide_type in {SlideType.TITLE, SlideType.SECTION, SlideType.CLOSING}:
            data["bullets"] = []
            if slide_type != SlideType.CONTENT:
                data["body"] = data.get("body") or None

        if slide_type not in {SlideType.TITLE, SlideType.SECTION}:
            data["subtitle"] = None

        if is_last:
            data["slide_type"] = SlideType.CLOSING.value
            data["title"] = data.get("title") or "Grazie"
            data["subtitle"] = None
            data["bullets"] = []

        return DatapizzaSlide(**data)

    def generate(
        self,
        *,
        markdown_text: str,
        requested_slides: int | None = None,
        language: str = "Italiano",
    ) -> SlideDeck:
        """Call the LLM and parse the resulting slide deck."""

        prompt = self._build_prompt(
            markdown_text=markdown_text,
            requested_slides=requested_slides,
            language=language,
        )
        response = self.client.structured_response(input=prompt, output_cls=SlideDeck)
        if not response.structured_data:
            raise RuntimeError("Il modello non ha restituito dati strutturati.")

        raw_deck = response.structured_data[0]
        slides = [
            self._normalize_slide(slide, idx == len(raw_deck.slides) - 1)
            for idx, slide in enumerate(raw_deck.slides)
        ]

        if not slides:
            raise RuntimeError("Il modello ha restituito un deck vuoto.")

        if slides[-1].slide_type != SlideType.CLOSING:
            slides.append(
                DatapizzaSlide(
                    slide_type=SlideType.CLOSING,
                    title="Grazie",
                    speaker_notes="Chiudi richiamando il messaggio chiave della presentazione.",
                    image_prompt=(
                        "SVG 800x500px, viewBox 0 0 800 500. "
                        "Segno di chiusura minimalista per una presentazione tech, "
                        "wordmark astratto o gesto di saluto professionale, flat, vettoriale, "
                        "sfondo bianco #FFFFFF, forme nere #1A1A1A, grigie #E5E5E5 e pochi "
                        "accenti arancio #FF5C00, senza ombre o gradienti."
                    ),
                )
            )

        repaired_slides = self._repair_deck_against_outline(markdown_text, slides)
        return SlideDeck(slides=repaired_slides)
