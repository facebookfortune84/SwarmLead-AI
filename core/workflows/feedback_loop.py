from core.prompts.adaptive_weights import AdaptiveWeightEngine


class FeedbackLoop:
    def __init__(self):
        self.engine = AdaptiveWeightEngine()

    def record_result(
        self,
        archetypes: dict,
        score: float,
    ):
        """
        score range: 0.0 - 1.0
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
