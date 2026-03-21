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
    def _parse_markdown_tree(markdown_text: str) -> dict:
        """Parse the markdown into a deterministic H1/H2/H3 tree."""
        doc = {"title": None, "intro_lines": [], "sections": []}
        current_h2: dict | None = None
        current_h3: dict | None = None
        heading_re = re.compile(r"^(#{1,3})\s+(.*)$")

        for raw_line in markdown_text.splitlines():
            line = raw_line.rstrip()
            match = heading_re.match(line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                if level == 1:
                    doc["title"] = title
                    current_h2 = None
                    current_h3 = None
                elif level == 2:
                    current_h2 = {"title": title, "body_lines": [], "subsections": []}
                    doc["sections"].append(current_h2)
                    current_h3 = None
                elif level == 3 and current_h2 is not None:
                    current_h3 = {"title": title, "body_lines": []}
                    current_h2["subsections"].append(current_h3)
                continue

            if current_h3 is not None:
                current_h3["body_lines"].append(line)
            elif current_h2 is not None:
                current_h2["body_lines"].append(line)
            else:
                doc["intro_lines"].append(line)

        doc["intro"] = "\n".join(doc["intro_lines"]).strip()
        for section in doc["sections"]:
            section["body"] = "\n".join(section["body_lines"]).strip()
            for subsection in section["subsections"]:
                subsection["body"] = "\n".join(subsection["body_lines"]).strip()
        return doc

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
    def _split_title_subtitle(title: str) -> tuple[str, str | None]:
        if ":" in title:
            left, right = title.split(":", 1)
            return left.strip(), right.strip()
        return title.strip(), None

    @staticmethod
    def _extract_bold_terms(body: str) -> list[str]:
        return [term.strip() for term in re.findall(r"\*\*([^*]+)\*\*", body)]

    @classmethod
    def _extract_named_bullets(cls, title: str, body: str) -> list[str]:
        lower_title = title.lower()
        bold_terms = cls._extract_bold_terms(body)
        if bold_terms:
            return [cls._shorten_sentence(term, 10) for term in bold_terms[:4]]

        if "famiglie concettuali" in lower_title:
            matches = re.findall(r"La (prima|seconda|terza) famiglia è\s+\*\*([^*]+)\*\*", body, re.IGNORECASE)
            if matches:
                return [cls._shorten_sentence(match[1], 10) for match in matches[:4]]

        if "failure" in lower_title or "metriche" in lower_title or "passaggi" in lower_title:
            return cls._extract_workflow_bullets(body)[:4]

        if "provider" in lower_title:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
            return [cls._shorten_sentence(s, 10) for s in sentences[:4]]

        return []

    @staticmethod
    def _visual_focus(body: str | None, bullets: list[str] | None) -> str:
        bullet_text = ", ".join((bullets or [])[:4]).strip()
        if bullet_text:
            return bullet_text
        if body:
            return SlideGenerationService._shorten_sentence(body, 18)
        return ""

    @staticmethod
    def _choose_skill_layout(
        *,
        slide_type: SlideType,
        title: str,
        body: str | None,
        bullets: list[str] | None,
        is_workflow: bool,
        is_architecture: bool,
    ) -> str:
        text = " ".join(filter(None, [title, body or "", " ".join(bullets or [])])).lower()
        bullet_count = len(bullets or [])
        if slide_type == SlideType.TITLE:
            return "Cover"
        if slide_type == SlideType.SECTION:
            return "Section Divider"
        if any(token in text for token in ["costo", "metriche", "misurare", "valutare", "benchmark"]):
            return "Statistiche"
        if any(token in text for token in ["stack", "layer", "livelli"]):
            return "Diagramma Stack"
        if is_workflow:
            return "Diagramma Flow V"
        if "provider" in text or "famiglie" in text or "confronto" in text:
            if bullet_count >= 4:
                return "Quattro Box"
            if bullet_count == 3:
                return "Tre Colonne"
            return "Due Colonne"
        if is_architecture:
            return "Diagramma Flow H"
        return "Diagramma Custom"

    @staticmethod
    def _is_workflow_visual(title: str, body: str | None, bullets: list[str] | None) -> bool:
        text = " ".join(filter(None, [title, body or "", " ".join(bullets or [])]))
        return bool(
            re.search(
                r"\b(esercizi|esercizio|workflow|step|passo|passaggi|come si costruisce|come funziona|pipeline|misurare|valutare)\b",
                text,
                re.IGNORECASE,
            )
        )

    @staticmethod
    def _is_architecture_visual(title: str, body: str | None, bullets: list[str] | None) -> bool:
        text = " ".join(filter(None, [title, body or "", " ".join(bullets or [])]))
        return bool(
            re.search(
                r"\b(architettura|retrieval|search|bm25|semantic|hybrid|reranking|dense|sparse|provider|indice|embedding|query|ranking|vettoriale)\b",
                text,
                re.IGNORECASE,
            )
        )

    @staticmethod
    def _build_visual_layout(
        *,
        slide_type: SlideType,
        title: str,
        focus: str,
        bullets: list[str] | None,
        is_workflow: bool,
        is_architecture: bool,
    ) -> str:
        title_l = title.lower()
        focus_text = focus or title
        skill_layout = SlideGenerationService._choose_skill_layout(
            slide_type=slide_type,
            title=title,
            body=focus,
            bullets=bullets,
            is_workflow=is_workflow,
            is_architecture=is_architecture,
        )
        full_slide_clause = (
            "Composizione full-slide 16:9, edge-to-edge, leggibile anche da lontano. "
            if slide_type == SlideType.CONTENT
            else "Composizione ampia e ariosa, con forte dominanza del visual. "
        )
        if is_workflow:
            if "come funziona" in title_l:
                return (
                    f"Ispirati direttamente al layout skill '{skill_layout}'. {full_slide_clause}"
                    f"Rappresenta '{title}' come sequenza operativa: colonna sinistra con input e contesto, "
                    "centro con motore o trasformazione, colonna destra con 3-4 step numerati e output. "
                    f"Visualizza questi elementi: {focus_text}. "
                    "Usa blu per struttura, arancio e giallo per attenzione o scoring, verde per outcome corretto."
                )
            if "costo" in title_l or "misurare" in title_l or "valutare" in title_l:
                return (
                    f"Ispirati direttamente al layout skill '{skill_layout}'. {full_slide_clause}"
                    f"Rappresenta '{title}' come framework decisionale: blocco iniziale, asse o checklist centrale, "
                    "colonna finale con outcome o trade-off. "
                    f"Metti in evidenza: {focus_text}. "
                    "Usa blu, giallo, arancio e rosso come segnali decisionali distinti."
                )
            return (
                f"Ispirati direttamente al layout skill '{skill_layout}' e allo schema 'Divide et Impera'. "
                f"{full_slide_clause}"
                f"Per '{title}': lato sinistro con contesto iniziale, "
                "centro con freccia di transizione blu, lato destro con timeline verticale numerata e 3-4 step. "
                f"Incorpora in modo esplicito: {focus_text}. "
                "Usa rosso per blocchi critici, verde per esito positivo e arancio per passaggi di attenzione."
            )
        if "provider" in title_l:
            return (
                f"Ispirati direttamente al layout skill '{skill_layout}'. {full_slide_clause}"
                f"Confronto provider per '{title}': 3-4 card verticali allineate, ciascuna con label, "
                "capacità chiave e differenza architetturale; frecce leggere solo se servono. "
                f"Usa come contenuti guida: {focus_text}. "
                "Usa una palette semantica ricca: blu, verde, arancio e viola per categorie distinte."
            )
        if "famiglie" in title_l or "confronto" in title_l:
            return (
                f"Ispirati direttamente al layout skill '{skill_layout}'. {full_slide_clause}"
                f"Matrice comparativa per '{title}': colonne o card parallele con intestazioni nette, "
                "una riga finale di sintesi evidenziata in blu. "
                f"Confronta visivamente: {focus_text}. "
                "Usa blu, verde, arancio e viola per differenziare famiglie senza perdere chiarezza."
            )
        if "dipende da un solo segnale" in title_l or "perché" in title_l:
            return (
                f"Ispirati direttamente al layout skill '{skill_layout}'. {full_slide_clause}"
                f"Visual causale per '{title}': a sinistra un singolo segnale isolato, al centro un collo di bottiglia o punto di fallimento, "
                "a destra più segnali o un outcome corretto. "
                f"Richiama questi concetti: {focus_text}. "
                "Usa rosso per il failure point, blu per il segnale iniziale e verde per la correzione finale."
            )
        if is_architecture:
            return (
                f"Ispirati direttamente al layout skill '{skill_layout}' e allo schema 'Datapizza Visual Architect'. "
                f"{full_slide_clause}"
                f"Per '{title}': architettura a blocchi o pipeline, "
                "nodi rettangolari con angoli arrotondati, frecce sottili blu, gerarchia chiara e ampio whitespace. "
                f"Metti in evidenza: {focus_text}. "
                "Usa blu per struttura, viola per componenti avanzati, giallo per metriche e verde per output desiderato."
            )
        return (
            f"Ispirati direttamente al layout skill '{skill_layout}'. {full_slide_clause}"
            f"Visual concettuale per '{title}': 2-4 card o forme astratte con una sola relazione visiva chiara. "
            f"Rendi leggibile questo contenuto: {focus_text}. "
            "Usa almeno tre colori semantici Datapizza tra blu, rosso, verde, arancio, giallo e viola. "
            "Evita icone stock o clipart."
        )

    @staticmethod
    def _build_image_prompt(
        *,
        slide_type: SlideType,
        title: str,
        body: str | None,
        bullets: list[str] | None = None,
        is_workflow: bool,
        is_architecture: bool,
    ) -> str:
        focus = SlideGenerationService._visual_focus(body, bullets)
        base = (
            "SVG 800x500px, viewBox 0 0 800 500. "
            "Stile Datapizza, flat, minimalista, vettoriale, senza ombre o gradienti. "
            "Palette Datapizza completa: sfondo bianco #FFFFFF, blu #1B64F5, rosso brand #C64336, rosso critico #D7342B, "
            "verde #398C4B, arancio #C86E3E, giallo #E8A317, viola #7C3AED, testo #111F2D e #0D1F2E, grigi #ECEFF2 e #737373. "
            "Usa il colore in modo semantico, non decorativo, ma rendi il visual ricco, chiaro e memorabile. "
            "Usa solo forme geometriche pulite, testo minimo dentro il visual, niente mockup, niente persone, niente 3D. "
        )
        layout = SlideGenerationService._build_visual_layout(
            slide_type=slide_type,
            title=title,
            focus=focus,
            bullets=bullets,
            is_workflow=is_workflow,
            is_architecture=is_architecture,
        )
        return base + layout

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
                    slide_type=SlideType.BULLETS,
                    title=title,
                    body=body,
                    bullets=bullets[:4],
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
                slide_type=SlideType.CONTENT,
                title=title,
                body=short_body,
                bullets=None,
                is_workflow=False,
                is_architecture=is_architecture,
            ),
        )

    @classmethod
    def _slide_from_block(cls, title: str, body: str) -> DatapizzaSlide | None:
        if not body.strip():
            return None

        workflow_keywords = re.compile(
            r"\b(esercizi|esercizio|workflow|pipeline|step|passo|misurare|valutare|provider|costi|failure|metriche)\b",
            re.IGNORECASE,
        )
        is_workflow = bool(workflow_keywords.search(title) or workflow_keywords.search(body))
        architecture_keywords = re.compile(
            r"\b(architettura|retrieval|bm25|semantic search|hybrid search|reranking|provider|sparse|dense|pipeline)\b",
            re.IGNORECASE,
        )
        is_architecture = bool(architecture_keywords.search(title) or architecture_keywords.search(body))
        bullets = cls._extract_named_bullets(title, body)

        if bullets:
            return DatapizzaSlide(
                slide_type=SlideType.BULLETS,
                title=title,
                bullets=bullets[:4],
                speaker_notes=cls._extract_body(body),
                image_prompt=cls._build_image_prompt(
                    slide_type=SlideType.BULLETS,
                    title=title,
                    body=body,
                    bullets=bullets[:4],
                    is_workflow=is_workflow,
                    is_architecture=is_architecture,
                ),
            )

        return DatapizzaSlide(
            slide_type=SlideType.CONTENT,
            title=title,
            body=cls._extract_body(body),
            speaker_notes=cls._extract_body(body),
            image_prompt=cls._build_image_prompt(
                slide_type=SlideType.CONTENT,
                title=title,
                body=body,
                bullets=None,
                is_workflow=is_workflow,
                is_architecture=is_architecture,
            ),
        )

    @classmethod
    def _build_deterministic_deck(cls, markdown_text: str) -> SlideDeck:
        tree = cls._parse_markdown_tree(markdown_text)
        raw_title = tree["title"] or "Presentazione Datapizza"
        title, subtitle = cls._split_title_subtitle(raw_title)
        slides: list[DatapizzaSlide] = [
            DatapizzaSlide(
                slide_type=SlideType.TITLE,
                title=title,
                subtitle=subtitle,
                speaker_notes=cls._extract_body(tree["intro"] or raw_title),
                image_prompt=cls._build_image_prompt(
                    slide_type=SlideType.TITLE,
                    title=title,
                    body=subtitle or tree["intro"],
                    bullets=None,
                    is_workflow=False,
                    is_architecture=True,
                ),
            )
        ]

        for section in tree["sections"]:
            slides.append(
                DatapizzaSlide(
                    slide_type=SlideType.SECTION,
                    title=section["title"],
                    subtitle=None,
                    speaker_notes=cls._extract_body(section["body"] or section["title"]),
                    image_prompt=cls._build_image_prompt(
                        slide_type=SlideType.SECTION,
                        title=section["title"],
                        body=section["body"],
                        bullets=None,
                        is_workflow=bool(
                            re.search(r"\b(workflow|pipeline|costi|misurare|provider)\b", section["title"], re.IGNORECASE)
                        ),
                        is_architecture=True,
                    ),
                )
            )

            section_slide = cls._slide_from_block(section["title"], section["body"])
            if section_slide:
                slides.append(section_slide)

            for subsection in section["subsections"]:
                subsection_slide = cls._slide_from_block(subsection["title"], subsection["body"])
                if subsection_slide:
                    slides.append(subsection_slide)

        slides.append(
            DatapizzaSlide(
                slide_type=SlideType.CLOSING,
                title="Grazie",
                speaker_notes="Chiudi richiamando il principio chiave: non fidarti di un solo segnale.",
                image_prompt=cls._build_image_prompt(
                    slide_type=SlideType.CLOSING,
                    title="Grazie",
                    body="Chiusura della presentazione",
                    bullets=None,
                    is_workflow=False,
                    is_architecture=False,
                ),
            )
        )
        return SlideDeck(slides=slides)

    @classmethod
    def _restyle_image_prompt(cls, slide: DatapizzaSlide) -> DatapizzaSlide:
        title = slide.title
        body = slide.body or " ".join(slide.bullets[:2])
        bullets = slide.bullets[:4]
        is_workflow = cls._is_workflow_visual(title, body, bullets)
        is_architecture = cls._is_architecture_visual(title, body, bullets)
        return DatapizzaSlide(
            **{
                **slide.model_dump(mode="python"),
                "image_prompt": cls._build_image_prompt(
                    slide_type=slide.slide_type,
                    title=title,
                    body=body,
                    bullets=bullets,
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
                slide_type=SlideType.CLOSING,
                title="Grazie",
                body="Chiusura della presentazione",
                bullets=None,
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
        """Generate slides deterministically from the Markdown structure."""

        deck = self._build_deterministic_deck(markdown_text)
        normalized = [
            self._normalize_slide(slide, idx == len(deck.slides) - 1)
            for idx, slide in enumerate(deck.slides)
        ]
        repaired_slides = self._repair_deck_against_outline(markdown_text, normalized)
        return SlideDeck(slides=repaired_slides)
