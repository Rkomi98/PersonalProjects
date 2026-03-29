import base64
from pathlib import Path

import pytest

from voxtral_terminal_backend.mistral_api import (
    MistralAPIConfigurationError,
    MistralAPIError,
    MistralCloudSynthesizer,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, str] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict[str, str]:
        return self._payload


class FakeClient:
    def __init__(self, response: FakeResponse, recorder: list[dict[str, object]]) -> None:
        self._response = response
        self._recorder = recorder

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url: str, *, headers: dict[str, str], json: dict[str, object]) -> FakeResponse:
        self._recorder.append({"url": url, "headers": headers, "json": json})
        return self._response


def test_cloud_synthesizer_requires_api_key() -> None:
    with pytest.raises(MistralAPIConfigurationError):
        MistralCloudSynthesizer(api_key="")


def test_cloud_synthesizer_writes_wav_bytes(monkeypatch, tmp_path: Path) -> None:
    reference_audio = tmp_path / "voice.wav"
    reference_audio.write_bytes(b"voice-bytes")
    output_path = tmp_path / "out.wav"
    recorder: list[dict[str, object]] = []
    payload = {"audio_data": base64.b64encode(b"wav-bytes").decode("utf-8")}

    monkeypatch.setattr(
        "voxtral_terminal_backend.mistral_api.httpx.Client",
        lambda timeout: FakeClient(FakeResponse(200, payload=payload), recorder),
    )

    synthesizer = MistralCloudSynthesizer(api_key="test-key", model="tts-model")
    result = synthesizer.synthesize_text(
        text="Ciao dal cloud",
        reference_audio_path=reference_audio,
        output_path=output_path,
    )

    assert result == output_path
    assert output_path.read_bytes() == b"wav-bytes"
    assert recorder[0]["json"]["model"] == "tts-model"
    assert recorder[0]["json"]["ref_audio"] == base64.b64encode(b"voice-bytes").decode("utf-8")


def test_cloud_synthesizer_raises_on_api_error(monkeypatch, tmp_path: Path) -> None:
    reference_audio = tmp_path / "voice.wav"
    reference_audio.write_bytes(b"voice-bytes")
    recorder: list[dict[str, object]] = []

    monkeypatch.setattr(
        "voxtral_terminal_backend.mistral_api.httpx.Client",
        lambda timeout: FakeClient(FakeResponse(401, text="unauthorized"), recorder),
    )

    synthesizer = MistralCloudSynthesizer(api_key="test-key")
    with pytest.raises(MistralAPIError):
        synthesizer.synthesize_text(
            text="Ciao dal cloud",
            reference_audio_path=reference_audio,
            output_path=tmp_path / "out.wav",
        )
