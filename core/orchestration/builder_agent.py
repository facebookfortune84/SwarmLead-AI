from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BuildResult:
    task_name: str
    success: bool
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class BuilderAgent:
    """
    Executes repository build tasks.

    This is intentionally lightweight for v2 and can later
    be connected to:
        - LLM generation
        - CI runners
        - code review agents
        - repair agents
    """

    def __init__(self):
        self.completed_tasks = []
        self.failed_tasks = []

    def execute_task(
        self,
        task_name: str,
        artifacts: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        fail: bool = False,
    ) -> BuildResult:

        result = BuildResult(
            task_name=task_name,
            success=not fail,
            artifacts=artifacts or [],
            metadata=metadata or {},
        )

        if result.success:
            self.completed_tasks.append(task_name)
        else:
            self.failed_tasks.append(task_name)

        return result

    def completed(self) -> List[str]:
        return list(self.completed_tasks)

    def failed(self) -> List[str]:
        return list(self.failed_tasks)

    def has_completed(
        self,
        task_name: str,
    ) -> bool:
        return task_name in self.completed_tasks

    def has_failed(
        self,
        task_name: str,
    ) -> bool:
        return task_name in self.failed_tasks

    def summary(self) -> Dict:
        return {
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "success_rate": (
                len(self.completed_tasks)
                / (
                    len(self.completed_tasks)
                    + len(self.failed_tasks)
                )
                if (
                    len(self.completed_tasks)
                    + len(self.failed_tasks)
                ) > 0
                else 0.0
            ),
        }

    def reset(self):
        self.completed_tasks = []
        self.failed_tasks = []