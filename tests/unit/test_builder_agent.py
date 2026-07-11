from core.orchestration.builder_agent import (
    BuilderAgent,
    BuildResult,
)


def test_execute_success():
    agent = BuilderAgent()

    result = agent.execute_task("build_api")

    assert result.success is True
    assert result.task_name == "build_api"


def test_execute_failure():
    agent = BuilderAgent()

    result = agent.execute_task(
        "build_api",
        fail=True,
    )

    assert result.success is False


def test_completed_tracking():
    agent = BuilderAgent()

    agent.execute_task("one")
    agent.execute_task("two")

    assert agent.completed() == [
        "one",
        "two",
    ]


def test_failed_tracking():
    agent = BuilderAgent()

    agent.execute_task(
        "bad",
        fail=True,
    )

    assert agent.failed() == ["bad"]


def test_has_completed_true():
    agent = BuilderAgent()

    agent.execute_task("task")

    assert agent.has_completed("task") is True


def test_has_completed_false():
    agent = BuilderAgent()

    assert agent.has_completed("task") is False


def test_has_failed_true():
    agent = BuilderAgent()

    agent.execute_task(
        "bad",
        fail=True,
    )

    assert agent.has_failed("bad") is True


def test_has_failed_false():
    agent = BuilderAgent()

    assert agent.has_failed("bad") is False


def test_summary_empty():
    agent = BuilderAgent()

    summary = agent.summary()

    assert summary["completed"] == 0
    assert summary["failed"] == 0
    assert summary["success_rate"] == 0.0


def test_summary_partial():
    agent = BuilderAgent()

    agent.execute_task("a")
    agent.execute_task(
        "b",
        fail=True,
    )

    summary = agent.summary()

    assert summary["completed"] == 1
    assert summary["failed"] == 1
    assert summary["success_rate"] == 0.5


def test_reset():
    agent = BuilderAgent()

    agent.execute_task("a")

    agent.execute_task(
        "b",
        fail=True,
    )

    agent.reset()

    assert agent.completed() == []
    assert agent.failed() == []


def test_artifacts_and_metadata():
    agent = BuilderAgent()

    result = agent.execute_task(
        "task",
        artifacts=[
            "file1.py",
            "file2.py",
        ],
        metadata={"branch": "main"},
    )

    assert result.artifacts == [
        "file1.py",
        "file2.py",
    ]

    assert result.metadata["branch"] == "main"


def test_build_result_dataclass():
    result = BuildResult(
        task_name="x",
        success=True,
        artifacts=["a"],
        metadata={"b": 1},
    )

    assert result.task_name == "x"
    assert result.success is True
    assert result.artifacts == ["a"]
    assert result.metadata["b"] == 1
