"""
Pure unit tests for WorkflowService — full state-machine coverage.

Uses an in-memory/tmp sqlite engine created per test, with
core.persistence.session.SessionLocal monkeypatched to the test session
(the same pattern as test_voice_agent_service.py). The Celery task and the
event bus are replaced with recording fakes so no network/broker is touched.
"""

import json

import pytest

from core.models.workflow_step import WorkflowStep
from core.services.workflow_service import WorkflowService


class RecordingBus:
    def __init__(self):
        self.events = []
        self.fail = False

    def publish(self, event, payload=None):
        if self.fail:
            raise RuntimeError("event bus down")
        self.events.append((event, payload))


class RecordingTask:
    def __init__(self):
        self.calls = []
        self.fail = False

    def apply_async(self, args=None, **kwargs):
        if self.fail:
            raise RuntimeError("broker down")
        self.calls.append((args, kwargs))
        return None


@pytest.fixture
def harness(tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401  (register all models on Base.metadata)
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'workflows.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)

    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    bus = RecordingBus()
    task = RecordingTask()
    monkeypatch.setattr("core.events.event_bus.event_bus", bus)
    monkeypatch.setattr(
        "infrastructure.celery.workflow_tasks.execute_workflow_step", task
    )

    db = test_session()
    svc = WorkflowService(db)
    yield svc, db, bus, task
    db.close()


def _create(svc, steps, name="Test Workflow", company_id=None):
    return svc.create_workflow(name=name, steps=steps, company_id=company_id)


def _steps(session, workflow_id):
    return (
        session.query(WorkflowStep)
        .filter(WorkflowStep.workflow_id == workflow_id)
        .order_by(WorkflowStep.id)
        .all()
    )


# --------------------------------------------------------------------- #
# create_workflow
# --------------------------------------------------------------------- #


def test_create_workflow_with_steps(harness):
    svc, session, bus, task = harness
    wf = _create(
        svc,
        [
            {"step_name": "Step 1", "step_type": "ticket", "input": {"title": "T1"}},
            {"step_name": "Step 2", "step_type": "notification", "input": {}},
        ],
        name="Create Test",
        company_id="acme",
    )

    assert wf.id
    assert wf.name == "Create Test"
    assert wf.company_id == "acme"
    assert wf.status == "pending"
    assert wf.current_step == 0
    assert json.loads(wf.steps_json) == [
        {"step_name": "Step 1", "step_type": "ticket", "input": {"title": "T1"}},
        {"step_name": "Step 2", "step_type": "notification", "input": {}},
    ]

    rows = _steps(session, wf.id)
    by_name = {r.step_name: r for r in rows}
    assert len(rows) == 2
    assert by_name["Step 1"].workflow_id == wf.id
    assert by_name["Step 1"].step_type == "ticket"
    assert json.loads(by_name["Step 1"].input_json) == {"title": "T1"}
    assert by_name["Step 1"].status == "pending"
    assert by_name["Step 2"].step_type == "notification"

    assert task.calls == []
    assert bus.events == []


def test_create_workflow_defaults_when_keys_missing(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{}])

    rows = _steps(session, wf.id)
    assert len(rows) == 1
    assert rows[0].step_name == "unnamed"
    assert rows[0].step_type == "ticket"
    assert rows[0].input_json == "{}"


def test_create_workflow_empty_steps(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [])

    assert wf.status == "pending"
    assert json.loads(wf.steps_json) == []
    assert _steps(session, wf.id) == []


def test_create_workflow_without_company_id(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "S", "step_type": "ticket"}])
    assert wf.company_id is None


# --------------------------------------------------------------------- #
# start_workflow
# --------------------------------------------------------------------- #


def test_start_workflow_not_found_returns_none(harness):
    svc, session, bus, task = harness
    assert svc.start_workflow("missing-id") is None


def test_start_workflow_transitions_to_running_and_enqueues_first_step(harness):
    svc, session, bus, task = harness
    wf = _create(
        svc,
        [
            {"step_name": "Step 1", "step_type": "ticket"},
            {"step_name": "Step 2", "step_type": "ticket"},
        ],
    )

    started = svc.start_workflow(wf.id)

    assert started.status == "running"
    assert started.current_step == 0
    assert started.updated_at is not None

    step0 = _steps(session, wf.id)[0]
    assert step0.status == "running"
    assert step0.started_at is not None
    assert step0.completed_at is None

    assert len(task.calls) == 1
    assert task.calls[0][0] == [wf.id, step0.id]
    assert task.calls[0][1] == {"queue": "default"}


def test_start_workflow_idempotent_when_already_running(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    first = svc.start_workflow(wf.id)
    second = svc.start_workflow(wf.id)

    assert second is first
    assert second.status == "running"
    assert len(task.calls) == 1


def test_start_workflow_empty_steps(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [])

    started = svc.start_workflow(wf.id)

    assert started.status == "running"
    assert started.current_step == 0
    assert task.calls == []


def test_start_workflow_enqueue_failure_is_swallowed(harness):
    svc, session, bus, task = harness
    task.fail = True
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    started = svc.start_workflow(wf.id)

    assert started.status == "running"
    assert _steps(session, wf.id)[0].status == "running"


# --------------------------------------------------------------------- #
# advance_workflow
# --------------------------------------------------------------------- #


def test_advance_workflow_not_found_returns_none(harness):
    svc, session, bus, task = harness
    assert svc.advance_workflow("missing-id") is None


def test_advance_workflow_noop_when_not_running(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    result = svc.advance_workflow(wf.id)

    assert result is wf
    assert wf.status == "pending"
    assert task.calls == []
    assert bus.events == []


def test_advance_workflow_moves_to_next_step(harness):
    svc, session, bus, task = harness
    wf = _create(
        svc,
        [
            {"step_name": "Step 1", "step_type": "ticket"},
            {"step_name": "Step 2", "step_type": "ticket"},
        ],
    )
    svc.start_workflow(wf.id)
    task.calls.clear()

    advanced = svc.advance_workflow(wf.id)

    assert advanced.status == "running"
    assert advanced.current_step == 1

    rows = _steps(session, wf.id)
    assert rows[0].status == "completed"
    assert rows[0].completed_at is not None
    assert rows[1].status == "running"
    assert rows[1].started_at is not None

    assert len(task.calls) == 1
    assert task.calls[0][0] == [wf.id, rows[1].id]
    assert bus.events == []


def test_advance_workflow_completes_on_last_step_and_publishes_event(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)
    task.calls.clear()

    advanced = svc.advance_workflow(wf.id)

    assert advanced.status == "completed"
    assert advanced.completed_at is not None
    assert advanced.current_step == 0

    step = _steps(session, wf.id)[0]
    assert step.status == "completed"
    assert step.completed_at is not None

    assert bus.events == [("workflow.completed", {"workflow_id": wf.id})]
    assert task.calls == []


def test_advance_workflow_multistep_runs_to_completion(harness):
    svc, session, bus, task = harness
    wf = _create(
        svc,
        [
            {"step_name": "Step 1", "step_type": "ticket"},
            {"step_name": "Step 2", "step_type": "ticket"},
        ],
    )
    svc.start_workflow(wf.id)
    svc.advance_workflow(wf.id)

    done = svc.advance_workflow(wf.id)

    assert done.status == "completed"
    assert done.completed_at is not None
    rows = _steps(session, wf.id)
    assert all(r.status == "completed" for r in rows)
    assert bus.events == [("workflow.completed", {"workflow_id": wf.id})]


def test_advance_workflow_empty_steps_completes(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [])
    svc.start_workflow(wf.id)

    advanced = svc.advance_workflow(wf.id)

    assert advanced.status == "completed"
    assert advanced.completed_at is not None
    assert bus.events == [("workflow.completed", {"workflow_id": wf.id})]


def test_advance_workflow_event_publish_failure_swallowed(harness):
    svc, session, bus, task = harness
    bus.fail = True
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)

    advanced = svc.advance_workflow(wf.id)

    assert advanced.status == "completed"
    assert advanced.completed_at is not None


# --------------------------------------------------------------------- #
# pause_workflow
# --------------------------------------------------------------------- #


def test_pause_workflow_running(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)

    paused = svc.pause_workflow(wf.id)

    assert paused.status == "paused"
    assert paused.updated_at is not None


def test_pause_workflow_not_found_returns_none(harness):
    svc, session, bus, task = harness
    assert svc.pause_workflow("missing-id") is None


def test_pause_workflow_noop_when_not_running(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    paused = svc.pause_workflow(wf.id)

    assert paused is wf
    assert wf.status == "pending"


# --------------------------------------------------------------------- #
# resume_workflow
# --------------------------------------------------------------------- #


def test_resume_workflow_restarts_paused(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)
    svc.pause_workflow(wf.id)
    task.calls.clear()

    resumed = svc.resume_workflow(wf.id)

    assert resumed.status == "running"
    assert len(task.calls) == 1
    step = _steps(session, wf.id)[0]
    assert task.calls[0][0] == [wf.id, step.id]


def test_resume_workflow_not_found_returns_none(harness):
    svc, session, bus, task = harness
    assert svc.resume_workflow("missing-id") is None


def test_resume_workflow_noop_when_not_paused(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    resumed = svc.resume_workflow(wf.id)

    assert resumed is wf
    assert wf.status == "pending"
    assert task.calls == []


# --------------------------------------------------------------------- #
# cancel_workflow
# --------------------------------------------------------------------- #


def test_cancel_workflow_marks_failed_with_user(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)

    cancelled = svc.cancel_workflow(wf.id, user_id="alice")

    assert cancelled.status == "failed"
    assert cancelled.error_message == "Cancelled by user alice"
    assert cancelled.updated_at is not None


def test_cancel_workflow_without_user(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)

    cancelled = svc.cancel_workflow(wf.id)

    assert cancelled.status == "failed"
    assert cancelled.error_message == "Cancelled by user None"


def test_cancel_workflow_not_found_returns_none(harness):
    svc, session, bus, task = harness
    assert svc.cancel_workflow("missing-id") is None


def test_cancel_workflow_completed_noop(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)
    svc.advance_workflow(wf.id)

    cancelled = svc.cancel_workflow(wf.id)

    assert cancelled.status == "completed"
    assert cancelled.error_message is None


# --------------------------------------------------------------------- #
# handle_failure
# --------------------------------------------------------------------- #


def test_handle_failure_not_found_returns_none(harness):
    svc, session, bus, task = harness
    assert svc.handle_failure("missing-id", "missing-step", "boom") is None


def test_handle_failure_marks_workflow_and_step_failed(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    step = _steps(session, wf.id)[0]

    result = svc.handle_failure(wf.id, step.id, "boom")

    assert result.status == "failed"
    assert result.error_message == "boom"

    failed_step = _steps(session, wf.id)[0]
    assert failed_step.status == "failed"
    assert failed_step.error_message == "boom"
    assert failed_step.retry_count == 1

    assert bus.events == [("workflow.failed", {"workflow_id": wf.id, "error": "boom"})]


def test_handle_failure_increments_existing_retry_count(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    step = _steps(session, wf.id)[0]
    step.retry_count = 2
    session.commit()

    svc.handle_failure(wf.id, step.id, "again")

    assert _steps(session, wf.id)[0].retry_count == 3


def test_handle_failure_step_not_found_marks_workflow_only(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    result = svc.handle_failure(wf.id, "missing-step", "err")

    assert result.status == "failed"
    assert result.error_message == "err"
    step = _steps(session, wf.id)[0]
    assert step.status == "pending"
    assert step.retry_count == 0


def test_handle_failure_event_publish_failure_swallowed(harness):
    svc, session, bus, task = harness
    bus.fail = True
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    result = svc.handle_failure(wf.id, "missing-step", "err")

    assert result.status == "failed"
    assert result.error_message == "err"


# --------------------------------------------------------------------- #
# get_status
# --------------------------------------------------------------------- #


def test_get_status_unknown_id_returns_none(harness):
    svc, session, bus, task = harness
    assert svc.get_status("missing-id") is None


def test_get_status_returns_workflow_details(harness):
    svc, session, bus, task = harness
    wf = _create(
        svc,
        [
            {"step_name": "Step 1", "step_type": "ticket", "input": {"title": "T1"}},
            {"step_name": "Step 2", "step_type": "notification"},
        ],
    )
    svc.start_workflow(wf.id)

    info = svc.get_status(wf.id)

    assert info["id"] == wf.id
    assert info["name"] == "Test Workflow"
    assert info["status"] == "running"
    assert info["current_step"] == 0
    assert info["total_steps"] == 2
    assert info["error_message"] is None
    assert info["created_at"] is not None
    assert info["updated_at"] is not None
    assert info["completed_at"] is None

    assert len(info["steps"]) == 2
    by_name = {s["step_name"]: s for s in info["steps"]}
    assert by_name["Step 1"]["step_type"] == "ticket"
    assert by_name["Step 2"]["step_type"] == "notification"

    statuses = sorted(s["status"] for s in info["steps"])
    assert statuses == ["pending", "running"]
    running = next(s for s in info["steps"] if s["status"] == "running")
    pending = next(s for s in info["steps"] if s["status"] == "pending")
    assert running["retry_count"] == 0
    assert running["error_message"] is None
    assert running["started_at"] is not None
    assert running["completed_at"] is None
    assert pending["started_at"] is None


def test_get_status_empty_steps(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [])

    info = svc.get_status(wf.id)

    assert info["status"] == "pending"
    assert info["total_steps"] == 0
    assert info["steps"] == []


def test_get_status_completed_workflow_timestamps(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])
    svc.start_workflow(wf.id)
    svc.advance_workflow(wf.id)

    info = svc.get_status(wf.id)

    assert info["status"] == "completed"
    assert info["completed_at"] is not None
    assert info["steps"][0]["status"] == "completed"
    assert info["steps"][0]["completed_at"] is not None
    assert info["steps"][0]["started_at"] is not None


# --------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------- #


def test_get_returns_workflow_or_none(harness):
    svc, session, bus, task = harness
    wf = _create(svc, [{"step_name": "Step 1", "step_type": "ticket"}])

    assert svc._get(wf.id) is wf
    assert svc._get("missing-id") is None


def test_get_steps_returns_ordered_steps(harness):
    svc, session, bus, task = harness
    wf = _create(
        svc,
        [
            {"step_name": "S1", "step_type": "ticket"},
            {"step_name": "S2", "step_type": "ticket"},
            {"step_name": "S3", "step_type": "ticket"},
        ],
    )

    rows = svc._get_steps(wf.id)

    assert len(rows) == 3
    assert [r.id for r in rows] == sorted(r.id for r in rows)
    assert svc._get_steps("missing-id") == []
