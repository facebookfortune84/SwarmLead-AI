from core.orchestration.execution_history import (
    ExecutionHistory,
    ExecutionRecord,
)


def test_record():
    history = ExecutionHistory()

    record = history.record(
        "task1",
        "success",
    )

    assert record.task_name == "task1"
    assert record.status == "success"


def test_record_metadata():
    history = ExecutionHistory()

    record = history.record(
        "task1",
        "success",
        metadata={
            "branch": "main",
        },
    )

    assert record.metadata["branch"] == "main"


def test_all():
    history = ExecutionHistory()

    history.record(
        "task1",
        "success",
    )

    records = history.all()

    assert len(records) == 1


def test_successful():
    history = ExecutionHistory()

    history.record(
        "good",
        "success",
    )

    history.record(
        "bad",
        "failed",
    )

    successes = history.successful()

    assert len(successes) == 1
    assert successes[0].task_name == "good"


def test_failed():
    history = ExecutionHistory()

    history.record(
        "good",
        "success",
    )

    history.record(
        "bad",
        "failed",
    )

    failures = history.failed()

    assert len(failures) == 1
    assert failures[0].task_name == "bad"


def test_latest_none():
    history = ExecutionHistory()

    assert history.latest() is None


def test_latest():
    history = ExecutionHistory()

    history.record(
        "one",
        "success",
    )

    history.record(
        "two",
        "failed",
    )

    latest = history.latest()

    assert latest.task_name == "two"


def test_count():
    history = ExecutionHistory()

    history.record(
        "one",
        "success",
    )

    history.record(
        "two",
        "success",
    )

    assert history.count() == 2


def test_summary_empty():
    history = ExecutionHistory()

    summary = history.summary()

    assert summary["total"] == 0
    assert summary["successful"] == 0
    assert summary["failed"] == 0


def test_summary_populated():
    history = ExecutionHistory()

    history.record(
        "good",
        "success",
    )

    history.record(
        "bad",
        "failed",
    )

    summary = history.summary()

    assert summary["total"] == 2
    assert summary["successful"] == 1
    assert summary["failed"] == 1


def test_clear():
    history = ExecutionHistory()

    history.record(
        "task",
        "success",
    )

    history.clear()

    assert history.count() == 0
    assert history.all() == []


def test_execution_record_dataclass():
    record = ExecutionRecord(
        task_name="demo",
        status="success",
        metadata={"version": 1},
    )

    assert record.task_name == "demo"
    assert record.status == "success"
    assert record.metadata["version"] == 1
