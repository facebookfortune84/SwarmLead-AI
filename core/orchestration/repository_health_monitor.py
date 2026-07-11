from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class HealthSnapshot:
    score: float


@dataclass
class HealthReport:
    snapshots: List[HealthSnapshot] = field(default_factory=list)


class RepositoryHealthMonitor:
    """
    Tracks repository health trends over time.

    Future:
        - historical persistence
        - growth metrics
        - health regression alerts
        - trend analysis
    """

    def record(
        self,
        report: HealthReport,
        score: float,
    ) -> HealthSnapshot:

        snapshot = HealthSnapshot(score=score)

        report.snapshots.append(snapshot)

        return snapshot

    def latest(
        self,
        report: HealthReport,
    ) -> Optional[HealthSnapshot]:
        if not report.snapshots:
            return None

        return report.snapshots[-1]

    def average(
        self,
        report: HealthReport,
    ) -> float:

        if not report.snapshots:
            return 0.0

        return sum(x.score for x in report.snapshots) / len(report.snapshots)

    def improving(
        self,
        report: HealthReport,
    ) -> bool:

        if len(report.snapshots) < 2:
            return False

        return report.snapshots[-1].score > report.snapshots[-2].score

    def declining(
        self,
        report: HealthReport,
    ) -> bool:

        if len(report.snapshots) < 2:
            return False

        return report.snapshots[-1].score < report.snapshots[-2].score

    def snapshot_count(
        self,
        report: HealthReport,
    ) -> int:

        return len(report.snapshots)

    def summary(
        self,
        report: HealthReport,
    ) -> Dict:

        latest = self.latest(report)

        return {
            "snapshots": len(report.snapshots),
            "average": self.average(report),
            "latest": (latest.score if latest else None),
            "improving": self.improving(report),
        }

    def clear(
        self,
        report: HealthReport,
    ) -> None:

        report.snapshots.clear()
