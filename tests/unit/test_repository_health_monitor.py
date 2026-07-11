from core.orchestration.repository_health_monitor import (
    HealthReport,
    HealthSnapshot,
    RepositoryHealthMonitor,
)


def test_record():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    snapshot = monitor.record(
        report,
        90.0,
    )

    assert snapshot.score == 90.0
    assert len(report.snapshots) == 1


def test_latest_none():
    monitor = RepositoryHealthMonitor()

    assert monitor.latest(HealthReport()) is None


def test_latest():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 80.0)
    monitor.record(report, 90.0)

    assert monitor.latest(report).score == 90.0


def test_average_empty():
    monitor = RepositoryHealthMonitor()

    assert monitor.average(HealthReport()) == 0.0


def test_average():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 80.0)
    monitor.record(report, 100.0)

    assert monitor.average(report) == 90.0


def test_improving_false_no_history():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 90.0)

    assert monitor.improving(report) is False


def test_improving_true():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 80.0)
    monitor.record(report, 90.0)

    assert monitor.improving(report) is True


def test_declining_false_no_history():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 90.0)

    assert monitor.declining(report) is False


def test_declining_true():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 100.0)
    monitor.record(report, 80.0)

    assert monitor.declining(report) is True


def test_snapshot_count():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 1.0)
    monitor.record(report, 2.0)

    assert monitor.snapshot_count(report) == 2


def test_summary_empty():
    monitor = RepositoryHealthMonitor()

    summary = monitor.summary(HealthReport())

    assert summary["snapshots"] == 0
    assert summary["average"] == 0.0
    assert summary["latest"] is None
    assert summary["improving"] is False


def test_summary_populated():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 80.0)
    monitor.record(report, 100.0)

    summary = monitor.summary(report)

    assert summary["snapshots"] == 2
    assert summary["average"] == 90.0
    assert summary["latest"] == 100.0
    assert summary["improving"] is True


def test_clear():
    monitor = RepositoryHealthMonitor()

    report = HealthReport()

    monitor.record(report, 90.0)

    monitor.clear(report)

    assert report.snapshots == []


def test_health_snapshot_dataclass():
    snapshot = HealthSnapshot(score=95.0)

    assert snapshot.score == 95.0


def test_health_report_dataclass():
    report = HealthReport()

    assert report.snapshots == []
