from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

from .config import get_config


def download_voxtral_model(*, force: bool = False) -> Path:
    config = get_config()
    local_dir = config.voxtral_local_dir
    local_dir.mkdir(parents=True, exist_ok=True)

    if local_dir.exists() and any(local_dir.iterdir()) and not force:
        return local_dir

    snapshot_download(
        repo_id=config.voxtral_repo_id,
        repo_type="model",
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        token=config.hf_token,
    )
    return local_dir


def resolve_model_source(model_path: str | Path | None = None) -> str:
    if model_path is not None:
        candidate = Path(model_path).expanduser()
        if candidate.exists():
            return str(candidate.resolve())
        return str(model_path)

    config = get_config()
    if config.voxtral_local_dir.exists() and any(config.voxtral_local_dir.iterdir()):
        return str(config.voxtral_local_dir.resolve())
    return config.voxtral_repo_id
