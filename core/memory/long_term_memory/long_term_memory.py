import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class LongTermMemory:
    """
    Persistent storage for historical campaign learnings,
    outreach performance, strategy insights and feedback.

    Records are stored as plain JSON and enriched with
    metadata to support retrieval across agents.
    """

    def __init__(
        self,
        path: str = "data/long_term_memory.json",
    ):
        self.path = Path(path)
        self.memory = self._load()

    # ---------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------

    def _load(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []

        try:
            with open(
                self.path,
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

            return []

        except Exception:
            return []

    def _save(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.memory,
                f,
                indent=2,
                ensure_ascii=False,
            )

    # ---------------------------------------------------------
    # Core Operations
    # ---------------------------------------------------------

    def add(
        self,
        record: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Add a raw memory record.

        Automatically enriches missing metadata.
        """

        entry = dict(record)

        entry.setdefault(
            "created_at",
            datetime.now(timezone.utc).isoformat(),
        )

        entry.setdefault(
            "type",
            "general",
        )

        self.memory.append(entry)

        self._save()

        return entry

    def add_learning(
        self,
        content: str,
        memory_type: str = "feedback",
        score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convenience method used by FeedbackLoop.
        """

        record = {
            "type": memory_type,
            "content": content,
            "score": score,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.memory.append(record)

        self._save()

        return record

    def all(self) -> List[Dict[str, Any]]:
        return list(self.memory)

    def count(self) -> int:
        return len(self.memory)

    def clear(self) -> None:
        self.memory = []
        self._save()

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def find(
        self,
        key: str,
        value: Any,
    ) -> List[Dict[str, Any]]:
        return [record for record in self.memory if record.get(key) == value]

    def find_by_type(
        self,
        memory_type: str,
    ) -> List[Dict[str, Any]]:
        return self.find(
            "type",
            memory_type,
        )

    def latest(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        return list(self.memory[-limit:])

    def search_text(
        self,
        text: str,
    ) -> List[Dict[str, Any]]:
        text = text.lower()

        results = []

        for record in self.memory:
            content = str(record.get("content", "")).lower()

            if text in content:
                results.append(record)

        return results
