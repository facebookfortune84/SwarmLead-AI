from core.orchestration.repair_agent import (
    RepairAction,
    RepairAgent,
    RepairResult,
)


def test_suggest_fix():
    agent = RepairAgent()

    action = agent.suggest_fix(
        target="file.py",
        issue="missing import",
    )

    assert action.target == "file.py"
    assert "missing import" in action.description


def test_repair_with_actions():
    agent = RepairAgent()

    action = RepairAction(
        description="fix",
        target="file.py",
    )

    result = agent.repair(actions=[action])

    assert result.repaired is True


def test_repair_without_actions():
    agent = RepairAgent()

    result = agent.repair()

    assert result.repaired is False
    assert result.actions == []


def test_action_count():
    agent = RepairAgent()

    result = agent.repair(
        actions=[
            RepairAction(
                description="a",
                target="one",
            ),
            RepairAction(
                description="b",
                target="two",
            ),
        ]
    )

    assert agent.action_count(result) == 2


def test_was_repaired_true():
    agent = RepairAgent()

    result = agent.repair(
        actions=[
            RepairAction(
                description="a",
                target="one",
            )
        ]
    )

    assert agent.was_repaired(result) is True


def test_was_repaired_false():
    agent = RepairAgent()

    result = agent.repair()

    assert agent.was_repaired(result) is False


def test_summary():
    agent = RepairAgent()

    action = RepairAction(
        description="fix",
        target="file.py",
    )

    result = agent.repair(actions=[action])

    summary = agent.summary(result)

    assert summary["repaired"] is True
    assert summary["action_count"] == 1
    assert summary["targets"] == ["file.py"]


def test_merge_actions():
    agent = RepairAgent()

    first = [
        RepairAction(
            description="a",
            target="one",
        )
    ]

    second = [
        RepairAction(
            description="b",
            target="two",
        )
    ]

    merged = agent.merge_actions(
        first,
        second,
    )

    assert len(merged) == 2
    assert merged[0].target == "one"
    assert merged[1].target == "two"


def test_repair_metadata():
    agent = RepairAgent()

    result = agent.repair(
        actions=[
            RepairAction(
                description="fix",
                target="x",
            )
        ],
        metadata={"branch": "main"},
    )

    assert result.metadata["branch"] == "main"


def test_repair_action_dataclass():
    action = RepairAction(
        description="demo",
        target="demo.py",
    )

    assert action.description == "demo"
    assert action.target == "demo.py"


def test_repair_result_dataclass():
    result = RepairResult(
        repaired=True,
    )

    assert result.repaired is True
    assert result.actions == []
    assert result.metadata == {}
