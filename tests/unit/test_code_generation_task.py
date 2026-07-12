import pytest

from core.orchestration.code_generation_task import (
    CodeGenerationResult,
    CodeGenerationTask,
)


def test_execute():

    task = CodeGenerationTask()

    result = task.execute(
        "api_layer",
        "api_layer.py",
    )

    assert isinstance(
        result,
        CodeGenerationResult,
    )

    assert result.success is True


def test_task_name_preserved():

    task = CodeGenerationTask()

    result = task.execute(
        "task",
        "file.py",
    )

    assert result.task_name == "task"


def test_artifact_preserved():

    task = CodeGenerationTask()

    result = task.execute(
        "task",
        "file.py",
    )

    assert result.artifact_name == "file.py"


def test_empty_task_name():

    task = CodeGenerationTask()

    with pytest.raises(ValueError):
        task.execute(
            "",
            "file.py",
        )


def test_empty_artifact_name():

    task = CodeGenerationTask()

    with pytest.raises(ValueError):
        task.execute(
            "task",
            "",
        )


def test_execution_record_created():

    task = CodeGenerationTask()

    task.execute(
        "task",
        "file.py",
    )

    assert task.history.count() == 1


def test_event_tracking():

    task = CodeGenerationTask()

    task.execute(
        "task",
        "file.py",
    )

    assert task.tracker.count() == 2


def test_summary():

    task = CodeGenerationTask()

    task.execute(
        "task",
        "file.py",
    )

    summary = task.summary()

    assert "history" in summary
    assert "events" in summary


def test_result_dataclass():

    result = CodeGenerationResult(
        task_name="demo",
        artifact_name="demo.py",
        success=True,
    )

    assert result.task_name == "demo"
    assert result.artifact_name == "demo.py"
    assert result.success is True
