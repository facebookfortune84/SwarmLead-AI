from core.orchestration.autonomous_swarm import (
    AutonomousRunResult,
    AutonomousSwarm,
)


def test_run_cycle():
    swarm = AutonomousSwarm()

    result = swarm.run_cycle()

    assert result.task_name == "api_layer"


def test_run_cycle_updates_history():
    swarm = AutonomousSwarm()

    swarm.run_cycle()

    assert swarm.history.count() == 1


def test_run_cycle_updates_state():
    swarm = AutonomousSwarm()

    swarm.run_cycle()

    summary = swarm.state.summary()

    assert summary["completed"] == 1


def test_run_cycles():
    swarm = AutonomousSwarm()

    result = swarm.run_cycles(2)

    assert result.tasks_executed == 2
    assert result.successful_tasks == 2
    assert result.failed_tasks == 0


def test_run_cycles_stops_when_done():
    swarm = AutonomousSwarm()

    result = swarm.run_cycles(20)

    assert result.tasks_executed == 4


def test_summary():
    swarm = AutonomousSwarm()

    swarm.run_cycle()

    summary = swarm.summary()

    assert "history" in summary
    assert "state" in summary


def test_reset():
    swarm = AutonomousSwarm()

    swarm.run_cycle()

    swarm.reset()

    assert swarm.history.count() == 0

    assert swarm.state.summary()["completed"] == 0


def test_empty_cycle_after_completion():
    swarm = AutonomousSwarm()

    swarm.run_cycles(10)

    result = swarm.run_cycle()

    assert result.task_name is None


def test_autonomous_run_result_dataclass():
    result = AutonomousRunResult(
        tasks_executed=1,
        successful_tasks=1,
        failed_tasks=0,
    )

    assert result.tasks_executed == 1
    assert result.successful_tasks == 1
    assert result.failed_tasks == 0


def test_multiple_summaries():
    swarm = AutonomousSwarm()

    swarm.run_cycles(2)

    summary = swarm.summary()

    assert summary["history"]["total"] == 2


def test_history_contains_records():
    swarm = AutonomousSwarm()

    swarm.run_cycle()

    records = swarm.history.all()

    assert len(records) == 1


def test_state_tracks_completion():
    swarm = AutonomousSwarm()

    swarm.run_cycle()

    completed = swarm.state.completed_tasks()

    assert len(completed) == 1
