from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BacklogTask:
    name: str
    priority: int
    completed: bool = False


class TaskBacklog:
    """Dynamic task management layer.

    Supports:
        - prioritization
        - completion tracking
        - retry workflows
        - coordinator integration
    """

    def __init__(self) -> None:
        self.tasks: List[BacklogTask] = []

    def add_task(self, name: str, priority: int) -> None:
        self.tasks.append(BacklogTask(name=name, priority=priority))

    def all_tasks(self) -> List[BacklogTask]:
        return list(self.tasks)

    def next_task(self) -> Optional[BacklogTask]:
        pending = [t for t in self.tasks if not t.completed]
        if not pending:
            return None
        return sorted(pending, key=lambda t: t.priority)[0]

    def mark_completed(self, task_name: str) -> bool:
        for task in self.tasks:
            if task.name == task_name:
                task.completed = True
                return True
        return False

    def reset_task(self, task_name: str) -> bool:
        for task in self.tasks:
            if task.name == task_name:
                task.completed = False
                return True
        return False

    def remove_task(self, task_name: str) -> bool:
        before = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.name != task_name]
        return len(self.tasks) < before

    def completed_tasks(self) -> List[str]:
        return [task.name for task in self.tasks if task.completed]

    def pending_tasks(self) -> List[str]:
        return [task.name for task in self.tasks if not task.completed]

    def summary(self) -> Dict:
        return {
            "total": len(self.tasks),
            "completed": len(self.completed_tasks()),
            "pending": len(self.pending_tasks()),
        }
