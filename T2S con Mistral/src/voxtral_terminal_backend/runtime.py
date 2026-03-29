from __future__ import annotations

import importlib.util
import platform
from dataclasses import dataclass


class UnsupportedRuntimeError(RuntimeError):
    """Raised when the current machine cannot execute the official Voxtral runtime."""


class MissingRuntimeDependencyError(RuntimeError):
    """Raised when the machine is compatible but Python runtime deps are missing."""


@dataclass(slots=True)
class RuntimeReport:
    platform: str
    machine: str
    has_vllm: bool
    has_vllm_omni: bool
    has_torch: bool
    cuda_available: bool | None
    supported: bool
    reasons: list[str]


@dataclass(slots=True)
class VoxtralRuntimeBindings:
    Omni: type
    SamplingParams: type
    torch: object


def inspect_runtime() -> RuntimeReport:
    current_platform = platform.system()
    current_machine = platform.machine()
    has_vllm = importlib.util.find_spec("vllm") is not None
    has_vllm_omni = importlib.util.find_spec("vllm_omni") is not None
    has_torch = importlib.util.find_spec("torch") is not None

    reasons: list[str] = []
    cuda_available: bool | None = None
    if current_platform != "Linux":
        reasons.append(
            "Il runtime ufficiale di Voxtral con vllm/vllm-omni e' supportato lato progetto su host Linux."
        )
    if not has_vllm:
        reasons.append("Manca il pacchetto Python `vllm`.")
    if not has_vllm_omni:
        reasons.append("Manca il pacchetto Python `vllm-omni`.")
    if current_platform == "Linux":
        if not has_torch:
            reasons.append("Manca il pacchetto Python `torch`.")
        else:
            try:
                import torch

                cuda_available = bool(torch.cuda.is_available())
            except Exception as exc:  # pragma: no cover - defensive path for broken local torch installs
                reasons.append(f"Impossibile interrogare torch per CUDA: {exc.__class__.__name__}.")
            else:
                if cuda_available is False:
                    reasons.append("Torch non vede una GPU CUDA disponibile per l'inferenza locale.")

    supported = not reasons
    return RuntimeReport(
        platform=current_platform,
        machine=current_machine,
        has_vllm=has_vllm,
        has_vllm_omni=has_vllm_omni,
        has_torch=has_torch,
        cuda_available=cuda_available,
        supported=supported,
        reasons=reasons,
    )


def assert_supported_runtime() -> RuntimeReport:
    report = inspect_runtime()
    if report.platform != "Linux":
        raise UnsupportedRuntimeError(_format_runtime_error(report))
    if not report.has_vllm or not report.has_vllm_omni or report.cuda_available is False:
        raise MissingRuntimeDependencyError(_format_runtime_error(report))
    return report


def load_runtime_bindings() -> VoxtralRuntimeBindings:
    assert_supported_runtime()

    import torch
    from vllm import SamplingParams
    from vllm_omni.entrypoints.omni import Omni

    return VoxtralRuntimeBindings(Omni=Omni, SamplingParams=SamplingParams, torch=torch)


def _format_runtime_error(report: RuntimeReport) -> str:
    reason_block = "\n".join(f"- {reason}" for reason in report.reasons)
    return (
        f"Runtime Voxtral non pronto su questa macchina ({report.platform} {report.machine}).\n"
        f"{reason_block}\n"
        "Per la sintesi locale usa un host Linux con GPU supportata, installa `vllm>=0.18.0` e "
        "`vllm-omni` da `main`, poi rilancia `speak-markdown`."
    )
