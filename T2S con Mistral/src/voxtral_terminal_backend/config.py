from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class AppConfig:
    model_cache_dir: Path = Path(os.getenv("MODEL_CACHE_DIR", ".cache/models"))
    voxtral_repo_id: str = os.getenv("VOXTRAL_REPO_ID", "mistralai/Voxtral-4B-TTS-2603")
    default_reference_audio: Path = Path(os.getenv("DEFAULT_REFERENCE_AUDIO", "audio.wav"))
    default_output_dir: Path = Path(os.getenv("DEFAULT_OUTPUT_DIR", "outputs"))
    default_max_chars_per_chunk: int = int(os.getenv("DEFAULT_MAX_CHARS_PER_CHUNK", "420"))
    default_max_tokens: int = int(os.getenv("DEFAULT_MAX_TOKENS", "2500"))
    default_silence_ms: int = int(os.getenv("DEFAULT_SILENCE_MS", "120"))
    hf_token: str | None = os.getenv("HF_TOKEN")
    mistral_api_key: str | None = os.getenv("MISTRAL_API_KEY")
    mistral_api_base_url: str = os.getenv("MISTRAL_API_BASE_URL", "https://api.mistral.ai")
    mistral_tts_model: str = os.getenv("MISTRAL_TTS_MODEL", "mistralai/Voxtral-4B-TTS-2603")
    mistral_voice_id: str | None = os.getenv("MISTRAL_VOICE_ID")

    def ensure_directories(self) -> None:
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def voxtral_local_dir(self) -> Path:
        return self.model_cache_dir / "voxtral" / self.voxtral_repo_id.replace("/", "__")


def get_config() -> AppConfig:
    config = AppConfig()
    config.ensure_directories()
    return config
