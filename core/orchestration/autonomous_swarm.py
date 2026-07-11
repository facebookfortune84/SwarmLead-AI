from dataclasses import dataclass, field
from typing import Dict

from core.orchestration.execution_history import (
    ExecutionHistory,
)
from core.orchestration.repository_state import (
    RepositoryState,
)
from core.orchestration.swarm_coordinator import (
    SwarmCoordinator,
)


@dataclass
class AutonomousRunResult:
    tasks_executed: int
    successful_tasks: int
    failed_tasks: int
    metadata: Dict = field(default_factory=dict)


class AutonomousSwarm:
    """
    First-generation autonomous repository workflow.

    Components:

        SwarmCoordinator
                ↓
        ExecutionHistory
                ↓
        RepositoryState

    Purpose:

        - execute autonomous build cycles
        - track execution history
        - update repository state
        - expose operational metrics
    """

    def __init__(
        self,
        coordinator=None,
        history=None,
        state=None,
    ):
        self.coordinator = coordinator or SwarmCoordinator()

        self.history = history or ExecutionHistory()

        self.state = state or RepositoryState()

    def run_cycle(self):

        result = self.coordinator.run_next_task()

        if result.task_name is None:
            return result

        status = "success" if result.build_success else "failed"

        self.history.record(
            result.task_name,
            status,
        )

        if result.build_success:
            self.state.record_completion(result.task_name)

        else:
            self.state.record_failure(result.task_name)

        return result

    def run_cycles(
        self,
        count: int,
    ) -> AutonomousRunResult:

        executed = 0
        successful = 0
        failed = 0

        for _ in range(count):
            result = self.run_cycle()

            if result.task_name is None:
                break

            executed += 1

            if result.build_success:
                successful += 1
            else:
                failed += 1

        return AutonomousRunResult(
            tasks_executed=executed,
            successful_tasks=successful,
            failed_tasks=failed,
        )

    def summary(self) -> Dict:

        return {
            "history": self.history.summary(),
            "state": self.state.summary(),
        }

    def reset(self):

        self.history.clear()
        self.state.reset()
