from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RefactorTask:
    component: str
    reason: str
    priority: int


@dataclass
class RefactorPlan:
    tasks: List[RefactorTask] = field(default_factory=list)


class RefactorPlanner:
    """
    Converts technical debt items into
    refactoring activities.
    """

    def create_plan(
        self,
        components: List[str],
    ) -> RefactorPlan:

        tasks = []

        for component in components:
            tasks.append(
                RefactorTask(
                    component=component,
                    reason="technical_debt",
                    priority=5,
                )
            )

        return RefactorPlan(tasks=tasks)

    def task_count(
        self,
        plan: RefactorPlan,
    ) -> int:

        return len(plan.tasks)

    def highest_priority(
        self,
        plan: RefactorPlan,
    ):

        if not plan.tasks:
            return None

        return sorted(
            plan.tasks,
            key=lambda t: t.priority,
        )[0]

    def summary(
        self,
        plan: RefactorPlan,
    ) -> Dict:

        highest = self.highest_priority(plan)

        return {
            "tasks": len(plan.tasks),
            "highest_priority": (highest.priority if highest else None),
        }

    def clear(
        self,
        plan: RefactorPlan,
    ) -> None:

        plan.tasks.clear()
