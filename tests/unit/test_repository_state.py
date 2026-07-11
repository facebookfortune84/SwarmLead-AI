from core.orchestration.repository_state import (
    RepositorySnapshot,
    RepositoryState,
)


def test_record_completion():
    state = RepositoryState()

    state.record_completion("task")

    assert state.completed_tasks() == ["task"]


def test_record_completion_duplicate():
    state = RepositoryState()

    state.record_completion("task")

    state.record_completion("task")

    assert state.completed_tasks() == ["task"]


def test_record_failure():
    state = RepositoryState()

    state.record_failure("bad")

    assert state.failed_tasks() == ["bad"]


def test_record_failure_duplicate():
    state = RepositoryState()

    state.record_failure("bad")

    state.record_failure("bad")

    assert state.failed_tasks() == ["bad"]


def test_record_file():
    state = RepositoryState()

    state.record_file("demo.py")

    assert state.files_created() == ["demo.py"]


def test_record_file_duplicate():
    state = RepositoryState()

    state.record_file("demo.py")

    state.record_file("demo.py")

    assert state.files_created() == ["demo.py"]


def test_set_metadata():
    state = RepositoryState()

    state.set_metadata(
        "env",
        "test",
    )

    assert state.get_metadata("env") == "test"


def test_get_metadata_default():
    state = RepositoryState()

    assert (
        state.get_metadata(
            "missing",
            "default",
        )
        == "default"
    )


def test_summary_empty():
    state = RepositoryState()

    summary = state.summary()

    assert summary["completed"] == 0
    assert summary["failed"] == 0
    assert summary["files"] == 0


def test_summary_populated():
    state = RepositoryState()

    state.record_completion("one")

    state.record_failure("two")

    state.record_file("file.py")

    state.set_metadata(
        "branch",
        "main",
    )

    summary = state.summary()

    assert summary["completed"] == 1
    assert summary["failed"] == 1
    assert summary["files"] == 1
    assert summary["metadata"]["branch"] == "main"


def test_reset():
    state = RepositoryState()

    state.record_completion("one")

    state.record_failure("two")

    state.record_file("file.py")

    state.reset()

    assert state.completed_tasks() == []

    assert state.failed_tasks() == []

    assert state.files_created() == []


def test_repository_snapshot_dataclass():
    snapshot = RepositorySnapshot()

    assert snapshot.completed_tasks == []

    assert snapshot.failed_tasks == []

    assert snapshot.files_created == []

    assert snapshot.metadata == {}
