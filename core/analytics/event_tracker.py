from datetime import datetime


class EventTracker:
    """
    Lightweight event tracking for
    agents, workflows, campaigns,
    and system learning.
    """

    def __init__(self):
        self._events = []

    def track(
        self,
        event_type: str,
        payload=None,
    ):
        self._events.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "payload": payload or {},
            }
        )

    def all(self):
        return list(self._events)

    def count(self):
        return len(self._events)

    def clear(self):
        self._events.clear()

    def filter(self, event_type):
        return [event for event in self._events if event["event_type"] == event_type]
