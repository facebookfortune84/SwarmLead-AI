from dataclasses import dataclass, field
from typing import Dict, Optional

from core.orchestration.builder_agent import BuilderAgent
from core.orchestration.repair_agent import RepairAgent
from core.orchestration.repository_planner import RepositoryPlanner
from core.orchestration.review_agent import (
    ReviewAgent,
    ReviewFinding,
)


@dataclass
class SwarmRunResult:
    task_name: Optional[str]
    build_success: bool
    review_success: bool
    repaired: bool
    metadata: Dict = field(default_factory=dict)


class SwarmCoordinator:
    """
    Coordinates the autonomous repository workflow.

    Planner
        ↓
    Builder
        ↓
    Reviewer
        ↓
    RepairAgent
    """

    def __init__(
        self,
        planner=None,
        builder=None,
        reviewer=None,
        repairer=None,
    ):
        self.planner = planner or RepositoryPlanner()
        self.builder = builder or BuilderAgent()
        self.reviewer = reviewer or ReviewAgent()
        self.repairer = repairer or RepairAgent()

    def run_next_task(
        self,
    ) -> SwarmRunResult:

        task = self.planner.next_task()

        if task is None:
            return SwarmRunResult(
                task_name=None,
                build_success=False,
                review_success=False,
                repaired=False,
                metadata={"reason": "no_tasks_remaining"},
            )

        build_result = self.builder.execute_task(
            task.name,
            artifacts=[f"{task.name}.py"],
        )

        review_result = self.reviewer.review_artifact(f"{task.name}.py")

        repair_result = self.repairer.repair()

        if build_result.success:
            self.planner.mark_complete(task.name)

        return SwarmRunResult(
            task_name=task.name,
            build_success=build_result.success,
            review_success=review_result.approved,
            repaired=repair_result.repaired,
        )

    def run_review_failure(
        self,
        task_name: str,
    ) -> SwarmRunResult:

        build_result = self.builder.execute_task(task_name)

        review_result = self.reviewer.review_artifact(
            f"{task_name}.py",
            findings=[
                ReviewFinding(
                    severity="error",
                    message="review failure",
                )
            ],
        )

        repair_action = self.repairer.suggest_fix(
            f"{task_name}.py",
            "review failure",
        )

        repair_result = self.repairer.repair(actions=[repair_action])

        return SwarmRunResult(
            task_name=task_name,
            build_success=build_result.success,
            review_success=review_result.approved,
            repaired=repair_result.repaired,
        )

    def summary(self) -> Dict:

        return {
            "completed_tasks": self.builder.completed(),
            "failed_tasks": self.builder.failed(),
            "planner": self.planner.summary(),
            "builder": self.builder.summary(),
        }
