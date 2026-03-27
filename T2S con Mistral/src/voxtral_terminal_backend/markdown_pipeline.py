from __future__ import annotations

import re
from pathlib import Path
from tempfile import NamedTemporaryFile

from datapizza.core.models import PipelineComponent
from datapizza.modules.parsers.md_parser import MDParser
from datapizza.pipeline.pipeline import Pipeline
from datapizza.type import Node, NodeType


class SpeakableMarkdownParser(PipelineComponent):
    def __init__(self) -> None:
        self._parser = MDParser()

    def _run(self, markdown_path: str | Path) -> Node:
        markdown_path = Path(markdown_path)
        raw_markdown = markdown_path.read_text(encoding="utf-8")
        speakable_markdown = sanitize_markdown(raw_markdown)

        with NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=True) as tmp:
            tmp.write(speakable_markdown)
            tmp.flush()
            return self._parser.run(tmp.name, metadata={"source": str(markdown_path)})


class SpeechScriptRenderer(PipelineComponent):
    def _run(self, document_node: Node) -> str:
        parts: list[str] = []
        self._walk(document_node, parts)
        joined = " ".join(part.strip() for part in parts if part.strip())
        return normalize_spaces(joined)

    def _walk(self, node: Node, parts: list[str]) -> None:
        if node.node_type == NodeType.SECTION:
            title = node.metadata.get("title")
            if title:
                parts.append(f"{title}.")

        if node.node_type == NodeType.SENTENCE and node.content:
            parts.append(ensure_sentence_ending(node.content))

        for child in node.children:
            self._walk(child, parts)


def sanitize_markdown(raw_markdown: str) -> str:
    text = raw_markdown
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+(.*)$", r"\1.", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+(.*)$", r"\1.", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ensure_sentence_ending(text: str) -> str:
    cleaned = normalize_spaces(text)
    if not cleaned:
        return ""
    cleaned = re.sub(r"([.!?]){2,}$", r"\1", cleaned)
    if cleaned[-1] in ".!?":
        return cleaned
    return f"{cleaned}."


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class MarkdownSpeechPipeline:
    def __init__(self) -> None:
        self._pipeline = Pipeline(
            components=[
                SpeakableMarkdownParser(),
                SpeechScriptRenderer(),
            ]
        )

    def render(self, markdown_path: str | Path) -> str:
        return self._pipeline.run(str(markdown_path))
