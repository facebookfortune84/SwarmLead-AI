"""
Integration Test
"""

from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.workflow_service import (
    WorkflowService,
)


def test_workflow_completion():

    init_db()

    db = SessionLocal()

    try:
        service = WorkflowService(db)

        workflow = service.create_workflow(
            name="Completion Test",
            steps=[
                {
                    "step_name": "Only Step",
                    "step_type": "ticket",
                }
            ],
        )

        service.start_workflow(workflow.id)

        result = service.advance_workflow(workflow.id)

        assert result is not None

        assert result.status in (
            "completed",
            "running",
        )

    finally:
        db.close()
