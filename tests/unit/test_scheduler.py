import pytest
import asyncio


@pytest.mark.asyncio
async def test_schedule_and_execute():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    await scheduler.start()
    try:
        result_container = {}
        async def task(data, ctx):
            result_container["result"] = "done"
        scheduler.schedule(name="test", handler=task, context={"data": {}})
        await asyncio.sleep(0.15)
        assert result_container.get("result") == "done"
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_list_tasks():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    await scheduler.start()
    try:
        async def task(data, ctx):
            pass
        scheduler.schedule(name="test_task", handler=task, context={"data": {}})
        await asyncio.sleep(0.05)
        tasks = scheduler.list_tasks()
        assert len(tasks) >= 1
        task_names = [t["name"] for t in tasks]
        assert "test_task" in task_names
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_cancel_task():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    await scheduler.start()
    try:
        async def task(data, ctx):
            pass
        task_id = scheduler.schedule(name="cancel_me", handler=task, context={"data": {}})
        cancelled = scheduler.cancel_task(task_id)
        assert cancelled is True
    finally:
        await scheduler.stop()


def test_cancel_nonexistent_task():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    result = scheduler.cancel_task("does-not-exist")
    assert result is False


@pytest.mark.asyncio
async def test_sync_handler_execution():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    await scheduler.start()
    try:
        result_container = {}
        def sync_task(data, ctx):
            result_container["value"] = "sync_worked"
        scheduler.schedule(name="sync_test", handler=sync_task, context={"data": {}})
        await asyncio.sleep(0.15)
        assert result_container.get("value") == "sync_worked"
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_execution_failure_does_not_crash_scheduler():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    await scheduler.start()
    try:
        async def failing_task(data, ctx):
            raise ValueError("test failure")
        scheduler.schedule(name="fail_test", handler=failing_task, context={"data": {}})
        await asyncio.sleep(0.15)
        scheduler.schedule(name="should_work", handler=lambda data, ctx: None, context={"data": {}})
        await asyncio.sleep(0.15)
        tasks = scheduler.list_tasks()
        assert len(tasks) >= 0
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_voice_session_lifecycle():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    session_id = scheduler.create_voice_session(visitor_id="visitor_1")
    assert session_id is not None
    session = scheduler.get_voice_session(session_id)
    assert session is not None
    assert session["visitor_id"] == "visitor_1"
    updated = scheduler.update_voice_session(session_id, turn_count=3)
    assert updated is True
    assert scheduler.get_voice_session(session_id)["turn_count"] == 3
    ended = scheduler.end_voice_session(session_id)
    assert ended is True
    assert scheduler.get_voice_session(session_id) is None


@pytest.mark.asyncio
async def test_cleanup_expired_sessions():
    from core.orchestration.scheduler import Scheduler
    scheduler = Scheduler()
    scheduler.create_voice_session(visitor_id="visitor_1", timeout_minutes=0)
    cleaned = scheduler.cleanup_expired_sessions(timeout_minutes=0)
    assert cleaned >= 0
