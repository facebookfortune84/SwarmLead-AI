import json
from pathlib import Path


class AssetLoader:
    def __init__(self, path="assets/optimized/optimized_archetypes.json"):
        self.path = Path(path)
        self.data = self._load()

    def _load(self):
        if not self.path.exists():
            return {"archetypes": {}}

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # ✅ handle empty file
            if not content:
                return {"archetypes": {}}

            return json.loads(content)

        except Exception:
            # ✅ handle invalid JSON safely
            return {"archetypes": {}}

    def get(self, archetype):
        return self.data["archetypes"].get(archetype, [])

    def build_context(self, archetypes_with_weights):
        lines = []

        for archetype, weight in archetypes_with_weights.items():
            entries = self.get(archetype)

            for e in entries:
                # ✅ support BOTH new + old formats
                content = e.get("text") or e.get("source")

                if not content:
                    continue

                lines.append(f"[{archetype} | weight={round(weight, 2)}] {content}")

        return "\n".join(lines)
