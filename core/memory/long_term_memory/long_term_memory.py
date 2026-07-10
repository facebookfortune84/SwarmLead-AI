import json
from pathlib import Path


class LongTermMemory:
    """
    Persistent memory storage for
    campaign learnings, insights,
    and historical knowledge.
    """

    def __init__(
        self,
        path="data/long_term_memory.json",
    ):
        self.path = Path(path)
        self.memory = self._load()

    def _load(self):
        if not self.path.exists():
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception:
            return []

    def _save(self):
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
            )

    def add(self, record):
        self.memory.append(record)
        self._save()

    def all(self):
        return list(self.memory)

    def count(self):
        return len(self.memory)

    def clear(self):
        self.memory = []
        self._save()

    def find(self, key, value):
        return [record for record in self.memory if record.get(key) == value]
