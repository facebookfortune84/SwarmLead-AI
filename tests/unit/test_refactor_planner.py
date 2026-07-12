from core.orchestration.refactor_planner import (
    RefactorPlan,
    RefactorPlanner,
    RefactorTask,
)


def test_create_plan():

    planner = RefactorPlanner()

    plan = planner.create_plan(
        [
            "agent_manager",
            "task_router",
        ]
    )

    assert len(plan.tasks) == 2


def test_task_count():

    planner = RefactorPlanner()

    plan = planner.create_plan(["component"])

    assert planner.task_count(plan) == 1


def test_highest_priority_empty():

    planner = RefactorPlanner()

    plan = RefactorPlan()

    assert planner.highest_priority(plan) is None


def test_highest_priority():

    planner = RefactorPlanner()

    plan = planner.create_plan(["component"])

    assert planner.highest_priority(plan) is not None


def test_summary():

    planner = RefactorPlanner()

    plan = planner.create_plan(["component"])

    summary = planner.summary(plan)

    assert summary["tasks"] == 1


def test_clear():

    planner = RefactorPlanner()

    plan = planner.create_plan(["component"])

    planner.clear(plan)

    assert plan.tasks == []


def test_refactor_task_dataclass():

    task = RefactorTask(
        component="demo",
        reason="cleanup",
        priority=1,
    )

    assert task.component == "demo"
    assert task.reason == "cleanup"
    assert task.priority == 1


def test_refactor_plan_dataclass():

    plan = RefactorPlan()

    assert plan.tasks == []
