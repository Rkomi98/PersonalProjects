from voxtral_terminal_backend.markdown_pipeline import (
    MarkdownSpeechPipeline,
    ensure_sentence_ending,
    sanitize_markdown,
)


def test_sanitize_markdown_removes_links_and_code() -> None:
    raw = "# Titolo\n\nVai su [Mistral](https://mistral.ai) e usa `python`.\n\n```py\nprint('x')\n```"
    cleaned = sanitize_markdown(raw)
    assert "https://mistral.ai" not in cleaned
    assert "print('x')" not in cleaned
    assert "Mistral" in cleaned
    assert "python" in cleaned


def test_ensure_sentence_ending_adds_period() -> None:
    assert ensure_sentence_ending("Ciao mondo") == "Ciao mondo."


def test_markdown_pipeline_renders_titles_and_text(tmp_path) -> None:
    markdown_file = tmp_path / "demo.md"
    markdown_file.write_text("# Demo\n\nQuesto e un test.\n\n## Sezione\n\n- Punto uno\n- Punto due\n", encoding="utf-8")

    pipeline = MarkdownSpeechPipeline()
    rendered = pipeline.render(markdown_file)

    assert "Demo." in rendered
    assert "Sezione." in rendered
    assert "Punto uno." in rendered
    assert "Punto due." in rendered
