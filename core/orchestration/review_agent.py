from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReviewFinding:
    severity: str
    message: str


@dataclass
class ReviewResult:
    artifact: str
    approved: bool
    findings: List[ReviewFinding] = field(default_factory=list)


class ReviewAgent:
    """
    Performs lightweight repository reviews.

    Future expansion:
    - Static analysis
    - Security rules
    - Architecture validation
    - LLM code review
    """

    def review_artifact(
        self,
        artifact: str,
        findings: Optional[List[ReviewFinding]] = None,
    ) -> ReviewResult:

        findings = findings or []

        return ReviewResult(
            artifact=artifact,
            approved=len(findings) == 0,
            findings=findings,
        )

    def has_errors(
        self,
        result: ReviewResult,
    ) -> bool:
        return any(finding.severity == "error" for finding in result.findings)

    def has_warnings(
        self,
        result: ReviewResult,
    ) -> bool:
        return any(finding.severity == "warning" for finding in result.findings)

    def score(
        self,
        result: ReviewResult,
    ) -> float:
        if self.has_errors(result):
            return 0.0

        warnings = sum(1 for f in result.findings if f.severity == "warning")

        if warnings == 0:
            return 1.0

        return max(
            0.0,
            1.0 - (warnings * 0.25),
        )

    def summary(
        self,
        result: ReviewResult,
    ) -> Dict:
        return {
            "artifact": result.artifact,
            "approved": result.approved,
            "finding_count": len(result.findings),
            "score": self.score(result),
        }
