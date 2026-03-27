from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class AppConfig:
    model_cache_dir: Path = Path(os.getenv("MODEL_CACHE_DIR", ".cache/models"))
    voxtral_repo_id: str = os.getenv("VOXTRAL_REPO_ID", "mistralai/voxtral-tts-demo")
    voxtral_repo_type: str = os.getenv("VOXTRAL_REPO_TYPE", "space")

    def ensure_directories(self) -> None:
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def voxtral_local_dir(self) -> Path:
        slug = self.voxtral_repo_id.replace("/", "__")
        return self.model_cache_dir / "voxtral" / slug


def get_config() -> AppConfig:
    config = AppConfig()
    config.ensure_directories()
    return config
