from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionRecord:
    task_name: str
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionHistory:
    """
    Tracks execution history across the swarm.

    Intended usage:

        planner
           ↓
        backlog
           ↓
        coordinator
           ↓
        execution history

    Provides visibility into:
        - successes
        - failures
        - order of execution
        - metadata associated with runs
    """

    def __init__(self) -> None:
        self.records: List[ExecutionRecord] = []

    def record(
        self,
        task_name: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionRecord:

        entry = ExecutionRecord(
            task_name=task_name,
            status=status,
            metadata=metadata or {},
        )

        self.records.append(entry)

        return entry

    def all(self) -> List[ExecutionRecord]:
        return list(self.records)

    def successful(self) -> List[ExecutionRecord]:
        return [record for record in self.records if record.status == "success"]

    def failed(self) -> List[ExecutionRecord]:
        return [record for record in self.records if record.status == "failed"]

    def latest(self) -> Optional[ExecutionRecord]:
        if not self.records:
            return None

        return self.records[-1]

    def count(self) -> int:
        return len(self.records)

    def summary(self) -> Dict[str, int]:
        return {
            "total": len(self.records),
            "successful": len(self.successful()),
            "failed": len(self.failed()),
        }

    def clear(self) -> None:
        self.records = []
