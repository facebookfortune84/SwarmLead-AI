"""
Migration Validation

Verify migrated files contain no unexpected backend imports.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

STATE_FILE = ROOT / "migration_state.json"


ALLOWED_BACKEND_REFERENCES = {
    "backend.core.factory",
    "backend.db.linear_engine",
    "backend.orchestration.box_deployer",
    "backend.replicator",
}


ALLOWED_CELERY_REFERENCES = {
    "backend.tasks.ticket_tasks",
    "backend.tasks.notification_tasks",
    "backend.tasks.workflow_tasks",
}


def load_generated_files():

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    return state["generated_files"]


def test_no_backend_imports_remain():

    violations = []

    for relative_path in load_generated_files():
        file_path = ROOT / relative_path

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if "backend." not in line:
                continue

            if any(item in line for item in ALLOWED_BACKEND_REFERENCES):
                continue

            if any(item in line for item in ALLOWED_CELERY_REFERENCES):
                continue

            violations.append(f"{relative_path}:{line_number}: {line.strip()}")

    assert not violations, "\n\n".join(violations)
