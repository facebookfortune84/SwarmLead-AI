from dataclasses import dataclass, field
from typing import Dict, List

from core.orchestration.failure_analyzer import (
    FailureReport,
)


@dataclass
class ImprovementTask:
    name: str
    priority: int
    reason: str


@dataclass
class ImprovementPlan:
    tasks: List[ImprovementTask] = field(default_factory=list)


class ImprovementPlanner:
    """
    Converts repository weaknesses into
    actionable future work.

    Future integrations:
        - RepositoryScanner
        - DependencyGraph
        - CoverageAnalyzer
        - ArchitectureValidator
        - AutonomousSwarm
    """

    def create_plan(
        self,
        failure_report: FailureReport,
    ) -> ImprovementPlan:

        tasks: List[ImprovementTask] = []

        for failure in failure_report.failures:
            priority = 1 if failure.severity == "critical" else 5

            tasks.append(
                ImprovementTask(
                    name=f"fix_{failure.component}",
                    priority=priority,
                    reason=failure.message,
                )
            )

        return ImprovementPlan(tasks=tasks)

    def task_count(
        self,
        plan: ImprovementPlan,
    ) -> int:

        return len(plan.tasks)

    def highest_priority(
        self,
        plan: ImprovementPlan,
    ):

        if not plan.tasks:
            return None

        return sorted(
            plan.tasks,
            key=lambda t: t.priority,
        )[0]

    def priorities(
        self,
        plan: ImprovementPlan,
    ) -> List[int]:
        return [task.priority for task in plan.tasks]

    def summary(
        self,
        plan: ImprovementPlan,
    ) -> Dict:

        highest = self.highest_priority(plan)

        return {
            "tasks": len(plan.tasks),
            "highest_priority": (highest.priority if highest else None),
        }

    def clear(
        self,
        plan: ImprovementPlan,
    ) -> None:

        plan.tasks.clear()
