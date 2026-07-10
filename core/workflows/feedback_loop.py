from typing import Any, Dict, Optional

from core.analytics.event_tracker import EventTracker
from core.prompts.adaptive_weights import AdaptiveWeightEngine


# Fallback minimal implementation if the real LongTermMemory is unavailable
class LongTermMemory:
    def __init__(self):
        self._store = []

    def add(self, record: dict):
        self._store.append(record)

    def find_by_type(self, t: str):
        return [r for r in self._store if r.get("type") == t]


class FeedbackLoop:
    """
    Records campaign outcomes, updates archetype weights, persists learnings, and emits telemetry
    """

    def __init__(
        self,
        weights_path: str = "assets/optimized/archetype_weights.json",
        memory: Optional[LongTermMemory] = None,
        event_tracker: Optional[EventTracker] = None,
    ):
        self.engine = AdaptiveWeightEngine(path=weights_path)

        self.memory = memory or LongTermMemory()

        self.event_tracker = event_tracker or EventTracker()

    # ----------------------------------------------------------------------------------------------
    # Feedback Processing
    # ----------------------------------------------------------------------------------------------

    def record_results(
        self,
        archetype: Dict[str, float],
        score: float,
        campaign_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        lesson: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a campaign outcome.

        score:
            0.0 - 1.0

        lesson:
            Description of what was learned from the campaign result.add()
        """

        self.engine.update(
            archetypes=archetype,
            score=score,
        )

        learning_record = {
            "type": "feedback",
            "content": lesson or "Campaign feedback recorded",
            "core": score,
            "campaign_id": campaign_id,
            "archetypes": archetype,
            "metadata": metadata or {},
        }

        self.memory.add(learning_record)

        self.event_tracker.track(
            event_type="feedback_recorded",
            trace_id=trace_id,
            campaign_id=campaign_id,
            payload={
                "score": score,
                "archetypes": archetype,
            },
            agent="FeedbackLoop",
        )

        return {
            "updated": True,
            "weights": self.engine.weights,
            "memory_recorded": True,
        }

    # --------------------------------------------------------------------------------
    # Queries
    # --------------------------------------------------------------------------------

    def get_weights(self):
        return self.engine.weights

    def get_learnings(self):
        return self.memory.find_by_type("feedback")
