from core.orchestration.swarm_decision_engine import (
    DecisionResult,
    SwarmDecisionEngine,
)
from core.orchestration.task_backlog import TaskBacklog


def test_decide_no_tasks():

    engine = SwarmDecisionEngine()

    result = engine.decide()

    assert result.selected_task is None
    assert result.reason == "no_tasks_available"


def test_decide_selects_highest_priority():

    backlog = TaskBacklog()

    backlog.add_task(
        "low_priority",
        5,
    )

    backlog.add_task(
        "high_priority",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    result = engine.decide()

    assert result.selected_task.name == "high_priority"


def test_decision_reason():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    result = engine.decide()

    assert result.reason == "highest_priority_pending"


def test_execution_history_recorded():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()

    assert engine.history.count() == 1


def test_selected_status_recorded():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()

    record = engine.history.latest()

    assert record.status == "selected"


def test_priority_metadata_recorded():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        2,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()

    record = engine.history.latest()

    assert record.metadata["priority"] == 2


def test_event_recorded():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()

    assert engine.tracker.count() == 1


def test_no_task_event_recorded():

    engine = SwarmDecisionEngine()

    engine.decide()

    events = engine.tracker.filter("decision_no_task")

    assert len(events) == 1


def test_summary():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()

    summary = engine.summary()

    assert "history" in summary
    assert "events" in summary
    assert "pending_tasks" in summary


def test_reset():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()

    engine.reset()

    assert engine.history.count() == 0
    assert engine.tracker.count() == 0


def test_decision_result_dataclass():

    result = DecisionResult(
        selected_task=None,
        reason="none",
    )

    assert result.reason == "none"
    assert result.selected_task is None


def test_multiple_decisions():

    backlog = TaskBacklog()

    backlog.add_task(
        "a",
        1,
    )

    backlog.add_task(
        "b",
        2,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()
    engine.decide()

    assert engine.history.count() == 2


def test_event_type_created():

    backlog = TaskBacklog()

    backlog.add_task(
        "task",
        1,
    )

    engine = SwarmDecisionEngine(
        backlog=backlog,
    )

    engine.decide()

    event_summary = engine.tracker.summary()

    assert event_summary["event_types"]["task_selected"] == 1
