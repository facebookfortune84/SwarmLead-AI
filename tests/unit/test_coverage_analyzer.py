from core.orchestration.coverage_analyzer import (
    CoverageAnalyzer,
    CoverageReport,
    CoverageTarget,
)


def test_analyze_empty():
    analyzer = CoverageAnalyzer()

    report = analyzer.analyze([])

    assert report.targets == []


def test_analyze_populated():
    analyzer = CoverageAnalyzer()

    report = analyzer.analyze(
        [
            CoverageTarget(
                name="module",
                coverage=90.0,
            )
        ]
    )

    assert len(report.targets) == 1


def test_average_coverage_empty():
    analyzer = CoverageAnalyzer()

    report = CoverageReport()

    assert analyzer.average_coverage(report) == 0.0


def test_average_coverage():
    analyzer = CoverageAnalyzer()

    report = CoverageReport(
        targets=[
            CoverageTarget(
                name="a",
                coverage=100.0,
            ),
            CoverageTarget(
                name="b",
                coverage=50.0,
            ),
        ]
    )

    assert analyzer.average_coverage(report) == 75.0


def test_low_coverage_default():
    analyzer = CoverageAnalyzer()

    report = CoverageReport(
        targets=[
            CoverageTarget(
                name="a",
                coverage=50.0,
            ),
            CoverageTarget(
                name="b",
                coverage=100.0,
            ),
        ]
    )

    results = analyzer.low_coverage(report)

    assert len(results) == 1
    assert results[0].name == "a"


def test_low_coverage_custom_threshold():
    analyzer = CoverageAnalyzer()

    report = CoverageReport(
        targets=[
            CoverageTarget(
                name="a",
                coverage=70.0,
            )
        ]
    )

    results = analyzer.low_coverage(
        report,
        threshold=75.0,
    )

    assert len(results) == 1


def test_fully_covered():
    analyzer = CoverageAnalyzer()

    report = CoverageReport(
        targets=[
            CoverageTarget(
                name="a",
                coverage=100.0,
            ),
            CoverageTarget(
                name="b",
                coverage=90.0,
            ),
        ]
    )

    results = analyzer.fully_covered(report)

    assert len(results) == 1
    assert results[0].name == "a"


def test_highest_coverage_none():
    analyzer = CoverageAnalyzer()

    assert analyzer.highest_coverage(CoverageReport()) is None


def test_highest_coverage():
    analyzer = CoverageAnalyzer()

    report = CoverageReport(
        targets=[
            CoverageTarget(
                name="a",
                coverage=50.0,
            ),
            CoverageTarget(
                name="b",
                coverage=100.0,
            ),
        ]
    )

    result = analyzer.highest_coverage(report)

    assert result.name == "b"


def test_summary_empty():
    analyzer = CoverageAnalyzer()

    summary = analyzer.summary(CoverageReport())

    assert summary["targets"] == 0
    assert summary["average"] == 0.0
    assert summary["highest"] is None


def test_summary_populated():
    analyzer = CoverageAnalyzer()

    report = CoverageReport(
        targets=[
            CoverageTarget(
                name="module",
                coverage=100.0,
            )
        ]
    )

    summary = analyzer.summary(report)

    assert summary["targets"] == 1
    assert summary["average"] == 100.0
    assert summary["highest"] == 100.0


def test_clear():
    analyzer = CoverageAnalyzer()

    report = CoverageReport(
        targets=[
            CoverageTarget(
                name="x",
                coverage=50.0,
            )
        ]
    )

    analyzer.clear(report)

    assert report.targets == []


def test_coverage_target_dataclass():
    target = CoverageTarget(
        name="demo",
        coverage=95.0,
    )

    assert target.name == "demo"
    assert target.coverage == 95.0


def test_coverage_report_dataclass():
    report = CoverageReport()

    assert report.targets == []
