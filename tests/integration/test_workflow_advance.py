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


def test_workflow_advance():

    init_db()

    db = SessionLocal()

    try:
        service = WorkflowService(db)

        workflow = service.create_workflow(
            name="Advance Workflow",
            steps=[
                {
                    "step_name": "Step 1",
                    "step_type": "ticket",
                },
                {
                    "step_name": "Step 2",
                    "step_type": "ticket",
                },
            ],
        )

        service.start_workflow(workflow.id)

        updated = service.advance_workflow(workflow.id)

        assert updated is not None

    finally:
        db.close()
