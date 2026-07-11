from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BuildTask:
    """
    Represents a repository work item.
    """

    name: str
    priority: int
    category: str
    description: str


class RepositoryPlanner:
    """
    Generates and prioritizes repository build tasks.
    """

    DEFAULT_TASKS = [
        BuildTask(
            name="api_layer",
            priority=1,
            category="infrastructure",
            description="Build FastAPI service layer",
        ),
        BuildTask(
            name="builder_agent",
            priority=2,
            category="automation",
            description="Create autonomous builder agent",
        ),
        BuildTask(
            name="review_agent",
            priority=3,
            category="automation",
            description="Create code review agent",
        ),
        BuildTask(
            name="repair_agent",
            priority=4,
            category="automation",
            description="Create automated repair agent",
        ),
    ]

    def __init__(
        self,
        completed: Optional[List[str]] = None,
    ):
        self.completed = set(completed or [])

    def all_tasks(self) -> List[BuildTask]:
        return list(self.DEFAULT_TASKS)

    def completed_tasks(self) -> List[str]:
        return sorted(self.completed)

    def mark_complete(
        self,
        task_name: str,
    ) -> None:
        self.completed.add(task_name)

    def is_complete(
        self,
        task_name: str,
    ) -> bool:
        return task_name in self.completed

    def pending_tasks(
        self,
    ) -> List[BuildTask]:
        return [task for task in self.DEFAULT_TASKS if task.name not in self.completed]

    def next_task(
        self,
    ) -> Optional[BuildTask]:
        pending = self.pending_tasks()

        if not pending:
            return None

        return sorted(
            pending,
            key=lambda t: t.priority,
        )[0]

    def summary(
        self,
    ) -> Dict:
        return {
            "total": len(self.DEFAULT_TASKS),
            "completed": len(self.completed),
            "remaining": len(self.pending_tasks()),
        }
