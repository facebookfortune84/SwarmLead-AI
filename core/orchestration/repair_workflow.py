from dataclasses import dataclass, field
from typing import Dict, Optional

from core.analytics.event_tracker import EventTracker
from core.orchestration.execution_history import ExecutionHistory
from core.orchestration.repair_agent import (
    RepairAgent,
    RepairResult,
)
from core.orchestration.review_agent import (
    ReviewAgent,
    ReviewResult,
)


@dataclass
class RepairWorkflowResult:
    artifact: str
    repaired: bool
    repair_result: Optional[RepairResult]
    metadata: Dict = field(default_factory=dict)


class RepairWorkflow:
    """
    Coordinates repair activity following review failures.

    Workflow:

        ReviewResult
              ↓
        RepairWorkflow
              ↓
        RepairAgent
              ↓
        ExecutionHistory
              ↓
        EventTracker
    """

    def __init__(
        self,
        repair_agent: Optional[RepairAgent] = None,
        review_agent: Optional[ReviewAgent] = None,
        history: Optional[ExecutionHistory] = None,
        tracker: Optional[EventTracker] = None,
    ) -> None:

        self.repair_agent = repair_agent or RepairAgent()
        self.review_agent = review_agent or ReviewAgent()
        self.history = history or ExecutionHistory()
        self.tracker = tracker or EventTracker()

    def execute(
        self,
        artifact: str,
        review_result: ReviewResult,
    ) -> RepairWorkflowResult:

        self.tracker.track(
            event_type="repair_workflow_started",
            payload={
                "artifact": artifact,
            },
            agent="RepairWorkflow",
        )

        if review_result.approved:
            self.history.record(
                task_name=artifact,
                status="not_required",
            )

            self.tracker.track(
                event_type="repair_workflow_skipped",
                payload={
                    "artifact": artifact,
                },
                agent="RepairWorkflow",
            )

            return RepairWorkflowResult(
                artifact=artifact,
                repaired=False,
                repair_result=None,
            )

        actions = [
            self.repair_agent.suggest_fix(
                artifact,
                finding.message,
            )
            for finding in review_result.findings
        ]

        repair_result = self.repair_agent.repair(
            actions=actions,
        )

        self.history.record(
            task_name=artifact,
            status="repaired" if repair_result.repaired else "failed",
            metadata={
                "repair_actions": len(actions),
            },
        )

        self.tracker.track(
            event_type="repair_workflow_completed",
            payload={
                "artifact": artifact,
                "actions": len(actions),
            },
            agent="RepairWorkflow",
        )

        return RepairWorkflowResult(
            artifact=artifact,
            repaired=repair_result.repaired,
            repair_result=repair_result,
        )

    def summary(self) -> Dict:

        return {
            "history": self.history.summary(),
            "events": self.tracker.summary(),
        }

    def reset(self) -> None:

        self.history.clear()
        self.tracker.clear()
