import pytest
import asyncio
import json
import io
import logging
from utils.logging import JSONFormatter


def capture_log(logger):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return stream, handler


@pytest.mark.asyncio
async def test_structured_error_logging():
    from core.orchestration.scheduler import Scheduler
    from utils.logging import get_logger

    scheduler = Scheduler()
    logger = get_logger("core.orchestration.scheduler")

    stream, handler = capture_log(logger)

    try:

        async def failing_task(data, context):
            raise ValueError("test failure")

        scheduler.schedule(failing_task, {}, retries=0)

        import asyncio

        await asyncio.sleep(0.1)

        handler.flush()
        logs = stream.getvalue().strip().split("\n")

        # Find error log
        parsed = [json.loads(log) for log in logs if log.strip()]
        error_logs = [log for log in parsed if log["level"] == "ERROR"]

        assert len(error_logs) > 0

        error_log = error_logs[-1]

        assert error_log["message"] == "Task execution failed"
        assert "task_id" in error_log
        assert "error" in error_log
        assert "attempt" in error_log

    finally:
        logger.removeHandler(handler)


@pytest.mark.asyncio
async def test_schedule_and_execute():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    result_container = {}

    async def task(data, context):
        result_container["result"] = "done"

    scheduler.schedule(task, {})

    await asyncio.sleep(0.1)

    assert result_container["result"] == "done"


@pytest.mark.asyncio
async def test_delayed_execution():
    from core.orchestration.scheduler import Scheduler
    import time

    scheduler = Scheduler()

    timestamps = {}

    async def task(data, context):
        timestamps["executed"] = time.time()

    start = time.time()
    scheduler.schedule(task, {}, delay=0.1)

    await asyncio.sleep(0.2)

    assert timestamps["executed"] - start >= 0.09


@pytest.mark.asyncio
async def test_retry_logic():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    attempts = {"count": 0}

    async def task(data, context):
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise ValueError("fail")

    scheduler.schedule(task, {}, retries=1, retry_delay=0.05)

    await asyncio.sleep(0.2)

    assert attempts["count"] == 2


@pytest.mark.asyncio
async def test_cancel_task():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    async def task(data, context):
        pass

    task_id = scheduler.schedule(task, {}, delay=1)

    cancelled = scheduler.cancel(task_id)

    assert cancelled is True


@pytest.mark.asyncio
async def test_list_tasks():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    async def task(data, context):
        pass

    task_id = scheduler.schedule(task, {}, delay=0.1)

    tasks = scheduler.list_tasks()

    assert task_id in tasks


@pytest.mark.asyncio
async def test_retry_exhaustion():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    attempts = {"count": 0}

    async def always_fail(data, context):
        attempts["count"] += 1
        raise ValueError("fail always")

    scheduler.schedule(always_fail, {}, retries=1, retry_delay=0.05)

    await asyncio.sleep(0.2)

    # Should attempt initial + 1 retry = 2
    assert attempts["count"] == 2


def test_cancel_nonexistent_task():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    result = scheduler.cancel("does-not-exist")

    assert result is False


@pytest.mark.asyncio
async def test_sync_handler_execution():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    result_container = {}

    def sync_task(data, context):
        result_container["value"] = "sync_worked"

    scheduler.schedule(sync_task, {})

    await asyncio.sleep(0.1)

    assert result_container["value"] == "sync_worked"


@pytest.mark.asyncio
async def test_no_retry_failure_path():
    from core.orchestration.scheduler import Scheduler

    scheduler = Scheduler()

    attempts = {"count": 0}

    async def fail_once(data, context):
        attempts["count"] += 1
        raise RuntimeError("fail")

    # No retries allowed
    scheduler.schedule(fail_once, {}, retries=0)

    await asyncio.sleep(0.1)

    assert attempts["count"] == 1
