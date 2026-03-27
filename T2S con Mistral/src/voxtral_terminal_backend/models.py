from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

from .config import get_config
from .devices import resolve_torch_device


def download_voxtral_assets() -> Path:
    config = get_config()
    local_dir = config.voxtral_local_dir
    local_dir.mkdir(parents=True, exist_ok=True)

    snapshot_download(
        repo_id=config.voxtral_repo_id,
        repo_type=config.voxtral_repo_type,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
    )
    return local_dir


def download_voice_cloner_assets(device: str | None = None) -> str:
    import perth
    from chatterbox.tts import ChatterboxTTS

    if getattr(perth, "PerthImplicitWatermarker", None) is None:
        perth.PerthImplicitWatermarker = perth.DummyWatermarker

    resolved_device = resolve_torch_device(device)
    ChatterboxTTS.from_pretrained(device=resolved_device)
    return resolved_device
