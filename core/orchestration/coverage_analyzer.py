from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CoverageTarget:
    name: str
    coverage: float


@dataclass
class CoverageReport:
    targets: List[CoverageTarget] = field(default_factory=list)


class CoverageAnalyzer:
    """
    Analyzes repository test coverage.

    Future integrations:
        - pytest-cov XML
        - Coverage JSON
        - repository scanner
        - improvement planner
    """

    def analyze(
        self,
        targets: List[CoverageTarget],
    ) -> CoverageReport:

        return CoverageReport(targets=list(targets))

    def average_coverage(
        self,
        report: CoverageReport,
    ) -> float:

        if not report.targets:
            return 0.0

        total = sum(t.coverage for t in report.targets)

        return total / len(report.targets)

    def low_coverage(
        self,
        report: CoverageReport,
        threshold: float = 80.0,
    ) -> List[CoverageTarget]:
        return [target for target in report.targets if target.coverage < threshold]

    def fully_covered(
        self,
        report: CoverageReport,
    ) -> List[CoverageTarget]:
        return [target for target in report.targets if target.coverage >= 100.0]

    def highest_coverage(
        self,
        report: CoverageReport,
    ):

        if not report.targets:
            return None

        return max(
            report.targets,
            key=lambda t: t.coverage,
        )

    def summary(
        self,
        report: CoverageReport,
    ) -> Dict:

        highest = self.highest_coverage(report)

        return {
            "targets": len(report.targets),
            "average": self.average_coverage(report),
            "low_coverage": len(self.low_coverage(report)),
            "highest": (highest.coverage if highest else None),
        }

    def clear(
        self,
        report: CoverageReport,
    ) -> None:

        report.targets.clear()
