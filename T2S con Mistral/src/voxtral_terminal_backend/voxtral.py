from __future__ import annotations

import gc
import re
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from mistral_common.protocol.instruct.chunk import TextChunk
from mistral_common.protocol.speech.request import SpeechRequest
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

from .model_store import resolve_model_source
from .runtime import load_runtime_bindings

DEFAULT_SAMPLE_RATE = 24_000


def split_text_for_tts(text: str, max_chars: int = 420) -> list[str]:
    cleaned = normalize_spaces(text)
    if not cleaned:
        return []

    sentence_parts = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: list[str] = []
    current = ""

    for sentence in sentence_parts:
        sentence = sentence.strip()
        if not sentence:
            continue

        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(sentence) <= max_chars:
            current = sentence
            continue

        words = sentence.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip() if current else word
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = word

    if current:
        chunks.append(current)

    return chunks


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class VoxtralOfflineSynthesizer:
    def __init__(
        self,
        *,
        model_path: str | Path | None = None,
        stage_configs_path: str | Path | None = None,
        log_stats: bool = False,
    ) -> None:
        self.model_source = resolve_model_source(model_path)
        self.stage_configs_path = str(Path(stage_configs_path).expanduser().resolve()) if stage_configs_path else None
        self.log_stats = log_stats
        self._tokenizer: MistralTokenizer | None = None

    def synthesize_text(
        self,
        *,
        text: str,
        reference_audio_path: str | Path,
        output_path: str | Path,
        max_chars_per_chunk: int = 420,
        max_tokens: int = 2500,
        silence_ms: int = 120,
    ) -> Path:
        text_chunks = split_text_for_tts(text, max_chars=max_chars_per_chunk)
        if not text_chunks:
            raise ValueError("Il testo da sintetizzare e' vuoto.")

        reference_audio_path = Path(reference_audio_path)
        if not reference_audio_path.exists():
            raise FileNotFoundError(f"Audio di riferimento non trovato: {reference_audio_path}")

        bindings = load_runtime_bindings()
        llm = bindings.Omni(
            model=self.model_source,
            stage_configs_path=self.stage_configs_path,
            log_stats=self.log_stats,
        )

        try:
            inputs = [self.compose_request(chunk, reference_audio_path) for chunk in text_chunks]
            sampling_params = bindings.SamplingParams(max_tokens=max_tokens)
            sampling_params_list = [sampling_params, sampling_params]
            outputs = llm.generate(inputs, sampling_params_list)
            audio_array = self._merge_outputs(outputs, bindings.torch, silence_ms=silence_ms)
        finally:
            del llm
            if bindings.torch.cuda.is_available():
                bindings.torch.cuda.empty_cache()
            gc.collect()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, audio_array, DEFAULT_SAMPLE_RATE)
        return output_path

    def compose_request(self, text: str, reference_audio_path: str | Path) -> dict[str, Any]:
        text_chunk = TextChunk(text=text)

        with Path(reference_audio_path).open("rb") as handle:
            ref_audio_bytes = handle.read()

        tokenized = self._get_tokenizer().instruct_tokenizer.encode_speech_request(
            SpeechRequest(input=text_chunk.text, ref_audio=ref_audio_bytes)
        )
        audio = tokenized.audios[0]
        return {
            "multi_modal_data": {"audio": [(audio.audio_array, audio.sampling_rate)]},
            "prompt_token_ids": tokenized.tokens,
        }

    def _get_tokenizer(self) -> MistralTokenizer:
        if self._tokenizer is None:
            model_path = Path(self.model_source)
            if model_path.is_dir():
                self._tokenizer = MistralTokenizer.from_file(str(model_path / "tekken.json"))
            else:
                self._tokenizer = MistralTokenizer.from_hf_hub(self.model_source)
        return self._tokenizer

    def _merge_outputs(self, outputs: list[Any], torch_module: Any, *, silence_ms: int) -> np.ndarray:
        rendered_parts: list[np.ndarray] = []
        silence_samples = int(DEFAULT_SAMPLE_RATE * (silence_ms / 1000))

        for index, output in enumerate(outputs):
            audio_chunks = output.multimodal_output.get("audio")
            if not audio_chunks:
                raise RuntimeError(f"Nessun audio prodotto dal chunk {index}.")

            audio_tensor = torch_module.cat(audio_chunks)
            rendered_parts.append(audio_tensor.float().detach().cpu().numpy())
            if silence_samples > 0 and index < len(outputs) - 1:
                rendered_parts.append(np.zeros(silence_samples, dtype=np.float32))

        return np.concatenate(rendered_parts).astype(np.float32)
