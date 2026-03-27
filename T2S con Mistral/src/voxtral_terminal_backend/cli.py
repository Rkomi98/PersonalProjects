from __future__ import annotations

import argparse
from pathlib import Path

from .markdown_pipeline import MarkdownSpeechPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voxtral-backend",
        description="Backend locale per parsing markdown e voice cloning da terminale.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser("download", help="Scarica gli asset necessari.")
    download_parser.add_argument(
        "--skip-voxtral",
        action="store_true",
        help="Salta il download degli asset collegati a Voxtral.",
    )
    download_parser.add_argument(
        "--device",
        default=None,
        help="Dispositivo torch per il preload del modello TTS: cpu, mps o cuda.",
    )

    extract_parser = subparsers.add_parser(
        "extract-text",
        help="Estrae il testo speakable da un file markdown usando datapizza-ai.",
    )
    extract_parser.add_argument("--markdown", required=True, help="Percorso del file markdown.")

    speak_parser = subparsers.add_parser(
        "speak",
        help="Legge un markdown con voce clonata a partire da audio.wav.",
    )
    speak_parser.add_argument("--markdown", required=True, help="Percorso del file markdown.")
    speak_parser.add_argument(
        "--reference-audio",
        default="audio.wav",
        help="Percorso dell'audio di riferimento.",
    )
    speak_parser.add_argument(
        "--output",
        default="outputs/output.wav",
        help="Percorso del file wav generato.",
    )
    speak_parser.add_argument("--device", default=None, help="Dispositivo torch: cpu, mps o cuda.")
    speak_parser.add_argument("--exaggeration", type=float, default=0.5)
    speak_parser.add_argument("--cfg-weight", type=float, default=0.5)
    speak_parser.add_argument("--temperature", type=float, default=0.8)

    return parser


def run_download(args: argparse.Namespace) -> int:
    from .models import download_voice_cloner_assets, download_voxtral_assets

    if not args.skip_voxtral:
        voxtral_dir = download_voxtral_assets()
        print(f"Asset Voxtral scaricati in: {voxtral_dir}")

    device = download_voice_cloner_assets(device=args.device)
    print(f"Modello di voice cloning pronto su device: {device}")
    return 0


def run_extract_text(args: argparse.Namespace) -> int:
    pipeline = MarkdownSpeechPipeline()
    print(pipeline.render(args.markdown))
    return 0


def run_speak(args: argparse.Namespace) -> int:
    from .tts import VoiceCloningService

    markdown_path = Path(args.markdown)
    reference_audio = Path(args.reference_audio)
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown non trovato: {markdown_path}")
    if not reference_audio.exists():
        raise FileNotFoundError(f"Audio di riferimento non trovato: {reference_audio}")

    service = VoiceCloningService(device=args.device)
    output_path = service.synthesize_markdown(
        markdown_path=markdown_path,
        reference_audio_path=reference_audio,
        output_path=args.output,
        exaggeration=args.exaggeration,
        cfg_weight=args.cfg_weight,
        temperature=args.temperature,
    )
    print(f"Audio generato in: {output_path}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "download":
        return run_download(args)
    if args.command == "extract-text":
        return run_extract_text(args)
    if args.command == "speak":
        return run_speak(args)

    parser.error("Comando non supportato")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
