from core.prompts.adaptive_weights import AdaptiveWeightEngine


class FeedbackLoop:
    """
    Records campaign outcomes and updates adaptive archetype weights.
    """

    def __init__(self, weights_path="assets/optimized/archetype_weights.json"):
        self.engine = AdaptiveWeightEngine(path=weights_path)

    def record_result(
        self,
        archetypes: dict,
        score: float,
    ):
        """
        archetypes:
            {
                "planner": 0.6,
                "architect": 0.4,
            }

        score:
            0.0 - 1.0
        """

        self.engine.update(
            archetypes=archetypes,
            score=score,
        )

        return {
            "updated": True,
            "weights": self.engine.weights,
        }

    def get_weights(self):
        return self.engine.weights
