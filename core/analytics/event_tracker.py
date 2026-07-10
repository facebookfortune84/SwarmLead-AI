from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class EventTracker:
    """
    Lightweight in-memory telemetry system.

    Tracks:
    - agent execution
    - campaign lifecycle
    - feedback processing
    - memory operations
    - system errors
    """

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # Core Tracking
    # ---------------------------------------------------------

    def track(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": payload or {},
            "trace_id": trace_id,
            "campaign_id": campaign_id,
            "agent": agent,
        }

        self._events.append(event)

        return event

    # ---------------------------------------------------------
    # Convenience Helpers
    # ---------------------------------------------------------

    def track_error(
        self,
        error: Exception,
        trace_id: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.track(
            event_type="error",
            payload={
                "message": str(error),
                "error_type": type(error).__name__,
            },
            trace_id=trace_id,
            agent=agent,
        )

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def all(self) -> List[Dict[str, Any]]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()

    def filter(
        self,
        event_type: str,
    ) -> List[Dict[str, Any]]:
        return [event for event in self._events if event["event_type"] == event_type]

    def filter_by_agent(
        self,
        agent: str,
    ) -> List[Dict[str, Any]]:
        return [event for event in self._events if event.get("agent") == agent]

    def filter_by_trace(
        self,
        trace_id: str,
    ) -> List[Dict[str, Any]]:
        return [event for event in self._events if event.get("trace_id") == trace_id]

    def latest(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        return list(self._events[-limit:])

    # ---------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        counts: Dict[str, int] = {}

        for event in self._events:
            event_type = event["event_type"]

            counts[event_type] = counts.get(event_type, 0) + 1

        return {
            "total_events": len(self._events),
            "event_types": counts,
        }
