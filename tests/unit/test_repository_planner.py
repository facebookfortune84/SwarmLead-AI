from core.orchestration.repository_planner import (
    BuildTask,
    RepositoryPlanner,
)


def test_all_tasks():
    planner = RepositoryPlanner()

    tasks = planner.all_tasks()

    assert len(tasks) == 4


def test_completed_starts_empty():
    planner = RepositoryPlanner()

    assert planner.completed_tasks() == []


def test_mark_complete():
    planner = RepositoryPlanner()

    planner.mark_complete("api_layer")

    assert planner.is_complete("api_layer") is True


def test_is_complete_false():
    planner = RepositoryPlanner()

    assert planner.is_complete("missing") is False


def test_pending_tasks():
    planner = RepositoryPlanner()

    planner.mark_complete("api_layer")

    pending = planner.pending_tasks()

    assert len(pending) == 3


def test_next_task_first_priority():
    planner = RepositoryPlanner()

    task = planner.next_task()

    assert task.name == "api_layer"


def test_next_task_after_completion():
    planner = RepositoryPlanner()

    planner.mark_complete("api_layer")

    task = planner.next_task()

    assert task.name == "builder_agent"


def test_next_task_none_when_complete():
    planner = RepositoryPlanner()

    for task in planner.all_tasks():
        planner.mark_complete(task.name)

    assert planner.next_task() is None


def test_summary_empty():
    planner = RepositoryPlanner()

    summary = planner.summary()

    assert summary["total"] == 4
    assert summary["completed"] == 0
    assert summary["remaining"] == 4


def test_summary_partial():
    planner = RepositoryPlanner()

    planner.mark_complete("api_layer")

    planner.mark_complete("builder_agent")

    summary = planner.summary()

    assert summary["completed"] == 2
    assert summary["remaining"] == 2


def test_completed_constructor():
    planner = RepositoryPlanner(completed=["api_layer"])

    assert planner.is_complete("api_layer")


def test_build_task_dataclass():
    task = BuildTask(
        name="x",
        priority=1,
        category="test",
        description="demo",
    )

    assert task.name == "x"
    assert task.priority == 1
    assert task.category == "test"
    assert task.description == "demo"
