from dataclasses import dataclass, field
from typing import Dict

from core.orchestration.architecture_validator import (
    ArchitectureReport,
)
from core.orchestration.coverage_analyzer import (
    CoverageAnalyzer,
    CoverageReport,
)
from core.orchestration.failure_analyzer import (
    FailureAnalyzer,
    FailureReport,
)


@dataclass
class SwarmEvaluation:
    score: float
    healthy: bool
    metadata: Dict = field(default_factory=dict)


class SwarmEvaluator:
    """
    Produces a unified repository health score.

    Inputs:
        - coverage
        - architecture health
        - failures

    Future:
        - dependency complexity
        - repository growth
        - backlog analysis
        - technical debt
    """

    def __init__(self):
        self.coverage_analyzer = CoverageAnalyzer()

        self.failure_analyzer = FailureAnalyzer()

    def evaluate(
        self,
        coverage_report: CoverageReport,
        architecture_report: ArchitectureReport,
        failure_report: FailureReport,
    ) -> SwarmEvaluation:

        coverage = self.coverage_analyzer.average_coverage(coverage_report)

        critical_failures = len(self.failure_analyzer.critical(failure_report))

        architecture_penalty = len(architecture_report.issues) * 10

        failure_penalty = critical_failures * 20

        score = max(
            0.0,
            coverage - architecture_penalty - failure_penalty,
        )

        healthy = score >= 80

        return SwarmEvaluation(
            score=score,
            healthy=healthy,
            metadata={
                "coverage": coverage,
                "critical_failures": (critical_failures),
                "architecture_issues": len(architecture_report.issues),
            },
        )

    def summary(
        self,
        evaluation: SwarmEvaluation,
    ) -> Dict:

        return {
            "score": evaluation.score,
            "healthy": evaluation.healthy,
            "metadata": dict(evaluation.metadata),
        }
