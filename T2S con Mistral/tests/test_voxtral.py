from voxtral_terminal_backend.model_store import resolve_model_source
from voxtral_terminal_backend.voxtral import split_text_for_tts


def test_split_text_for_tts_splits_long_text() -> None:
    text = (
        "Questa e una frase abbastanza lunga da richiedere uno split. "
        "Questa e un'altra frase che aiuta a creare piu chunk."
    )
    chunks = split_text_for_tts(text, max_chars=45)

    assert len(chunks) >= 2
    assert all(chunk.strip() for chunk in chunks)


def test_split_text_for_tts_handles_empty_input() -> None:
    assert split_text_for_tts("   ") == []


def test_resolve_model_source_preserves_remote_repo_id() -> None:
    assert resolve_model_source("mistralai/Voxtral-4B-TTS-2603") == "mistralai/Voxtral-4B-TTS-2603"
