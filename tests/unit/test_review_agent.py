from core.orchestration.review_agent import (
    ReviewAgent,
    ReviewFinding,
    ReviewResult,
)


def test_review_no_findings():
    agent = ReviewAgent()

    result = agent.review_artifact(
        "file.py",
    )

    assert result.approved is True


def test_review_with_findings():
    agent = ReviewAgent()

    result = agent.review_artifact(
        "file.py",
        findings=[
            ReviewFinding(
                severity="warning",
                message="test",
            )
        ],
    )

    assert result.approved is False


def test_has_errors_true():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="bad",
            )
        ],
    )

    assert agent.has_errors(result) is True


def test_has_errors_false():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=True,
    )

    assert agent.has_errors(result) is False


def test_has_warnings_true():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=False,
        findings=[
            ReviewFinding(
                severity="warning",
                message="warn",
            )
        ],
    )

    assert agent.has_warnings(result) is True


def test_has_warnings_false():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=True,
    )

    assert agent.has_warnings(result) is False


def test_score_errors():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="bad",
            )
        ],
    )

    assert agent.score(result) == 0.0


def test_score_perfect():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=True,
    )

    assert agent.score(result) == 1.0


def test_score_single_warning():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=False,
        findings=[
            ReviewFinding(
                severity="warning",
                message="warn",
            )
        ],
    )

    assert agent.score(result) == 0.75


def test_score_multiple_warnings():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="x",
        approved=False,
        findings=[
            ReviewFinding(
                severity="warning",
                message="1",
            ),
            ReviewFinding(
                severity="warning",
                message="2",
            ),
        ],
    )

    assert agent.score(result) == 0.5


def test_summary():
    agent = ReviewAgent()

    result = ReviewResult(
        artifact="file.py",
        approved=True,
    )

    summary = agent.summary(result)

    assert summary["artifact"] == "file.py"
    assert summary["approved"] is True
    assert summary["finding_count"] == 0
    assert summary["score"] == 1.0


def test_review_finding_dataclass():
    finding = ReviewFinding(
        severity="warning",
        message="sample",
    )

    assert finding.severity == "warning"
    assert finding.message == "sample"


def test_review_result_dataclass():
    result = ReviewResult(
        artifact="artifact.py",
        approved=True,
    )

    assert result.artifact == "artifact.py"
    assert result.approved is True
    assert result.findings == []
