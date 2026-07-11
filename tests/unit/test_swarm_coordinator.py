from core.orchestration.repository_planner import (
    RepositoryPlanner,
)
from core.orchestration.swarm_coordinator import (
    SwarmCoordinator,
    SwarmRunResult,
)


def test_run_next_task():
    coordinator = SwarmCoordinator()

    result = coordinator.run_next_task()

    assert result.build_success is True
    assert result.review_success is True
    assert result.task_name == "api_layer"


def test_run_until_complete():
    planner = RepositoryPlanner()

    coordinator = SwarmCoordinator(planner=planner)

    for _ in range(4):
        coordinator.run_next_task()

    result = coordinator.run_next_task()

    assert result.task_name is None
    assert result.metadata["reason"] == "no_tasks_remaining"


def test_planner_completion():
    planner = RepositoryPlanner()

    coordinator = SwarmCoordinator(planner=planner)

    coordinator.run_next_task()

    assert planner.is_complete("api_layer") is True


def test_review_failure_path():
    coordinator = SwarmCoordinator()

    result = coordinator.run_review_failure("demo")

    assert result.build_success is True
    assert result.review_success is False
    assert result.repaired is True


def test_summary():
    coordinator = SwarmCoordinator()

    coordinator.run_next_task()

    summary = coordinator.summary()

    assert "planner" in summary
    assert "builder" in summary
    assert summary["builder"]["completed"] == 1


def test_summary_empty():
    coordinator = SwarmCoordinator()

    summary = coordinator.summary()

    assert summary["builder"]["completed"] == 0

    assert summary["builder"]["failed"] == 0


def test_swarm_run_result_dataclass():
    result = SwarmRunResult(
        task_name="demo",
        build_success=True,
        review_success=True,
        repaired=False,
    )

    assert result.task_name == "demo"
    assert result.build_success is True
    assert result.review_success is True
    assert result.repaired is False


def test_multiple_task_execution():
    coordinator = SwarmCoordinator()

    first = coordinator.run_next_task()
    second = coordinator.run_next_task()

    assert first.task_name != second.task_name


def test_summary_reflects_progress():
    coordinator = SwarmCoordinator()

    coordinator.run_next_task()
    coordinator.run_next_task()

    summary = coordinator.summary()

    assert summary["planner"]["completed"] == 2


def test_run_review_failure_summary():
    coordinator = SwarmCoordinator()

    coordinator.run_review_failure("sample")

    summary = coordinator.summary()

    assert "builder" in summary
