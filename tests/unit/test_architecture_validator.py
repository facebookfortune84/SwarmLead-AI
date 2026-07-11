from core.orchestration.architecture_validator import (
    ArchitectureIssue,
    ArchitectureReport,
    ArchitectureValidator,
)


def test_validate_healthy():
    validator = ArchitectureValidator()

    report = validator.validate(
        [
            "api",
            "services",
        ],
        [
            "api",
        ],
    )

    assert report.issues == []


def test_validate_missing_component():
    validator = ArchitectureValidator()

    report = validator.validate(
        [
            "api",
        ],
        [
            "api",
            "db",
        ],
    )

    assert len(report.issues) == 1

    assert report.issues[0].component == "db"


def test_issue_count():
    validator = ArchitectureValidator()

    report = ArchitectureReport(
        issues=[
            ArchitectureIssue(
                component="api",
                message="x",
                severity="critical",
            )
        ]
    )

    assert validator.issue_count(report) == 1


def test_critical_issues():
    validator = ArchitectureValidator()

    report = ArchitectureReport(
        issues=[
            ArchitectureIssue(
                component="a",
                message="x",
                severity="critical",
            ),
            ArchitectureIssue(
                component="b",
                message="y",
                severity="warning",
            ),
        ]
    )

    assert len(validator.critical_issues(report)) == 1


def test_has_issues_true():
    validator = ArchitectureValidator()

    report = ArchitectureReport(
        issues=[
            ArchitectureIssue(
                component="x",
                message="y",
                severity="critical",
            )
        ]
    )

    assert validator.has_issues(report) is True


def test_has_issues_false():
    validator = ArchitectureValidator()

    assert validator.has_issues(ArchitectureReport()) is False


def test_healthy_true():
    validator = ArchitectureValidator()

    assert validator.healthy(ArchitectureReport()) is True


def test_healthy_false():
    validator = ArchitectureValidator()

    report = ArchitectureReport(
        issues=[
            ArchitectureIssue(
                component="x",
                message="y",
                severity="critical",
            )
        ]
    )

    assert validator.healthy(report) is False


def test_summary_empty():
    validator = ArchitectureValidator()

    summary = validator.summary(ArchitectureReport())

    assert summary["issues"] == 0
    assert summary["critical"] == 0
    assert summary["healthy"] is True


def test_summary_populated():
    validator = ArchitectureValidator()

    report = ArchitectureReport(
        issues=[
            ArchitectureIssue(
                component="db",
                message="missing",
                severity="critical",
            )
        ]
    )

    summary = validator.summary(report)

    assert summary["issues"] == 1
    assert summary["critical"] == 1
    assert summary["healthy"] is False


def test_clear():
    validator = ArchitectureValidator()

    report = ArchitectureReport(
        issues=[
            ArchitectureIssue(
                component="db",
                message="missing",
                severity="critical",
            )
        ]
    )

    validator.clear(report)

    assert report.issues == []


def test_architecture_issue_dataclass():
    issue = ArchitectureIssue(
        component="api",
        message="missing",
        severity="critical",
    )

    assert issue.component == "api"
    assert issue.message == "missing"
    assert issue.severity == "critical"


def test_architecture_report_dataclass():
    report = ArchitectureReport()

    assert report.issues == []
