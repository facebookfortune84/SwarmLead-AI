from core.orchestration.failure_analyzer import (
    FailureRecord,
    FailureReport,
)
from core.orchestration.improvement_planner import (
    ImprovementPlan,
    ImprovementPlanner,
    ImprovementTask,
)


def test_create_plan_empty():
    planner = ImprovementPlanner()

    plan = planner.create_plan(FailureReport())

    assert plan.tasks == []


def test_create_plan_critical():
    planner = ImprovementPlanner()

    report = FailureReport(
        failures=[
            FailureRecord(
                component="builder",
                message="build failed",
                severity="critical",
            )
        ]
    )

    plan = planner.create_plan(report)

    assert len(plan.tasks) == 1

    assert plan.tasks[0].priority == 1


def test_create_plan_warning():
    planner = ImprovementPlanner()

    report = FailureReport(
        failures=[
            FailureRecord(
                component="reviewer",
                message="warning",
                severity="warning",
            )
        ]
    )

    plan = planner.create_plan(report)

    assert plan.tasks[0].priority == 5


def test_task_count():
    planner = ImprovementPlanner()

    plan = ImprovementPlan(
        tasks=[
            ImprovementTask(
                name="x",
                priority=1,
                reason="y",
            )
        ]
    )

    assert planner.task_count(plan) == 1


def test_highest_priority_none():
    planner = ImprovementPlanner()

    assert planner.highest_priority(ImprovementPlan()) is None


def test_highest_priority():
    planner = ImprovementPlanner()

    plan = ImprovementPlan(
        tasks=[
            ImprovementTask(
                name="low",
                priority=5,
                reason="a",
            ),
            ImprovementTask(
                name="high",
                priority=1,
                reason="b",
            ),
        ]
    )

    task = planner.highest_priority(plan)

    assert task.name == "high"


def test_priorities():
    planner = ImprovementPlanner()

    plan = ImprovementPlan(
        tasks=[
            ImprovementTask(
                name="a",
                priority=1,
                reason="x",
            ),
            ImprovementTask(
                name="b",
                priority=3,
                reason="y",
            ),
        ]
    )

    assert planner.priorities(plan) == [1, 3]


def test_summary_empty():
    planner = ImprovementPlanner()

    summary = planner.summary(ImprovementPlan())

    assert summary["tasks"] == 0
    assert summary["highest_priority"] is None


def test_summary_populated():
    planner = ImprovementPlanner()

    plan = ImprovementPlan(
        tasks=[
            ImprovementTask(
                name="a",
                priority=1,
                reason="x",
            )
        ]
    )

    summary = planner.summary(plan)

    assert summary["tasks"] == 1
    assert summary["highest_priority"] == 1


def test_clear():
    planner = ImprovementPlanner()

    plan = ImprovementPlan(
        tasks=[
            ImprovementTask(
                name="a",
                priority=1,
                reason="x",
            )
        ]
    )

    planner.clear(plan)

    assert plan.tasks == []


def test_improvement_task_dataclass():
    task = ImprovementTask(
        name="demo",
        priority=1,
        reason="reason",
    )

    assert task.name == "demo"
    assert task.priority == 1
    assert task.reason == "reason"


def test_improvement_plan_dataclass():
    plan = ImprovementPlan()

    assert plan.tasks == []
