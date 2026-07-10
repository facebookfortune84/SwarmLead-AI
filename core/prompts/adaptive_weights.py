import json
from pathlib import Path


class AdaptiveWeightEngine:
    def __init__(self, path="assets/optimized/archetype_weights.json"):
        self.path = Path(path)
        self.weights = self._load()

    def _load(self):
        if not self.path.exists():
            return {}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, indent=2)

    # ------------------------------------------------------------------
    # GET WEIGHTS
    # ------------------------------------------------------------------

    def get(self, base_weights):
        """
        Merge base weights with learned weights
        """

        result = base_weights.copy()

        for k, v in self.weights.items():
            if k in result:
                result[k] *= 1 + v

        return result

    # ------------------------------------------------------------------
    # UPDATE WEIGHTS (LEARNING)
    # ------------------------------------------------------------------

    def update(self, archetypes, score: float):
        """
        score: 0.0 - 1.0 (performance rating)
        """

        for k in archetypes:
            current = self.weights.get(k, 0)

            # ✅ simple reinforcement learning
            adjustment = (score - 0.5) * 0.1

            self.weights[k] = max(-0.5, min(0.5, current + adjustment))

        self._save()
