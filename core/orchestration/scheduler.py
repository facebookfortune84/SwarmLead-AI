import asyncio
import time
import uuid
from typing import Callable, Dict, Any, Optional

from utils.logging import get_logger, log_with_context, log_performance

logger = get_logger(__name__)


class ScheduledTask:
    def __init__(
        self,
        task_id: str,
        handler: Callable,
        input_data: Dict[str, Any],
        delay: float = 0,
        retries: int = 0,
        retry_delay: float = 1.0,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.task_id = task_id
        self.handler = handler
        self.input_data = input_data
        self.delay = delay
        self.retries = retries
        self.retry_delay = retry_delay
        self.context = context or {}

        self.attempts = 0
        self.created_at = time.time()


class Scheduler:
    """
    Production-grade async scheduler.

    Features:
    - Delayed tasks
    - Retry with backoff
    - Concurrency control
    - Task tracking
    """

    def __init__(self, max_concurrent_tasks: int = 5):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    # ------------------------------------------------------------------
    # Task Scheduling
    # ------------------------------------------------------------------

    def schedule(
        self,
        handler: Callable,
        input_data: Dict[str, Any],
        delay: float = 0,
        retries: int = 0,
        retry_delay: float = 1.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        task_id = str(uuid.uuid4())

        task = ScheduledTask(
            task_id=task_id,
            handler=handler,
            input_data=input_data,
            delay=delay,
            retries=retries,
            retry_delay=retry_delay,
            context=context,
        )

        self.tasks[task_id] = task

        logger.info(f"Task scheduled: {task_id}")

        asyncio.create_task(self._execute_task(task))

        return task_id

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def _execute_task(self, task: ScheduledTask):
        await asyncio.sleep(task.delay)

        trace_id = str(uuid.uuid4())

        async with self.semaphore:
            await self._run_with_retries(task, trace_id)

    async def _run_with_retries(self, task: ScheduledTask, trace_id: str):
        start_time = time.time()

        while task.attempts <= task.retries:
            try:
                task.attempts += 1

                log_with_context(
                    logger,
                    "info",
                    f"Executing task {task.task_id}",
                    extra={"attempt": task.attempts},
                    trace_id=trace_id,
                )

                if asyncio.iscoroutinefunction(task.handler):
                    result = await task.handler(task.input_data, task.context)
                else:
                    result = task.handler(task.input_data, task.context)

                duration = time.time() - start_time

                log_performance(
                    logger,
                    "scheduler_task_execution",
                    duration,
                    metadata={"task_id": task.task_id},
                    trace_id=trace_id,
                )

                # Remove task after success
                self.tasks.pop(task.task_id, None)

                return result

            except Exception as e:
                log_with_context(
                    logger,
                    "error",
                    "Task execution failed",
                    extra={
                        "task_id": task.task_id,
                        "error": str(e),
                        "attempt": task.attempts,
                        "max_retries": task.retries,
                    },
                    trace_id=trace_id,
                )

                if task.attempts > task.retries:
                    self.tasks.pop(task.task_id, None)
                    return None

                await asyncio.sleep(task.retry_delay)

    # ------------------------------------------------------------------
    # Management
    # ------------------------------------------------------------------

    def cancel(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Task cancelled: {task_id}")
            return True
        return False

    def list_tasks(self) -> Dict[str, Dict[str, Any]]:
        return {
            task_id: {
                "attempts": task.attempts,
                "created_at": task.created_at,
                "delay": task.delay,
            }
            for task_id, task in self.tasks.items()
        }
