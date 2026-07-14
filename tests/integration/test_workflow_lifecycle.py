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


def test_workflow_start():

    init_db()

    db = SessionLocal()

    try:
        svc = WorkflowService(db)

        workflow = svc.create_workflow(
            name="Lifecycle Test",
            steps=[
                {
                    "step_name": "Step 1",
                    "step_type": "ticket",
                }
            ],
        )

        started = svc.start_workflow(workflow.id)

        assert started is not None

    finally:
        db.close()
