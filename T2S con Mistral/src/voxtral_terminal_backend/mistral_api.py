from __future__ import annotations

import base64
from pathlib import Path

import httpx

from .config import get_config


class MistralAPIConfigurationError(RuntimeError):
    """Raised when cloud TTS is requested without a valid Mistral API setup."""


class MistralAPIError(RuntimeError):
    """Raised when the Mistral Audio Speech API returns an error."""


class MistralCloudSynthesizer:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        voice_id: str | None = None,
        timeout_seconds: float = 180.0,
    ) -> None:
        config = get_config()
        self.api_key = config.mistral_api_key if api_key is None else api_key
        self.base_url = (config.mistral_api_base_url if base_url is None else base_url).rstrip("/")
        self.model = config.mistral_tts_model if model is None else model
        self.voice_id = config.mistral_voice_id if voice_id is None else voice_id
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            raise MistralAPIConfigurationError(
                "MISTRAL_API_KEY non configurata. Inseriscila nel file .env per usare il fallback cloud."
            )

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
        del max_chars_per_chunk
        del max_tokens
        del silence_ms

        reference_audio_path = Path(reference_audio_path)
        if not reference_audio_path.exists():
            raise FileNotFoundError(f"Audio di riferimento non trovato: {reference_audio_path}")

        ref_audio_b64 = base64.b64encode(reference_audio_path.read_bytes()).decode("utf-8")
        payload: dict[str, object] = {
            "input": text,
            "model": self.model,
            "response_format": "wav",
            "ref_audio": ref_audio_b64,
        }
        if self.voice_id:
            payload["voice_id"] = self.voice_id

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                f"{self.base_url}/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.status_code >= 400:
            raise MistralAPIError(
                f"Mistral Audio Speech API ha risposto con {response.status_code}: {response.text}"
            )

        audio_data_b64 = response.json().get("audio_data")
        if not audio_data_b64:
            raise MistralAPIError("La risposta dell'API non contiene `audio_data`.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(base64.b64decode(audio_data_b64))
        return output_path
