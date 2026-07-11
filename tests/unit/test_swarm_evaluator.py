from core.orchestration.architecture_validator import (
    ArchitectureIssue,
    ArchitectureReport,
)
from core.orchestration.coverage_analyzer import (
    CoverageReport,
    CoverageTarget,
)
from core.orchestration.failure_analyzer import (
    FailureRecord,
    FailureReport,
)
from core.orchestration.swarm_evaluator import (  # type: ignore[import]
    SwarmEvaluation,
    SwarmEvaluator,
)


def test_evaluate_no_penalties():
    evaluator = SwarmEvaluator()

    result = evaluator.evaluate(
        CoverageReport(
            targets=[
                CoverageTarget(
                    name="x",
                    coverage=100.0,
                )
            ]
        ),
        ArchitectureReport(),
        FailureReport(),
    )

    assert result.healthy is True
    assert result.score == 100.0


def test_evaluate_architecture_penalty():
    evaluator = SwarmEvaluator()

    result = evaluator.evaluate(
        CoverageReport(
            targets=[
                CoverageTarget(
                    name="x",
                    coverage=100.0,
                )
            ]
        ),
        ArchitectureReport(
            issues=[
                ArchitectureIssue(
                    component="db",
                    message="missing",
                    severity="critical",
                )
            ]
        ),
        FailureReport(),
    )

    assert result.score == 90.0


def test_evaluate_failure_penalty():
    evaluator = SwarmEvaluator()

    result = evaluator.evaluate(
        CoverageReport(
            targets=[
                CoverageTarget(
                    name="x",
                    coverage=100.0,
                )
            ]
        ),
        ArchitectureReport(),
        FailureReport(
            failures=[
                FailureRecord(
                    component="builder",
                    message="failed",
                    severity="critical",
                )
            ]
        ),
    )

    assert result.score == 80.0


def test_unhealthy_result():
    evaluator = SwarmEvaluator()

    result = evaluator.evaluate(
        CoverageReport(
            targets=[
                CoverageTarget(
                    name="x",
                    coverage=50.0,
                )
            ]
        ),
        ArchitectureReport(
            issues=[
                ArchitectureIssue(
                    component="api",
                    message="missing",
                    severity="critical",
                )
            ]
        ),
        FailureReport(
            failures=[
                FailureRecord(
                    component="builder",
                    message="boom",
                    severity="critical",
                )
            ]
        ),
    )

    assert result.healthy is False


def test_score_never_negative():
    evaluator = SwarmEvaluator()

    result = evaluator.evaluate(
        CoverageReport(),
        ArchitectureReport(
            issues=[
                ArchitectureIssue(
                    component="x",
                    message="bad",
                    severity="critical",
                )
            ]
            * 20
        ),
        FailureReport(
            failures=[
                FailureRecord(
                    component="y",
                    message="bad",
                    severity="critical",
                )
            ]
            * 20
        ),
    )

    assert result.score == 0.0


def test_summary():
    evaluator = SwarmEvaluator()

    evaluation = SwarmEvaluation(
        score=90.0,
        healthy=True,
        metadata={"coverage": 100.0},
    )

    summary = evaluator.summary(evaluation)

    assert summary["score"] == 90.0
    assert summary["healthy"] is True


def test_metadata_population():
    evaluator = SwarmEvaluator()

    result = evaluator.evaluate(
        CoverageReport(
            targets=[
                CoverageTarget(
                    name="module",
                    coverage=95.0,
                )
            ]
        ),
        ArchitectureReport(),
        FailureReport(),
    )

    assert result.metadata["coverage"] == 95.0


def test_swarm_evaluation_dataclass():
    value = SwarmEvaluation(
        score=100.0,
        healthy=True,
    )

    assert value.score == 100.0
    assert value.healthy is True
    assert value.metadata == {}
