from dataclasses import dataclass, field
from typing import Dict, Optional

from core.analytics.event_tracker import EventTracker
from core.orchestration.execution_history import ExecutionHistory


@dataclass
class CodeGenerationResult:
    task_name: str
    artifact_name: str
    success: bool
    metadata: Dict = field(default_factory=dict)


class CodeGenerationTask:
    """
    Orchestration layer representing a code generation request.

    Integrates with:
        - EventTracker
        - ExecutionHistory
        - BuilderAgent

    Future expansion:
        - AI code generation
        - template selection
        - repository-aware generation
    """

    def __init__(
        self,
        history: Optional[ExecutionHistory] = None,
        tracker: Optional[EventTracker] = None,
    ) -> None:
        self.history = history or ExecutionHistory()
        self.tracker = tracker or EventTracker()

    def execute(
        self,
        task_name: str,
        artifact_name: str,
    ) -> CodeGenerationResult:

        if not task_name:
            raise ValueError("task_name is required")

        if not artifact_name:
            raise ValueError("artifact_name is required")

        self.tracker.track(
            event_type="code_generation_started",
            payload={
                "task": task_name,
                "artifact": artifact_name,
            },
            agent="CodeGenerationTask",
        )

        result = CodeGenerationResult(
            task_name=task_name,
            artifact_name=artifact_name,
            success=True,
        )

        self.history.record(
            task_name=task_name,
            status="success",
            metadata={
                "artifact": artifact_name,
            },
        )

        self.tracker.track(
            event_type="code_generation_completed",
            payload={
                "task": task_name,
                "artifact": artifact_name,
            },
            agent="CodeGenerationTask",
        )

        return result

    def summary(self) -> Dict:
        return {
            "history": self.history.summary(),
            "events": self.tracker.summary(),
        }
