from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DebtItem:
    component: str
    description: str
    weight: int


@dataclass
class DebtReport:
    items: List[DebtItem] = field(default_factory=list)


class TechnicalDebtAnalyzer:
    """
    Tracks technical debt and prioritizes
    remediation opportunities.

    Future sources:
        - CoverageAnalyzer
        - FailureAnalyzer
        - ArchitectureValidator
        - RepositoryScanner
    """

    def analyze(
        self,
        items: List[DebtItem],
    ) -> DebtReport:

        return DebtReport(items=list(items))

    def total_weight(
        self,
        report: DebtReport,
    ) -> int:

        return sum(item.weight for item in report.items)

    def highest_priority(
        self,
        report: DebtReport,
    ):

        if not report.items:
            return None

        return max(
            report.items,
            key=lambda x: x.weight,
        )

    def item_count(
        self,
        report: DebtReport,
    ) -> int:

        return len(report.items)

    def debt_score(
        self,
        report: DebtReport,
    ) -> float:

        if not report.items:
            return 0.0

        return self.total_weight(report) / len(report.items)

    def summary(
        self,
        report: DebtReport,
    ) -> Dict:

        highest = self.highest_priority(report)

        return {
            "items": len(report.items),
            "weight": self.total_weight(report),
            "score": self.debt_score(report),
            "highest": (highest.component if highest else None),
        }

    def clear(
        self,
        report: DebtReport,
    ) -> None:

        report.items.clear()
