from core.orchestration.task_backlog import (
    BacklogTask,
    TaskBacklog,
)


def test_add_task():
    backlog = TaskBacklog()

    backlog.add_task(
        "task1",
        1,
    )

    assert len(backlog.all_tasks()) == 1


def test_all_tasks():
    backlog = TaskBacklog()

    backlog.add_task(
        "task1",
        1,
    )

    tasks = backlog.all_tasks()

    assert len(tasks) == 1


def test_next_task():
    backlog = TaskBacklog()

    backlog.add_task(
        "low",
        5,
    )

    backlog.add_task(
        "high",
        1,
    )

    task = backlog.next_task()

    assert task.name == "high"


def test_next_task_none():
    backlog = TaskBacklog()

    assert backlog.next_task() is None


def test_mark_completed():
    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    assert backlog.mark_completed("task") is True

    assert backlog.completed_tasks() == ["task"]


def test_mark_completed_missing():
    backlog = TaskBacklog()

    assert backlog.mark_completed("missing") is False


def test_reset_task():
    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    backlog.mark_completed("task")

    assert backlog.reset_task("task") is True

    assert backlog.pending_tasks() == ["task"]


def test_reset_task_missing():
    backlog = TaskBacklog()

    assert backlog.reset_task("missing") is False


def test_remove_task():
    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    assert backlog.remove_task("task") is True

    assert backlog.all_tasks() == []


def test_remove_task_missing():
    backlog = TaskBacklog()

    assert backlog.remove_task("missing") is False


def test_completed_tasks():
    backlog = TaskBacklog()

    backlog.add_task(
        "a",
        1,
    )

    backlog.add_task(
        "b",
        2,
    )

    backlog.mark_completed("a")

    assert backlog.completed_tasks() == ["a"]


def test_pending_tasks():
    backlog = TaskBacklog()

    backlog.add_task(
        "a",
        1,
    )

    backlog.add_task(
        "b",
        2,
    )

    backlog.mark_completed("a")

    assert backlog.pending_tasks() == ["b"]


def test_summary_empty():
    backlog = TaskBacklog()

    summary = backlog.summary()

    assert summary["total"] == 0
    assert summary["completed"] == 0
    assert summary["pending"] == 0


def test_summary_populated():
    backlog = TaskBacklog()

    backlog.add_task(
        "a",
        1,
    )

    backlog.add_task(
        "b",
        2,
    )

    backlog.mark_completed("a")

    summary = backlog.summary()

    assert summary["total"] == 2
    assert summary["completed"] == 1
    assert summary["pending"] == 1


def test_backlog_task_dataclass():
    task = BacklogTask(
        name="demo",
        priority=1,
    )

    assert task.name == "demo"
    assert task.priority == 1
    assert task.completed is False
