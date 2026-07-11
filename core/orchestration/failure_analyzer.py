from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FailureRecord:
    component: str
    message: str
    severity: str


@dataclass
class FailureReport:
    failures: List[FailureRecord] = field(default_factory=list)


class FailureAnalyzer:
    """
    Analyzes build, review, execution,
    and orchestration failures.
    """

    def analyze(
        self,
        failures: List[FailureRecord],
    ) -> FailureReport:

        return FailureReport(failures=list(failures))

    def count(
        self,
        report: FailureReport,
    ) -> int:

        return len(report.failures)

    def critical(
        self,
        report: FailureReport,
    ) -> List[FailureRecord]:

        return [failure for failure in report.failures if failure.severity == "critical"]

    def warnings(
        self,
        report: FailureReport,
    ) -> List[FailureRecord]:

        return [failure for failure in report.failures if failure.severity == "warning"]

    def has_failures(
        self,
        report: FailureReport,
    ) -> bool:

        return len(report.failures) > 0

    def summary(
        self,
        report: FailureReport,
    ) -> Dict:

        return {
            "failures": len(report.failures),
            "critical": len(self.critical(report)),
            "warnings": len(self.warnings(report)),
        }

    def clear(
        self,
        report: FailureReport,
    ) -> None:

        report.failures.clear()
