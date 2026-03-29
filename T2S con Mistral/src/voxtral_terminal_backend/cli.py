from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import get_config
from .markdown_pipeline import MarkdownSpeechPipeline
from .mistral_api import MistralAPIConfigurationError, MistralAPIError, MistralCloudSynthesizer
from .model_store import download_voxtral_model, resolve_model_source
from .runtime import MissingRuntimeDependencyError, UnsupportedRuntimeError, inspect_runtime
from .service import MarkdownSynthesisRequest, VoxtralMarkdownSpeechPipeline
from .voxtral import VoxtralOfflineSynthesizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voxtral-backend",
        description="Backend terminal-first per markdown-to-speech con Voxtral e datapizza-ai.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser("download-model", help="Scarica il modello Voxtral in cache locale.")
    download_parser.add_argument("--force", action="store_true", help="Forza un nuovo snapshot del modello.")

    doctor_parser = subparsers.add_parser("doctor", help="Mostra stato runtime e dipendenze locali.")
    doctor_parser.add_argument(
        "--model-path",
        default=None,
        help="Percorso del modello locale. Se omesso usa la cache configurata o il repo HF.",
    )

    extract_parser = subparsers.add_parser(
        "extract-text",
        help="Estrae il testo speakable da un file markdown usando datapizza-ai.",
    )
    extract_parser.add_argument("--markdown", required=True, help="Percorso del file markdown.")

    speak_parser = subparsers.add_parser("speak-markdown", help="Legge un markdown usando Voxtral e audio.wav.")
    speak_parser.add_argument("--markdown", required=True, help="Percorso del file markdown.")
    speak_parser.add_argument(
        "--reference-audio",
        default=str(get_config().default_reference_audio),
        help="Percorso dell'audio di riferimento.",
    )
    speak_parser.add_argument(
        "--output",
        default=str(get_config().default_output_dir / "voxtral_output.wav"),
        help="Percorso del file wav generato.",
    )
    speak_parser.add_argument("--model-path", default=None, help="Percorso del modello locale gia' scaricato.")
    speak_parser.add_argument("--stage-configs-path", default=None, help="Percorso opzionale allo YAML stage config.")
    speak_parser.add_argument(
        "--engine",
        choices=["auto", "local", "cloud"],
        default="auto",
        help="Seleziona il backend di sintesi: locale con vllm-omni, cloud via Mistral API o auto.",
    )
    speak_parser.add_argument(
        "--cloud-model",
        default=None,
        help="Override del model id usato dal fallback cloud Mistral.",
    )
    speak_parser.add_argument(
        "--voice-id",
        default=None,
        help="Voice id Mistral opzionale. Se omesso usa ref_audio per il cloning.",
    )
    speak_parser.add_argument(
        "--max-chars-per-chunk",
        type=int,
        default=get_config().default_max_chars_per_chunk,
        help="Massimo numero di caratteri per chunk inviato a Voxtral.",
    )
    speak_parser.add_argument(
        "--max-tokens",
        type=int,
        default=get_config().default_max_tokens,
        help="Max token generati per chunk nel decoder.",
    )
    speak_parser.add_argument(
        "--silence-ms",
        type=int,
        default=get_config().default_silence_ms,
        help="Pausa tra chunk concatenati.",
    )

    return parser


def run_download(args: argparse.Namespace) -> int:
    voxtral_dir = download_voxtral_model(force=args.force)
    print(f"Modello Voxtral disponibile in: {voxtral_dir}")
    return 0


def run_extract_text(args: argparse.Namespace) -> int:
    pipeline = MarkdownSpeechPipeline()
    print(pipeline.render(args.markdown))
    return 0


def run_doctor(args: argparse.Namespace) -> int:
    report = inspect_runtime()
    model_source = resolve_model_source(args.model_path)
    config = get_config()

    print(f"Platform: {report.platform} ({report.machine})")
    print(f"Model source: {model_source}")
    print(f"vllm installed: {'yes' if report.has_vllm else 'no'}")
    print(f"vllm-omni installed: {'yes' if report.has_vllm_omni else 'no'}")
    print(f"torch installed: {'yes' if report.has_torch else 'no'}")
    print(f"MISTRAL_API_KEY configured: {'yes' if bool(config.mistral_api_key) else 'no'}")
    print(f"Mistral cloud model: {config.mistral_tts_model}")
    if report.cuda_available is None:
        print("CUDA available: unknown")
    else:
        print(f"CUDA available: {'yes' if report.cuda_available else 'no'}")
    print(f"Runtime ready: {'yes' if report.supported else 'no'}")
    if report.reasons:
        print("Blocking checks:")
        for reason in report.reasons:
            print(f"- {reason}")
    return 0


def run_speak(args: argparse.Namespace) -> int:
    markdown_path = Path(args.markdown)
    reference_audio = Path(args.reference_audio)
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown non trovato: {markdown_path}")
    if not reference_audio.exists():
        raise FileNotFoundError(f"Audio di riferimento non trovato: {reference_audio}")

    request = MarkdownSynthesisRequest(
        markdown_path=markdown_path,
        reference_audio_path=reference_audio,
        output_path=Path(args.output),
        max_chars_per_chunk=args.max_chars_per_chunk,
        max_tokens=args.max_tokens,
        silence_ms=args.silence_ms,
    )

    synthesizers = []
    if args.engine in {"auto", "local"}:
        synthesizers.append(
            (
                "local",
                VoxtralOfflineSynthesizer(
                    model_path=args.model_path,
                    stage_configs_path=args.stage_configs_path,
                ),
            )
        )
    if args.engine in {"auto", "cloud"}:
        try:
            synthesizers.append(
                (
                    "cloud",
                    MistralCloudSynthesizer(
                        model=args.cloud_model,
                        voice_id=args.voice_id,
                    ),
                )
            )
        except MistralAPIConfigurationError as exc:
            if args.engine == "cloud":
                print(str(exc), file=sys.stderr)
                return 2

    output_path: Path | None = None
    errors: list[str] = []
    for name, synthesizer in synthesizers:
        pipeline = VoxtralMarkdownSpeechPipeline(synthesizer=synthesizer)
        try:
            output_path = pipeline.run(request)
            print(f"Backend usato: {name}")
            break
        except (
            UnsupportedRuntimeError,
            MissingRuntimeDependencyError,
            MistralAPIConfigurationError,
            MistralAPIError,
        ) as exc:
            errors.append(f"[{name}] {exc}")

    if output_path is None:
        for error in errors:
            print(error, file=sys.stderr)
        return 2

    print(f"Audio generato in: {output_path}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "download-model":
        return run_download(args)
    if args.command == "doctor":
        return run_doctor(args)
    if args.command == "extract-text":
        return run_extract_text(args)
    if args.command == "speak-markdown":
        return run_speak(args)

    parser.error("Comando non supportato")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
