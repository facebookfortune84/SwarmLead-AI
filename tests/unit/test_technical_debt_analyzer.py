from core.orchestration.technical_debt_analyzer import (
    DebtItem,
    DebtReport,
    TechnicalDebtAnalyzer,
)


def test_analyze_empty():
    analyzer = TechnicalDebtAnalyzer()

    report = analyzer.analyze([])

    assert report.items == []


def test_analyze_populated():
    analyzer = TechnicalDebtAnalyzer()

    report = analyzer.analyze(
        [
            DebtItem(
                component="api",
                description="todo",
                weight=5,
            )
        ]
    )

    assert len(report.items) == 1


def test_total_weight():
    analyzer = TechnicalDebtAnalyzer()

    report = DebtReport(
        items=[
            DebtItem(
                component="a",
                description="x",
                weight=2,
            ),
            DebtItem(
                component="b",
                description="y",
                weight=3,
            ),
        ]
    )

    assert analyzer.total_weight(report) == 5


def test_highest_priority_none():
    analyzer = TechnicalDebtAnalyzer()

    assert analyzer.highest_priority(DebtReport()) is None


def test_highest_priority():
    analyzer = TechnicalDebtAnalyzer()

    report = DebtReport(
        items=[
            DebtItem(
                component="low",
                description="x",
                weight=1,
            ),
            DebtItem(
                component="high",
                description="y",
                weight=10,
            ),
        ]
    )

    result = analyzer.highest_priority(report)

    assert result.component == "high"


def test_item_count():
    analyzer = TechnicalDebtAnalyzer()

    report = DebtReport(
        items=[
            DebtItem(
                component="a",
                description="x",
                weight=1,
            )
        ]
    )

    assert analyzer.item_count(report) == 1


def test_debt_score_empty():
    analyzer = TechnicalDebtAnalyzer()

    assert analyzer.debt_score(DebtReport()) == 0.0


def test_debt_score():
    analyzer = TechnicalDebtAnalyzer()

    report = DebtReport(
        items=[
            DebtItem(
                component="a",
                description="x",
                weight=2,
            ),
            DebtItem(
                component="b",
                description="y",
                weight=4,
            ),
        ]
    )

    assert analyzer.debt_score(report) == 3.0


def test_summary_empty():
    analyzer = TechnicalDebtAnalyzer()

    summary = analyzer.summary(DebtReport())

    assert summary["items"] == 0
    assert summary["weight"] == 0
    assert summary["score"] == 0.0
    assert summary["highest"] is None


def test_summary_populated():
    analyzer = TechnicalDebtAnalyzer()

    report = DebtReport(
        items=[
            DebtItem(
                component="api",
                description="x",
                weight=5,
            )
        ]
    )

    summary = analyzer.summary(report)

    assert summary["items"] == 1
    assert summary["weight"] == 5
    assert summary["score"] == 5.0
    assert summary["highest"] == "api"


def test_clear():
    analyzer = TechnicalDebtAnalyzer()

    report = DebtReport(
        items=[
            DebtItem(
                component="x",
                description="y",
                weight=1,
            )
        ]
    )

    analyzer.clear(report)

    assert report.items == []


def test_debt_item_dataclass():
    item = DebtItem(
        component="api",
        description="refactor",
        weight=3,
    )

    assert item.component == "api"
    assert item.description == "refactor"
    assert item.weight == 3


def test_debt_report_dataclass():
    report = DebtReport()

    assert report.items == []
