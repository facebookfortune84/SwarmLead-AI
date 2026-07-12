from dataclasses import dataclass, field
from typing import Dict, Optional

from core.analytics.event_tracker import EventTracker
from core.orchestration.execution_history import ExecutionHistory
from core.orchestration.repository_health_monitor import (
    HealthReport,
    RepositoryHealthMonitor,
)


@dataclass
class HealthServiceResult:
    score: float
    healthy: bool
    metadata: Dict = field(default_factory=dict)


class RepositoryHealthService:
    """
    Service layer around RepositoryHealthMonitor.

    Provides health aggregation and telemetry.
    """

    def __init__(
        self,
        monitor: Optional[RepositoryHealthMonitor] = None,
        history: Optional[ExecutionHistory] = None,
        tracker: Optional[EventTracker] = None,
    ) -> None:

        self.monitor = monitor or RepositoryHealthMonitor()
        self.history = history or ExecutionHistory()
        self.tracker = tracker or EventTracker()
        self.last_report: Optional[HealthReport] = None

    def collect_health(
        self,
        score: float,
    ) -> HealthServiceResult:

        if self.last_report is None:
            self.last_report = HealthReport([])

        snapshot = self.monitor.record(
            self.last_report,
            score,
        )

        self.history.record(
            "repository_health",
            "success",
            metadata={"score": score},
        )

        self.tracker.track(
            event_type="health_collected",
            payload={"score": score},
            agent="RepositoryHealthService",
        )

        return HealthServiceResult(
            score=snapshot.score,
            healthy=snapshot.score >= 80,
        )

    def average_health(self) -> float:

        if self.last_report is None:
            return 0.0

        return self.monitor.average(self.last_report)

    def health_trending_up(self) -> bool:

        if self.last_report is None:
            return False

        return self.monitor.improving(self.last_report)

    def health_trending_down(self) -> bool:

        if self.last_report is None:
            return False

        return self.monitor.declining(self.last_report)

    def summary(self) -> Dict:

        report = self.last_report or HealthReport([])

        return {
            "monitor": self.monitor.summary(report),
            "history": self.history.summary(),
            "events": self.tracker.summary(),
        }

    def reset(self) -> None:

        report = self.last_report or HealthReport([])
        self.monitor.clear(report)
        self.history.clear()
        self.tracker.clear()

    def latest_health(self):

        if self.last_report is None:
            return None

        return self.monitor.latest(self.last_report)
