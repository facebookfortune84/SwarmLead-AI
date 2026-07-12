from dataclasses import dataclass, field
from typing import Dict, Optional

from core.analytics.event_tracker import EventTracker
from core.orchestration.execution_history import ExecutionHistory
from core.orchestration.task_backlog import BacklogTask, TaskBacklog


@dataclass
class DecisionResult:
    selected_task: Optional[BacklogTask]
    reason: str
    metadata: Dict = field(default_factory=dict)


class SwarmDecisionEngine:
    """
    Determines which task should execute next.

    Current strategy:
        - priority-based selection

    Future strategies:
        - repository health scoring
        - technical debt weighting
        - autonomous planning
        - risk-adjusted scheduling
    """

    def __init__(
        self,
        backlog: Optional[TaskBacklog] = None,
        history: Optional[ExecutionHistory] = None,
        tracker: Optional[EventTracker] = None,
    ) -> None:

        self.backlog = backlog or TaskBacklog()
        self.history = history or ExecutionHistory()
        self.tracker = tracker or EventTracker()

    def decide(self) -> DecisionResult:

        task = self.backlog.next_task()

        if task is None:
            self.tracker.track(
                event_type="decision_no_task",
                agent="SwarmDecisionEngine",
            )

            return DecisionResult(
                selected_task=None,
                reason="no_tasks_available",
            )

        self.history.record(
            task_name=task.name,
            status="selected",
            metadata={
                "priority": task.priority,
            },
        )

        self.tracker.track(
            event_type="task_selected",
            payload={
                "task_name": task.name,
                "priority": task.priority,
            },
            agent="SwarmDecisionEngine",
        )

        return DecisionResult(
            selected_task=task,
            reason="highest_priority_pending",
            metadata={
                "priority": task.priority,
            },
        )

    def summary(self) -> Dict:
        return {
            "history": self.history.summary(),
            "events": self.tracker.summary(),
            "pending_tasks": len(self.backlog.pending_tasks()),
        }

    def reset(self) -> None:
        self.history.clear()
        self.tracker.clear()
