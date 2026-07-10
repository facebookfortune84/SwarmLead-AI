from core.prompts.adaptive_weights import AdaptiveWeightEngine


class FeedbackLoop:
    def __init__(self):
        self.weights = AdaptiveWeightEngine()

    def record_result(
        self,
        archetypes: dict,
        score: float,
    ):
        """
        score: 0.0 - 1.0
        """
        self.weights.update(
            archetypes=archetypes,
            score=score,
        )

        return self.weights.weights
