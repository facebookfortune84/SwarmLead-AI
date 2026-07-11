from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ArchitectureIssue:
    component: str
    message: str
    severity: str


@dataclass
class ArchitectureReport:
    issues: List[ArchitectureIssue] = field(
        default_factory=list
    )


class ArchitectureValidator:
    """
    Validates repository architecture.

    Initial rules:
        - required components exist
        - architecture issue tracking
        - repository health reporting

    Future rules:
        - circular dependency detection
        - layer violation detection
        - service boundary validation
    """

    def validate(
        self,
        available_components: List[str],
        required_components: List[str],
    ) -> ArchitectureReport:

        issues: List[ArchitectureIssue] = []

        for component in required_components:

            if component not in available_components:

                issues.append(
                    ArchitectureIssue(
                        component=component,
                        message=(
                            "Missing required component"
                        ),
                        severity="critical",
                    )
                )

        return ArchitectureReport(
            issues=issues
        )

    def issue_count(
        self,
        report: ArchitectureReport,
    ) -> int:

        return len(report.issues)

    def critical_issues(
        self,
        report: ArchitectureReport,
    ) -> List[ArchitectureIssue]:

        return [
            issue
            for issue in report.issues
            if issue.severity == "critical"
        ]

    def has_issues(
        self,
        report: ArchitectureReport,
    ) -> bool:

        return len(report.issues) > 0

    def healthy(
        self,
        report: ArchitectureReport,
    ) -> bool:

        return len(report.issues) == 0

    def summary(
        self,
        report: ArchitectureReport,
    ) -> Dict:

        return {
            "issues": len(report.issues),
            "critical": len(
                self.critical_issues(report)
            ),
            "healthy": self.healthy(report),
        }

    def clear(
        self,
        report: ArchitectureReport,
    ) -> None:

        report.issues.clear()