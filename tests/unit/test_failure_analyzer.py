from core.orchestration.failure_analyzer import (
    FailureAnalyzer,
    FailureRecord,
    FailureReport,
)


def test_analyze():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze(
        [
            FailureRecord(
                component="x",
                message="fail",
                severity="critical",
            )
        ]
    )

    assert len(report.failures) == 1


def test_count():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze(
        [
            FailureRecord(
                component="c",
                message="m",
                severity="critical",
            )
        ]
    )

    assert analyzer.count(report) == 1


def test_critical():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze(
        [
            FailureRecord(
                component="a",
                message="x",
                severity="critical",
            ),
            FailureRecord(
                component="b",
                message="y",
                severity="warning",
            ),
        ]
    )

    assert len(analyzer.critical(report)) == 1


def test_warnings():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze(
        [
            FailureRecord(
                component="a",
                message="x",
                severity="warning",
            )
        ]
    )

    assert len(analyzer.warnings(report)) == 1


def test_has_failures_true():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze(
        [
            FailureRecord(
                component="a",
                message="x",
                severity="warning",
            )
        ]
    )

    assert analyzer.has_failures(report) is True


def test_has_failures_false():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze([])

    assert analyzer.has_failures(report) is False


def test_summary_empty():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze([])

    summary = analyzer.summary(report)

    assert summary["failures"] == 0
    assert summary["critical"] == 0
    assert summary["warnings"] == 0


def test_summary_populated():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze(
        [
            FailureRecord(
                component="a",
                message="x",
                severity="critical",
            ),
            FailureRecord(
                component="b",
                message="y",
                severity="warning",
            ),
        ]
    )

    summary = analyzer.summary(report)

    assert summary["failures"] == 2
    assert summary["critical"] == 1
    assert summary["warnings"] == 1


def test_clear():
    analyzer = FailureAnalyzer()

    report = analyzer.analyze(
        [
            FailureRecord(
                component="x",
                message="y",
                severity="critical",
            )
        ]
    )

    analyzer.clear(report)

    assert report.failures == []


def test_failure_record_dataclass():
    record = FailureRecord(
        component="agent",
        message="boom",
        severity="critical",
    )

    assert record.component == "agent"
    assert record.message == "boom"
    assert record.severity == "critical"


def test_failure_report_dataclass():
    report = FailureReport()

    assert report.failures == []
