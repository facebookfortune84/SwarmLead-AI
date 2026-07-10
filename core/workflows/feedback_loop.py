from typing import Any, Dict, Optional

from core.analytics.event_tracker import EventTracker
from core.memory.long_term_memory.long_term_memory import LongTermMemory
from core.prompts.adaptive_weights import AdaptiveWeightEngine


class FeedbackLoop:
    """
    Records campaign outcomes, updates adaptive weights,
    persists learnings, and emits telemetry.
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

    # ---------------------------------------------------------
    # Feedback Processing
    # ---------------------------------------------------------

    def record_result(
        self,
        archetypes: Dict[str, float],
        score: float,
        campaign_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        lesson: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a completed campaign result.
        """

        self.engine.update(
            archetypes=archetypes,
            score=score,
        )

        learning_record = {
            "type": "feedback",
            "content": lesson or "Campaign feedback recorded",
            "score": score,
            "campaign_id": campaign_id,
            "archetypes": archetypes,
            "metadata": metadata or {},
        }

        self.memory.add(learning_record)

        self.event_tracker.track(
            event_type="feedback_recorded",
            trace_id=trace_id,
            campaign_id=campaign_id,
            payload={
                "score": score,
                "archetypes": archetypes,
            },
            agent="FeedbackLoop",
        )

        return {
            "updated": True,
            "weights": self.engine.weights,
            "memory_recorded": True,
        }

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def get_weights(self):
        return self.engine.weights

    def get_learnings(self):
        """
        Retrieve feedback learnings from any supported
        LongTermMemory implementation.
        """

        # Preferred API
        if hasattr(self.memory, "find_by_type"):
            try:
                return self.memory.find_by_type("feedback")
            except Exception:
                pass

        # Legacy API
        if hasattr(self.memory, "find"):
            try:
                return self.memory.find(
                    "type",
                    "feedback",
                )
            except Exception:
                pass

        # Direct fallback
        if hasattr(self.memory, "all"):
            try:
                return [record for record in self.memory.all() if record.get("type") == "feedback"]
            except Exception:
                pass

        return []
