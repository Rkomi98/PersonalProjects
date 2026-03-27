from __future__ import annotations

import torch


def resolve_torch_device(requested: str | None = None) -> str:
    if requested:
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"
