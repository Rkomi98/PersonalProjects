from pathlib import Path

from voxtral_terminal_backend.service import MarkdownSynthesisRequest, VoxtralMarkdownSpeechPipeline


class FakeSynthesizer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def synthesize_text(
        self,
        *,
        text: str,
        reference_audio_path: str | Path,
        output_path: str | Path,
        max_chars_per_chunk: int,
        max_tokens: int,
        silence_ms: int,
    ) -> Path:
        self.calls.append(
            {
                "text": text,
                "reference_audio_path": Path(reference_audio_path),
                "output_path": Path(output_path),
                "max_chars_per_chunk": max_chars_per_chunk,
                "max_tokens": max_tokens,
                "silence_ms": silence_ms,
            }
        )
        return Path(output_path)


def test_markdown_pipeline_builds_text_request_before_synthesis(tmp_path) -> None:
    markdown_file = tmp_path / "demo.md"
    markdown_file.write_text("# Demo\n\nQuesto e un test.\n\n- Primo punto\n- Secondo punto\n", encoding="utf-8")
    reference_audio = tmp_path / "voice.wav"
    reference_audio.write_bytes(b"fake")
    output_path = tmp_path / "result.wav"

    synthesizer = FakeSynthesizer()
    pipeline = VoxtralMarkdownSpeechPipeline(synthesizer=synthesizer)

    result = pipeline.run(
        MarkdownSynthesisRequest(
            markdown_path=markdown_file,
            reference_audio_path=reference_audio,
            output_path=output_path,
            max_chars_per_chunk=420,
            max_tokens=2500,
            silence_ms=120,
        )
    )

    assert result == output_path
    assert synthesizer.calls
    assert "Demo." in synthesizer.calls[0]["text"]
    assert "Primo punto." in synthesizer.calls[0]["text"]
