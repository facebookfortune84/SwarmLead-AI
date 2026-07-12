from dataclasses import dataclass, field
from typing import Dict, Optional

from core.analytics.event_tracker import EventTracker
from core.orchestration.execution_history import ExecutionHistory


@dataclass
class GeneratedTestSuite:
    """
    Represents a generated test suite artifact.
    """

    source_artifact: str
    test_artifact: str
    success: bool
    metadata: Dict = field(default_factory=dict)


class UnitTestGenerationTask:
    """
    Orchestration layer responsible for test generation requests.

    Integrates with:
        - EventTracker
        - ExecutionHistory

    Future expansion:
        - LLM generated tests
        - Coverage-driven generation
        - Repository-aware test creation
        - RepairWorkflow integration
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
        source_artifact: str,
        test_artifact: str,
    ) -> GeneratedTestSuite:

        if not source_artifact:
            raise ValueError("source_artifact is required")

        if not test_artifact:
            raise ValueError("test_artifact is required")

        self.tracker.track(
            event_type="test_generation_started",
            payload={
                "source_artifact": source_artifact,
                "test_artifact": test_artifact,
            },
            agent="TestGenerationTask",
        )

        result = GeneratedTestSuite(
            source_artifact=source_artifact,
            test_artifact=test_artifact,
            success=True,
        )

        self.history.record(
            task_name=f"generate_tests:{source_artifact}",
            status="success",
            metadata={
                "source_artifact": source_artifact,
                "test_artifact": test_artifact,
            },
        )

        self.tracker.track(
            event_type="test_generation_completed",
            payload={
                "source_artifact": source_artifact,
                "test_artifact": test_artifact,
            },
            agent="TestGenerationTask",
        )

        return result

    def summary(self) -> Dict:
        return {
            "history": self.history.summary(),
            "events": self.tracker.summary(),
        }
