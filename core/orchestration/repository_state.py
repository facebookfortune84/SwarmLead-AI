from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RepositorySnapshot:
    completed_tasks: List[str] = field(default_factory=list)

    failed_tasks: List[str] = field(default_factory=list)

    files_created: List[str] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)


class RepositoryState:
    """
    Persistent repository state tracking.

    Tracks:
        - completed tasks
        - failed tasks
        - files created
        - repository metadata
    """

    def __init__(self):
        self.snapshot = RepositorySnapshot()

    def record_completion(
        self,
        task_name: str,
    ):
        if task_name not in self.snapshot.completed_tasks:
            self.snapshot.completed_tasks.append(task_name)

    def record_failure(
        self,
        task_name: str,
    ):
        if task_name not in self.snapshot.failed_tasks:
            self.snapshot.failed_tasks.append(task_name)

    def record_file(
        self,
        filename: str,
    ):
        if filename not in self.snapshot.files_created:
            self.snapshot.files_created.append(filename)

    def set_metadata(
        self,
        key: str,
        value,
    ):
        self.snapshot.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default=None,
    ):
        return self.snapshot.metadata.get(
            key,
            default,
        )

    def completed_tasks(self):
        return list(self.snapshot.completed_tasks)

    def failed_tasks(self):
        return list(self.snapshot.failed_tasks)

    def files_created(self):
        return list(self.snapshot.files_created)

    def summary(self):
        return {
            "completed": len(self.snapshot.completed_tasks),
            "failed": len(self.snapshot.failed_tasks),
            "files": len(self.snapshot.files_created),
            "metadata": dict(self.snapshot.metadata),
        }

    def reset(self):
        self.snapshot = RepositorySnapshot()
