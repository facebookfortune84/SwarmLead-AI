"""Tests for the in-process event bus (publish/subscribe)."""

import asyncio
import logging
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core.events.event_bus import (
    EventBus,
    _on_task_failed,
    _on_ticket_resolved,
    _on_workflow_completed,
    _on_workflow_failed,
    event_bus,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def persistence_mocks():
    """Swap DB/notification/ticket modules with mocks so handlers make no IO."""
    mods = {
        "core.persistence.session": mock.MagicMock(),
        "core.persistence.ticket_history": mock.MagicMock(),
        "core.services.notification_service": mock.MagicMock(),
        "core.services.ticket_service": mock.MagicMock(),
    }
    patcher = mock.patch.dict(sys.modules, mods)
    patcher.start()
    try:
        yield {
            "session": mods["core.persistence.session"],
            "ticket_history": mods["core.persistence.ticket_history"],
            "notification_service": mods["core.services.notification_service"],
            "ticket_service": mods["core.services.ticket_service"],
        }
    finally:
        patcher.stop()


def _db(persistence_mocks):
    return persistence_mocks["session"].SessionLocal.return_value


def _ns(persistence_mocks):
    return persistence_mocks["notification_service"].NotificationService.return_value


def _ts(persistence_mocks):
    return persistence_mocks["ticket_service"].TicketService.return_value


# ─────────────────────────────────────────────────────────────────────────────
# subscribe / publish
# ─────────────────────────────────────────────────────────────────────────────


def test_subscribe_registers_handler():
    bus = EventBus()
    handler = lambda payload: None  # noqa: E731

    bus.subscribe("ticket.resolved", handler)

    assert handler in bus._subscribers["ticket.resolved"]


def test_subscribe_same_event_multiple_handlers():
    bus = EventBus()
    first = lambda payload: None  # noqa: E731
    second = lambda payload: None  # noqa: E731

    bus.subscribe("e", first)
    bus.subscribe("e", second)

    assert bus._subscribers["e"] == [first, second]


def test_publish_no_subscribers_is_noop():
    bus = EventBus()

    bus.publish("ghost.event", {"k": 1})


def test_publish_calls_sync_handler():
    bus = EventBus()
    seen = []

    def handler(payload):
        seen.append(payload)

    bus.subscribe("e", handler)
    payload = {"k": 1}

    bus.publish("e", payload)

    assert seen == [payload]


def test_publish_multiple_subscribers_all_called():
    bus = EventBus()
    calls = []

    def first(payload):
        calls.append("first")

    def second(payload):
        calls.append("second")

    bus.subscribe("e", first)
    bus.subscribe("e", second)

    bus.publish("e", {})

    assert calls == ["first", "second"]


def test_publish_events_are_isolated():
    bus = EventBus()
    calls = []

    def handler(payload):
        calls.append(payload)

    bus.subscribe("a", handler)

    bus.publish("b", {"k": 1})
    bus.publish("a", {"k": 2})

    assert calls == [{"k": 2}]


def test_publish_sync_handler_exception_is_logged_and_others_run(caplog):
    caplog.set_level(logging.ERROR, logger="EventBus")
    bus = EventBus()
    calls = []

    def bad_handler(payload):
        raise RuntimeError("sync boom")

    def good_handler(payload):
        calls.append(payload)

    bus.subscribe("e", bad_handler)
    bus.subscribe("e", good_handler)

    bus.publish("e", {"k": 1})

    assert calls == [{"k": 1}]
    assert "Event handler bad_handler raised on event 'e'" in caplog.text


@pytest.mark.asyncio
async def test_publish_async_handler_on_running_loop_schedules_task():
    bus = EventBus()
    calls = []

    async def handler(payload):
        calls.append(payload)

    bus.subscribe("e", handler)

    tasks = []
    real_ensure_future = asyncio.ensure_future

    def capturing_ensure_future(coro):
        task = real_ensure_future(coro)
        tasks.append(task)
        return task

    with mock.patch("core.events.event_bus.asyncio.ensure_future", side_effect=capturing_ensure_future):
        bus.publish("e", {"k": 1})

    assert len(tasks) == 1
    await asyncio.gather(*tasks)
    assert calls == [{"k": 1}]


def test_publish_async_handler_without_running_loop():
    bus = EventBus()
    calls = []

    async def handler(payload):
        calls.append(payload)

    bus.subscribe("e", handler)

    loop = asyncio.new_event_loop()
    with mock.patch("core.events.event_bus.asyncio.get_event_loop", return_value=loop):
        bus.publish("e", {"k": 1})
    loop.close()

    assert calls == [{"k": 1}]


def test_publish_async_handler_exception_without_running_loop(caplog):
    caplog.set_level(logging.ERROR, logger="EventBus")
    bus = EventBus()

    async def bad_handler(payload):
        raise RuntimeError("async boom")

    bus.subscribe("e", bad_handler)

    loop = asyncio.new_event_loop()
    with mock.patch("core.events.event_bus.asyncio.get_event_loop", return_value=loop):
        bus.publish("e", {"k": 1})
    loop.close()

    assert "Event handler bad_handler raised on event 'e'" in caplog.text


def test_publish_async_handler_scheduling_error_is_logged(caplog):
    caplog.set_level(logging.ERROR, logger="EventBus")
    bus = EventBus()

    async def handler(payload):
        pass

    bus.subscribe("e", handler)

    created = []

    def failing_ensure_future(coro):
        created.append(coro)
        raise RuntimeError("schedule boom")

    with mock.patch("core.events.event_bus.asyncio.ensure_future", side_effect=failing_ensure_future):
        bus.publish("e", {"k": 1})

    for coro in created:
        coro.close()

    assert "Event handler handler raised on event 'e'" in caplog.text


@pytest.mark.asyncio
async def test_publish_async_handler_exception_does_not_break_others():
    bus = EventBus()
    calls = []

    async def bad_handler(payload):
        raise RuntimeError("task boom")

    async def good_handler(payload):
        calls.append(payload)

    bus.subscribe("e", bad_handler)
    bus.subscribe("e", good_handler)

    tasks = []
    real_ensure_future = asyncio.ensure_future

    def capturing_ensure_future(coro):
        task = real_ensure_future(coro)
        tasks.append(task)
        return task

    with mock.patch("core.events.event_bus.asyncio.ensure_future", side_effect=capturing_ensure_future):
        bus.publish("e", {"k": 1})

    for task in tasks:
        try:
            await task
        except RuntimeError:
            pass

    assert calls == [{"k": 1}]


def test_singleton_wired_with_builtin_handlers():
    for event in ("ticket.resolved", "task.failed", "workflow.completed", "workflow.failed"):
        assert event in event_bus._subscribers
        assert len(event_bus._subscribers[event]) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# _on_ticket_resolved
# ─────────────────────────────────────────────────────────────────────────────


def test_on_ticket_resolved_notifies_reporter(persistence_mocks):
    ticket = mock.MagicMock()
    ticket.id = 42

    _on_ticket_resolved({"ticket": ticket})

    db = _db(persistence_mocks)
    persistence_mocks["session"].SessionLocal.assert_called_once_with()
    db.close.assert_called_once_with()
    persistence_mocks["notification_service"].NotificationService.assert_called_once_with(db)
    _ns(persistence_mocks).notify_ticket_resolved.assert_called_once_with(ticket)
    persistence_mocks["ticket_history"].record_change.assert_called_once_with(db, 42, "resolved_event_fired")


def test_on_ticket_resolved_without_ticket_returns_early(persistence_mocks):
    _on_ticket_resolved({})

    persistence_mocks["session"].SessionLocal.assert_not_called()


def test_on_ticket_resolved_handler_exception_is_logged(persistence_mocks, caplog):
    caplog.set_level(logging.ERROR, logger="EventBus")
    persistence_mocks["notification_service"].NotificationService.side_effect = RuntimeError("boom")

    _on_ticket_resolved({"ticket": mock.MagicMock()})

    assert "_on_ticket_resolved handler failed" in caplog.text


# ─────────────────────────────────────────────────────────────────────────────
# _on_task_failed
# ─────────────────────────────────────────────────────────────────────────────


def test_on_task_failed_creates_incident_ticket(persistence_mocks):
    _on_task_failed({"task_id": "task-7", "error": "boom detail"})

    db = _db(persistence_mocks)
    persistence_mocks["session"].SessionLocal.assert_called_once_with()
    db.close.assert_called_once_with()
    persistence_mocks["ticket_service"].TicketService.assert_called_once_with(db)
    _ts(persistence_mocks).create_ticket.assert_called_once_with(
        title="Incident: task task-7 failed",
        instruction="boom detail",
        priority="high",
        tags="incident,auto-created",
    )
    _ns(persistence_mocks).notify_task_failed.assert_called_once_with(task_id="task-7", error="boom detail")


def test_on_task_failed_defaults_task_id(persistence_mocks):
    _on_task_failed({"error": "boom"})

    _ts(persistence_mocks).create_ticket.assert_called_once_with(
        title="Incident: task unknown failed",
        instruction="boom",
        priority="high",
        tags="incident,auto-created",
    )


def test_on_task_failed_handler_exception_is_logged(persistence_mocks, caplog):
    caplog.set_level(logging.ERROR, logger="EventBus")
    persistence_mocks["ticket_service"].TicketService.side_effect = RuntimeError("boom")

    _on_task_failed({"task_id": "t1", "error": "e"})

    assert "_on_task_failed handler failed" in caplog.text


# ─────────────────────────────────────────────────────────────────────────────
# _on_workflow_completed
# ─────────────────────────────────────────────────────────────────────────────


def test_on_workflow_completed_broadcasts(persistence_mocks):
    _on_workflow_completed({"workflow_id": "wf-9"})

    db = _db(persistence_mocks)
    persistence_mocks["session"].SessionLocal.assert_called_once_with()
    db.close.assert_called_once_with()
    _ns(persistence_mocks).broadcast_system_event.assert_called_once_with(
        "workflow.completed",
        "Workflow wf-9 completed successfully.",
    )


def test_on_workflow_completed_without_id_returns_early(persistence_mocks):
    _on_workflow_completed({})

    persistence_mocks["session"].SessionLocal.assert_not_called()


def test_on_workflow_completed_handler_exception_is_logged(persistence_mocks, caplog):
    caplog.set_level(logging.ERROR, logger="EventBus")
    persistence_mocks["notification_service"].NotificationService.side_effect = RuntimeError("boom")

    _on_workflow_completed({"workflow_id": "wf-1"})

    assert "_on_workflow_completed handler failed" in caplog.text


# ─────────────────────────────────────────────────────────────────────────────
# _on_workflow_failed
# ─────────────────────────────────────────────────────────────────────────────


def test_on_workflow_failed_broadcasts(persistence_mocks):
    _on_workflow_failed({"workflow_id": "wf-2", "error": "err"})

    db = _db(persistence_mocks)
    persistence_mocks["session"].SessionLocal.assert_called_once_with()
    db.close.assert_called_once_with()
    _ns(persistence_mocks).broadcast_system_event.assert_called_once_with(
        "workflow.failed",
        "Workflow wf-2 failed: err",
    )


def test_on_workflow_failed_defaults_workflow_id(persistence_mocks):
    _on_workflow_failed({"error": "err"})

    _ns(persistence_mocks).broadcast_system_event.assert_called_once_with(
        "workflow.failed",
        "Workflow unknown failed: err",
    )


def test_on_workflow_failed_handler_exception_is_logged(persistence_mocks, caplog):
    caplog.set_level(logging.ERROR, logger="EventBus")
    persistence_mocks["notification_service"].NotificationService.side_effect = RuntimeError("boom")

    _on_workflow_failed({"workflow_id": "wf-3", "error": "err"})

    assert "_on_workflow_failed handler failed" in caplog.text
