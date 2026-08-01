"""
Product Knowledge Base — grounds the voice agent in the project's own docs.

Loads markdown from docs/ (founder intent, operations, agents, governance,
marketing plan), chunks it by headings, and retrieves the most relevant
sections for a user message so the voice assistant can answer real
"how do I use Genesis / how do I run my business" questions.

The local LLM (llama3.2:3b) has a small context window, so we only inject a
tight, bounded slice of the highest-scoring chunks per turn.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Docs the voice assistant is "trained" on. Paths are relative to the repo root.
INCLUDE_DIRS = [
    "docs/founder",
    "docs/agents",
    "docs/governance",
    "docs/operations",
    "docs/marketing_voice.md",
    "docs/marketing_voice_plan.md",
    "docs/marketing_voice_variation.md",
]

MAX_CHUNK_CHARS = 800
MAX_INJECT_CHARS = 1600
TOP_K = 4


class ProductKnowledgeBase:
    """Chunked, keyword-scored retrieval over the project docs."""

    def __init__(self, docs_root: Optional[str] = None, repo_root: Optional[str] = None):
        self._chunks: List[Dict] = []
        root = Path(repo_root or ".").resolve()
        docs_path = Path(docs_root or (root / "docs"))
        self._load(docs_path)

    def _load(self, docs_path: Path) -> None:
        loaded = 0
        for pattern in self._path_patterns():
            for path in self._expand(pattern, docs_path):
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError as exc:
                    logger.debug("Skipping %s: %s", path, exc)
                    continue
                for chunk in self._chunk(text, path):
                    self._chunks.append(chunk)
                    loaded += 1
        logger.info("Product knowledge loaded %d chunks from %s", loaded, docs_path)

    def _path_patterns(self) -> List[str]:
        patterns = []
        for entry in INCLUDE_DIRS:
            if entry.endswith(".md"):
                patterns.append(entry)
            else:
                patterns.append(f"{entry}/*.md")
        return patterns

    def _expand(self, pattern: str, docs_path: Path) -> List[Path]:
        if pattern.startswith("docs/"):
            candidate = Path(pattern)
            if candidate.is_file():
                return [candidate]
            return sorted(candidate.parent.glob(candidate.name)) if candidate.parent.exists() else []
        return sorted(docs_path.glob(pattern)) if docs_path.exists() else []

    def _chunk(self, text: str, path: Path) -> List[Dict]:
        """Split markdown into heading-anchored chunks (bounded size)."""
        lines = text.splitlines()
        chunks: List[Dict] = []
        title = path.stem.replace("_", " ").title()
        section_title = title
        buf: List[str] = []
        buf_chars = 0

        def flush() -> None:
            nonlocal buf, buf_chars
            if buf:
                body = "\n".join(buf).strip()
                if body:
                    chunks.append(
                        {
                            "source": str(path),
                            "title": section_title,
                            "text": body[:MAX_CHUNK_CHARS],
                        }
                    )
            buf = []
            buf_chars = 0

        for line in lines:
            heading = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
            if heading and buf_chars > 120:
                flush()
                section_title = heading.group(2).strip()
                continue
            if heading and not buf:
                section_title = heading.group(2).strip()
                continue
            buf.append(line)
            buf_chars += len(line) + 1
            if buf_chars >= MAX_CHUNK_CHARS:
                flush()
        flush()
        return chunks

    def retrieve(self, query: str, top_k: int = TOP_K, max_chars: int = MAX_INJECT_CHARS) -> List[Dict]:
        """Return the top chunks by keyword overlap with the query."""
        if not self._chunks or not query:
            return []

        q_terms = self._terms(query)

        scored = []
        for chunk in self._chunks:
            text = chunk["text"].lower()
            score = sum(2 if t in chunk["title"].lower() else 1 for t in q_terms if t in text)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)

        chosen: List[Dict] = []
        budget = 0
        for _, chunk in scored[:top_k]:
            budget += len(chunk["text"])
            if budget > max_chars:
                break
            chosen.append(chunk)
        return chosen

    @staticmethod
    def _terms(query: str) -> List[str]:
        words = re.findall(r"[a-z0-9]+", query.lower())
        stop = {
            "the", "a", "an", "and", "or", "of", "to", "for", "with", "how",
            "what", "do", "does", "is", "are", "can", "you", "i", "me", "my",
            "in", "on", "it", "that", "this", "about", "help", "want",
        }
        return [w for w in words if w not in stop][:24]

    def format_context(
        self, query: str, top_k: int = TOP_K, max_chars: int = MAX_INJECT_CHARS
    ) -> str:
        """Format retrieved chunks as an injectable context block."""
        chunks = self.retrieve(query, top_k=top_k, max_chars=max_chars)
        if not chunks:
            return ""
        parts = []
        for c in chunks:
            parts.append(f"[Source: {c['title']}]\n{c['text']}")
        return "\n\n".join(parts)


product_knowledge = ProductKnowledgeBase()

__all__ = ["ProductKnowledgeBase", "product_knowledge"]
