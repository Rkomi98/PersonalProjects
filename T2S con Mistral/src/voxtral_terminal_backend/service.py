from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from datapizza.core.models import PipelineComponent
from datapizza.pipeline.pipeline import Pipeline

from .markdown_pipeline import MarkdownSpeechPipeline


@dataclass(slots=True)
class MarkdownSynthesisRequest:
    markdown_path: Path
    reference_audio_path: Path
    output_path: Path
    max_chars_per_chunk: int
    max_tokens: int
    silence_ms: int


@dataclass(slots=True)
class TextSynthesisRequest:
    text: str
    reference_audio_path: Path
    output_path: Path
    max_chars_per_chunk: int
    max_tokens: int
    silence_ms: int


class MarkdownToTextRequestComponent(PipelineComponent):
    def __init__(self, markdown_pipeline: MarkdownSpeechPipeline | None = None) -> None:
        self._markdown_pipeline = markdown_pipeline or MarkdownSpeechPipeline()

    def _run(self, request: MarkdownSynthesisRequest) -> TextSynthesisRequest:
        text = self._markdown_pipeline.render(request.markdown_path)
        return TextSynthesisRequest(
            text=text,
            reference_audio_path=request.reference_audio_path,
            output_path=request.output_path,
            max_chars_per_chunk=request.max_chars_per_chunk,
            max_tokens=request.max_tokens,
            silence_ms=request.silence_ms,
        )


class VoxtralSynthesisComponent(PipelineComponent):
    def __init__(self, synthesizer) -> None:
        self._synthesizer = synthesizer

    def _run(self, request: TextSynthesisRequest) -> Path:
        return self._synthesizer.synthesize_text(
            text=request.text,
            reference_audio_path=request.reference_audio_path,
            output_path=request.output_path,
            max_chars_per_chunk=request.max_chars_per_chunk,
            max_tokens=request.max_tokens,
            silence_ms=request.silence_ms,
        )


class VoxtralMarkdownSpeechPipeline:
    def __init__(self, synthesizer, markdown_pipeline: MarkdownSpeechPipeline | None = None) -> None:
        self._pipeline = Pipeline(
            components=[
                MarkdownToTextRequestComponent(markdown_pipeline=markdown_pipeline),
                VoxtralSynthesisComponent(synthesizer=synthesizer),
            ]
        )

    def run(self, request: MarkdownSynthesisRequest) -> Path:
        return self._pipeline.run(request)
