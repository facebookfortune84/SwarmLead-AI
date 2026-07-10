class MetricsEngine:
    """
    Converts campaign/activity metrics into
    a normalized learning score (0.0 - 1.0).
    """

    def calculate_score(
        self,
        reply_rate=0.0,
        conversion_rate=0.0,
        engagement_score=0.0,
    ):
        """
        Inputs should already be normalized:
            0.0 -> 1.0
        """

        score = (reply_rate * 0.4) + (conversion_rate * 0.4) + (engagement_score * 0.2)

        return max(0.0, min(1.0, score))

    def score_campaign(self, metrics):
        return self.calculate_score(
            reply_rate=metrics.get("reply_rate", 0.0),
            conversion_rate=metrics.get("conversion_rate", 0.0),
            engagement_score=metrics.get("engagement_score", 0.0),
        )
