from __future__ import annotations

from pathlib import Path

import torchaudio

from .devices import resolve_torch_device
from .markdown_pipeline import MarkdownSpeechPipeline


class VoiceCloningService:
    def __init__(self, device: str | None = None) -> None:
        self.device = resolve_torch_device(device)
        self._model = self._load_model()
        self._pipeline = MarkdownSpeechPipeline()

    def _load_model(self):
        import perth
        from chatterbox.tts import ChatterboxTTS

        if getattr(perth, "PerthImplicitWatermarker", None) is None:
            perth.PerthImplicitWatermarker = perth.DummyWatermarker

        return ChatterboxTTS.from_pretrained(device=self.device)

    def extract_script(self, markdown_path: str | Path) -> str:
        return self._pipeline.render(markdown_path)

    def synthesize_markdown(
        self,
        markdown_path: str | Path,
        reference_audio_path: str | Path,
        output_path: str | Path,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8,
    ) -> Path:
        script = self.extract_script(markdown_path)
        return self.synthesize_text(
            text=script,
            reference_audio_path=reference_audio_path,
            output_path=output_path,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            temperature=temperature,
        )

    def synthesize_text(
        self,
        text: str,
        reference_audio_path: str | Path,
        output_path: str | Path,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8,
    ) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        wav = self._model.generate(
            text=text,
            audio_prompt_path=str(reference_audio_path),
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            temperature=temperature,
        )
        torchaudio.save(str(output_path), wav, self._model.sr)
        return output_path
