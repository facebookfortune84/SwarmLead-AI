from core.orchestration.repair_workflow import (
    RepairWorkflow,
    RepairWorkflowResult,
)
from core.orchestration.review_agent import (
    ReviewFinding,
    ReviewResult,
)


def test_review_passes_no_repair_required():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=True,
    )

    result = workflow.execute(
        "file.py",
        review_result,
    )

    assert result.repaired is False
    assert result.repair_result is None


def test_review_failure_triggers_repair():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure",
            )
        ],
    )

    result = workflow.execute(
        "file.py",
        review_result,
    )

    assert result.repaired is True


def test_repair_action_created():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure",
            )
        ],
    )

    result = workflow.execute(
        "file.py",
        review_result,
    )

    assert len(result.repair_result.actions) == 1


def test_execution_history_recorded():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure",
            )
        ],
    )

    workflow.execute(
        "file.py",
        review_result,
    )

    assert workflow.history.count() == 1


def test_skipped_history_recorded():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=True,
    )

    workflow.execute(
        "file.py",
        review_result,
    )

    record = workflow.history.latest()

    assert record.status == "not_required"


def test_repaired_history_recorded():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure",
            )
        ],
    )

    workflow.execute(
        "file.py",
        review_result,
    )

    record = workflow.history.latest()

    assert record.status == "repaired"


def test_event_tracking():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure",
            )
        ],
    )

    workflow.execute(
        "file.py",
        review_result,
    )

    assert workflow.tracker.count() == 2


def test_summary():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure",
            )
        ],
    )

    workflow.execute(
        "file.py",
        review_result,
    )

    summary = workflow.summary()

    assert "history" in summary
    assert "events" in summary


def test_reset():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure",
            )
        ],
    )

    workflow.execute(
        "file.py",
        review_result,
    )

    workflow.reset()

    assert workflow.history.count() == 0
    assert workflow.tracker.count() == 0


def test_multiple_findings():

    workflow = RepairWorkflow()

    review_result = ReviewResult(
        artifact="file.py",
        approved=False,
        findings=[
            ReviewFinding(
                severity="error",
                message="failure_1",
            ),
            ReviewFinding(
                severity="error",
                message="failure_2",
            ),
        ],
    )

    result = workflow.execute(
        "file.py",
        review_result,
    )

    assert len(result.repair_result.actions) == 2


def test_workflow_result_dataclass():

    result = RepairWorkflowResult(
        artifact="demo.py",
        repaired=True,
        repair_result=None,
    )

    assert result.artifact == "demo.py"
    assert result.repaired is True
