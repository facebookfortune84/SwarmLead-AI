import pytest

from core.orchestration.test_generation_task import (
    GeneratedTestSuite,
    UnitTestGenerationTask,
)


def test_execute():

    task = UnitTestGenerationTask()

    result = task.execute(
        "service.py",
        "test_service.py",
    )

    assert isinstance(
        result,
        GeneratedTestSuite,
    )

    assert result.success is True


def test_source_artifact_preserved():

    task = UnitTestGenerationTask()

    result = task.execute(
        "service.py",
        "test_service.py",
    )

    assert result.source_artifact == "service.py"


def test_test_artifact_preserved():

    task = UnitTestGenerationTask()

    result = task.execute(
        "service.py",
        "test_service.py",
    )

    assert result.test_artifact == "test_service.py"


def test_empty_source_artifact():

    task = UnitTestGenerationTask()

    with pytest.raises(ValueError):
        task.execute(
            "",
            "test_service.py",
        )


def test_empty_test_artifact():

    task = UnitTestGenerationTask()

    with pytest.raises(ValueError):
        task.execute(
            "service.py",
            "",
        )


def test_execution_history_recorded():

    task = UnitTestGenerationTask()

    task.execute(
        "service.py",
        "test_service.py",
    )

    assert task.history.count() == 1


def test_history_metadata_stored():

    task = UnitTestGenerationTask()

    task.execute(
        "service.py",
        "test_service.py",
    )

    record = task.history.latest()

    assert record.metadata["source_artifact"] == "service.py"

    assert record.metadata["test_artifact"] == "test_service.py"


def test_events_recorded():

    task = UnitTestGenerationTask()

    task.execute(
        "service.py",
        "test_service.py",
    )

    assert task.tracker.count() == 2


def test_event_types():

    task = UnitTestGenerationTask()

    task.execute(
        "service.py",
        "test_service.py",
    )

    summary = task.tracker.summary()

    assert summary["event_types"]["test_generation_started"] == 1

    assert summary["event_types"]["test_generation_completed"] == 1


def test_summary():

    task = UnitTestGenerationTask()

    task.execute(
        "service.py",
        "test_service.py",
    )

    summary = task.summary()

    assert "history" in summary
    assert "events" in summary


def test_generated_test_suite_dataclass():

    suite = GeneratedTestSuite(
        source_artifact="app.py",
        test_artifact="test_app.py",
        success=True,
    )

    assert suite.source_artifact == "app.py"
    assert suite.test_artifact == "test_app.py"
    assert suite.success is True


def test_multiple_generations():

    task = UnitTestGenerationTask()

    task.execute(
        "a.py",
        "test_a.py",
    )

    task.execute(
        "b.py",
        "test_b.py",
    )

    assert task.history.count() == 2
    assert task.tracker.count() == 4
