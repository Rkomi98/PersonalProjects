"""High level orchestration that asks datapizza/OpenAI to author a slide deck."""
from __future__ import annotations

import json
from dataclasses import dataclass

from datapizza.clients.openai import OpenAIClient

from .slide_models import SlideDeck


@dataclass
class SlideGeneratorConfig:
    api_key: str
    model_name: str
    system_prompt: str
    temperature: float
    style_prompt: str


class SlideGenerationService:
    """Generate structured slides leveraging datapizza's OpenAI client."""

    def __init__(self, config: SlideGeneratorConfig):
        self.config = config
        self.client = OpenAIClient(
            api_key=config.api_key,
            model=config.model_name,
            system_prompt=config.system_prompt,
            temperature=config.temperature,
        )
        self._schema = json.dumps(SlideDeck.model_json_schema(), ensure_ascii=False)

    def _build_prompt(
        self,
        *,
        topic: str,
        requested_slides: int,
        language: str,
    ) -> str:
        """Compose the textual prompt passed to the LLM."""

        guide = f"""Devi progettare una presentazione aziendale in {language}.\n"""
        tone_rules = (
            "Scrivi con tono professionale, concreto e orientato all'impatto. "
            "I titoli devono essere phrasing "
            "da consultivo e in sentence case. Usa numeri e metriche dove possibili."
        )
        visual_rules = (
            "Per ogni slide scegli il layout migliore impostando il campo layout tra "
            "'text_only', 'split' oppure 'visual_full'. "
            "Quando il visual è rilevante genera un SVG inline completo in stile Datapizza "
            "all'interno di visual.svg_markup e descrivilo con type/description/caption. "
            "Se il visual non è necessario lascia visual null. L'SVG non è obbligatorio."
        )

        return (
            f"{guide}{tone_rules}\n\n"
            f"VISUAL E SVG\n-------------\n{visual_rules}\n\n"
            f"STILE\n-----\n{self.config.style_prompt}\n\n"
            f"REQUISITI\n---------\n"
            f"- Genera esattamente {requested_slides} slide operative tra introduzione e chiusura.\n"
            "- Ogni slide deve avere titolo, key message, bullet brevi e note speaker.\n"
            "- Quando utile indica anche un visual coerente col messaggio.\n"
            "- Non ripetere le stesse idee, crea una narrativa progressiva (situazione, problem, solution, next step).\n"
            "- Niente markdown nel testo finale.\n\n"
            f"FORMATO JSON\n-------------\nRispetta esattamente questo schema: {self._schema}.\n"
            "Rispondi esclusivamente con un JSON valido, senza backtick.\n\n"
            f"TOPIC\n-----\n{topic.strip()}\n"
        )

    def generate(
        self,
        *,
        topic: str,
        requested_slides: int,
        language: str = "Italiano",
    ) -> SlideDeck:
        """Call the LLM and parse the resulting slide deck."""

        prompt = self._build_prompt(
            topic=topic,
            requested_slides=requested_slides,
            language=language,
        )
        response = self.client.structured_response(input=prompt, output_cls=SlideDeck)
        if not response.structured_data:
            raise RuntimeError("Il modello non ha restituito dati strutturati.")
        deck = response.structured_data[0]
        return deck
