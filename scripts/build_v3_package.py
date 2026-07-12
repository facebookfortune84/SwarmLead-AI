"""
build_v3_package.py

SwarmEnterprise v2 -> SwarmLead-AI migration engine

Usage
-----

Dry Run

    python scripts/build_v3_package.py

Apply

    python scripts/build_v3_package.py --apply

Apply + overwrite generated targets

    python scripts/build_v3_package.py --apply --force
"""

import argparse
import ast
import json
import shutil
from datetime import datetime
from pathlib import Path

from scripts.migration_config import (
    BACKEND_ROOT,
    BACKUP_ROOT,
    ENCODING_REPLACEMENTS,
    MODEL_SOURCE_FILE,
    REPORT_ROOT,
    STATE_FILE,
    TARGET_ROOT,
)

# ============================================================
# MODEL CONFIG
# ============================================================

MODEL_TARGETS = {
    "User": "core/models/user.py",
    "APIKey": "core/models/api_key.py",
    "Lead": "core/models/lead.py",
    "UsageEvent": "core/models/usage.py",
    "Deployment": "core/models/deployment.py",
    "CompanyTenant": "core/models/tenant.py",
    "Notification": "core/models/notification.py",
    "Message": "core/models/message.py",
    "MessageThread": "core/models/message_thread.py",
    "Workflow": "core/models/workflow.py",
    "WorkflowStep": "core/models/workflow_step.py",
    "Ticket": "core/models/ticket.py",
    "TicketHistory": "core/models/ticket_history.py",
    "TicketComment": "core/models/ticket_comment.py",
}

# ============================================================
# SOURCE VALIDATION
# ============================================================


def validate_sources():
    """
    Validate all migration inputs before any work begins.

    Checks:
    - models.py exists
    - every source file in COPY_FILES exists
    - models.py parses successfully
    - reports validation summary

    Raises:
        RuntimeError if validation fails
    """

    log("")
    log("VALIDATION PHASE")

    errors = []

    #
    # Validate model source
    #
    if not MODEL_SOURCE_FILE.exists():
        errors.append(f"Missing model source: {MODEL_SOURCE_FILE}")

    else:
        log(f"MODEL SOURCE OK: {MODEL_SOURCE_FILE}")

        try:
            source_code = MODEL_SOURCE_FILE.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            ast.parse(source_code)

            log("MODEL SOURCE AST VALID")

        except Exception as exc:
            errors.append(f"Unable to parse models.py: {exc}")

    #
    # Validate copy sources
    #
    for source_rel, target_rel in COPY_FILES:
        source_file = BACKEND_ROOT / source_rel

        if not source_file.exists():
            errors.append(f"Missing source file: {source_rel}")

        else:
            log(f"SOURCE OK: {source_rel}")

    #
    # Validate all target model classes exist
    #
    if MODEL_SOURCE_FILE.exists():
        try:
            source_code = MODEL_SOURCE_FILE.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            for model_name in MODEL_TARGETS:
                block = extract_class(
                    source_code,
                    model_name,
                )

                if block is None:
                    errors.append(f"Model not found in models.py: {model_name}")

                else:
                    log(f"MODEL FOUND: {model_name}")

        except Exception as exc:
            errors.append(f"Model validation failure: {exc}")

    #
    # Final validation result
    #
    if errors:
        log("")
        log("VALIDATION FAILED")

        for error in errors:
            log(f"ERROR: {error}")

        raise RuntimeError("\nMigration preflight validation failed.\n\n".join(errors))

    log("")
    log("VALIDATION PASSED")


# ============================================================
# COPY CONFIG
# ============================================================

COPY_FILES = [
    ("auth/jwt_handler.py", "interfaces/api/auth/jwt_handler.py"),
    ("auth/middleware.py", "interfaces/api/auth/middleware.py"),
    ("auth/permissions.py", "interfaces/api/auth/permissions.py"),
    ("auth/user_service.py", "interfaces/api/auth/user_service.py"),
    ("api/auth.py", "interfaces/api/routers/auth.py"),
    ("api/users.py", "interfaces/api/routers/users.py"),
    ("api/tenants.py", "interfaces/api/routers/tenants.py"),
    ("api/leads.py", "interfaces/api/routers/leads.py"),
    ("api/outreach.py", "interfaces/api/routers/outreach.py"),
    ("api/notifications.py", "interfaces/api/routers/notifications.py"),
    ("api/workflows.py", "interfaces/api/routers/workflows.py"),
    ("api/payments.py", "interfaces/api/routers/payments.py"),
    ("api/usage.py", "interfaces/api/routers/usage.py"),
    ("services/notification_service.py", "core/services/notification_service.py"),
    ("services/workflow_service.py", "core/services/workflow_service.py"),
    ("services/payments.py", "core/services/payment_service.py"),
    ("services/event_bus.py", "core/events/event_bus.py"),
    ("storage/file_manager.py", "core/storage/file_manager.py"),
    ("storage/s3_client.py", "core/storage/s3_client.py"),
    ("tasks/notification_tasks.py", "infrastructure/celery/notification_tasks.py"),
    ("tasks/ticket_tasks.py", "infrastructure/celery/ticket_tasks.py"),
    ("tasks/workflow_tasks.py", "infrastructure/celery/workflow_tasks.py"),
    ("task_queue.py", "infrastructure/queue/task_queue.py"),
    ("celery_app.py", "infrastructure/celery/celery_app.py"),
    ("api/crm_sync.py", "interfaces/api/routers/crm.py"),
    ("api/reporting.py", "interfaces/api/routers/reporting.py"),
    ("core/tenants.py", "core/services/tenant_service.py"),
    ("api/ws.py", "interfaces/api/ws.py"),
]

# ============================================================
# REPORTING
# ============================================================

REPORT = []


def log(message: str):
    print(message)
    REPORT.append(message)


# ============================================================
# STATE MANAGEMENT
# ============================================================


def load_state():
    """
    Load migration state from disk.

    Returns a valid state structure even if the file
    is missing or corrupted.
    """

    if not STATE_FILE.exists():
        return {"generated_files": []}

    try:
        state = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8",
            )
        )

        return validate_state(state)

    except Exception as exc:
        print(f"WARNING: Unable to read migration state: {exc}")

        return {"generated_files": []}


def save_state(state):
    """
    Normalize and persist migration state.
    """

    state = validate_state(state)

    STATE_FILE.write_text(
        json.dumps(
            state,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


# ============================================================
# STATE VALIDATION
# ============================================================


def validate_state(state):
    """
    Validate and normalize migration state.

    Returns:
        normalized state dictionary

    Raises:
        RuntimeError if state structure is invalid
    """

    if not isinstance(state, dict):
        raise RuntimeError("Migration state must be a dictionary.")

    if "generated_files" not in state:
        state["generated_files"] = []

    if not isinstance(
        state["generated_files"],
        list,
    ):
        raise RuntimeError("generated_files must be a list.")

    #
    # Remove duplicates
    #
    state["generated_files"] = sorted(list(set(state["generated_files"])))

    #
    # Normalize path separators
    #
    normalized = []

    for item in state["generated_files"]:
        if not isinstance(item, str):
            continue

        normalized.append(item.replace("\\", "/"))

    state["generated_files"] = sorted(list(set(normalized)))

    return state


# ============================================================
# TARGET VALIDATION
# ============================================================


def validate_target_root():
    """
    Verify target repository structure exists before migration.
    """

    if not TARGET_ROOT.exists():
        raise RuntimeError(f"Target root does not exist:\n{TARGET_ROOT}")

    required_dirs = [
        TARGET_ROOT / "core",
        TARGET_ROOT / "scripts",
    ]

    for directory in required_dirs:
        if not directory.exists():
            raise RuntimeError(f"Required directory missing:\n{directory}")


# ============================================================
# BACKUPS
# ============================================================


def backup_file(path: Path):

    backup_root = BACKUP_ROOT / "migration_engine"

    relative = path.relative_to(TARGET_ROOT)

    backup_path = backup_root / relative

    backup_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        path,
        backup_path,
    )

    return backup_path


# ============================================================
# CLEANUP
# ============================================================


def cleanup_previous_generation(
    state,
    apply_changes,
):

    log("")
    log("CLEANUP PHASE")

    for relative in state["generated_files"]:
        file_path = TARGET_ROOT / relative

        if not file_path.exists():
            continue

        log(f"REMOVE GENERATED {relative}")

        if not apply_changes:
            continue

        try:
            if file_path.is_file():
                file_path.unlink()

            elif file_path.is_dir():
                shutil.rmtree(file_path)

        except Exception as exc:
            log(f"FAILED REMOVE {relative} : {exc}")


# ============================================================
# ENCODING
# ============================================================


def fix_encoding(
    text: str,
):

    updated = text

    for bad, good in ENCODING_REPLACEMENTS.items():
        updated = updated.replace(
            bad,
            good,
        )

    return updated


# ============================================================
# FILE COPY
# ============================================================


def migrate_files(
    state,
    apply_changes,
    force,
):

    log("")
    log("FILE COPY PHASE")

    for source_rel, target_rel in COPY_FILES:
        source_file = BACKEND_ROOT / source_rel

        target_file = TARGET_ROOT / target_rel

        if not source_file.exists():
            log(f"MISSING SOURCE {source_rel}")

            continue

        if target_file.exists() and not force:
            log(f"SKIP EXISTS {target_rel}")

            continue

        log(f"COPY {source_rel} -> {target_rel}")

        if not apply_changes:
            continue

        if target_file.exists():
            backup_file(target_file)

        target_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        text = source_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        text = fix_encoding(text)

        target_file.write_text(
            text,
            encoding="utf-8",
        )

        state["generated_files"].append(
            target_rel.replace(
                "\\",
                "/",
            )
        )


# ============================================================
# AST HELPERS
# ============================================================


def parse_tree(code):

    try:
        return ast.parse(code)

    except SyntaxError as exc:
        raise RuntimeError(f"Model source parse failure:\n{exc}")


def extract_imports(code):

    tree = parse_tree(code)

    imports = []

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            segment = ast.get_source_segment(
                code,
                node,
            )

            if segment:
                imports.append(segment)

    return "\n".join(imports)


def extract_class(
    code,
    class_name,
):

    tree = parse_tree(code)

    for node in tree.body:
        if (
            isinstance(
                node,
                ast.ClassDef,
            )
            and node.name == class_name
        ):
            return ast.get_source_segment(
                code,
                node,
            )

    return None


# ============================================================
# MODEL SPLIT
# ============================================================


def split_models(
    state,
    apply_changes,
    force,
):

    log("")
    log("MODEL SPLIT PHASE")

    if not MODEL_SOURCE_FILE.exists():
        log(f"MISSING MODEL SOURCE {MODEL_SOURCE_FILE}")

        return

    code = MODEL_SOURCE_FILE.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    code = fix_encoding(code)

    imports = extract_imports(code)

    for model_name, target_rel in MODEL_TARGETS.items():
        block = extract_class(
            code,
            model_name,
        )

        if not block:
            log(f"MISSING MODEL {model_name}")

            continue

        generated = imports + "\n\n\n" + block + "\n"

        try:
            ast.parse(generated)

        except SyntaxError as exc:
            log(f"INVALID GENERATED MODEL {model_name}: {exc}")

            continue

        target_path = TARGET_ROOT / target_rel

        if target_path.exists() and not force:
            log(f"SKIP EXISTS {target_rel}")

            continue

        log(f"GENERATE MODEL {target_rel}")

        if not apply_changes:
            continue

        if target_path.exists():
            backup_file(target_path)

        target_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target_path.write_text(
            generated,
            encoding="utf-8",
        )

        state["generated_files"].append(target_rel)


# ============================================================
# MODEL INIT
# ============================================================


def generate_model_init(
    apply_changes,
):

    model_dir = TARGET_ROOT / "core" / "models"

    exports = []

    for class_name, target in MODEL_TARGETS.items():
        module = Path(target).stem

        exports.append(
            (
                module,
                class_name,
            )
        )

    lines = []

    for module, cls in exports:
        lines.append(f"from .{module} import {cls}")

    lines.append("")
    lines.append("__all__ = [")

    for _, cls in exports:
        lines.append(f'    "{cls}",')

    lines.append("]")

    content = "\n".join(lines)

    init_file = model_dir / "__init__.py"

    log("GENERATE core/models/__init__.py")

    if apply_changes:
        init_file.write_text(
            content,
            encoding="utf-8",
        )


# ============================================================
# REPORT
# ============================================================


def write_report():

    report_file = REPORT_ROOT / (
        "migration_report_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S") + ".txt"
    )

    report_file.write_text(
        "\n".join(REPORT),
        encoding="utf-8",
    )

    print()
    print(f"REPORT: {report_file}")


# ============================================================
# MAIN
# ============================================================


def main():

    parser = argparse.ArgumentParser(
        description="SwarmEnterprise v2 -> SwarmLead-AI Migration Engine"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply migration changes",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files",
    )

    args = parser.parse_args()

    print()
    print("=" * 70)
    print("SWARMENTERPRISE V2 -> SWARMLEAD-AI MIGRATION ENGINE")
    print("=" * 70)

    if args.apply:
        print("MODE: APPLY")
        print("FILES WILL BE MODIFIED")

        if args.force:
            print("FORCE MODE ENABLED")

    else:
        print("MODE: DRY RUN")
        print("NO FILES WILL BE MODIFIED")

    print("=" * 70)
    print()

    #
    # Validate inputs
    #
    try:
        validate_sources()

        validate_target_root()

    except Exception as exc:
        print()
        print("=" * 70)
        print("VALIDATION FAILED")
        print("=" * 70)
        print()

        print(str(exc))

        print()

        raise SystemExit(1)

    #
    # Load migration state
    #
    state = validate_state(load_state())

    #
    # Cleanup prior generated artifacts
    #
    cleanup_previous_generation(
        state,
        args.apply,
    )

    #
    # Copy approved files
    #
    migrate_files(
        state,
        args.apply,
        args.force,
    )

    #
    # Split database models
    #
    split_models(
        state,
        args.apply,
        args.force,
    )

    #
    # Generate core/models/__init__.py
    #
    generate_model_init(
        args.apply,
    )

    #
    # Summary
    #
    log("")
    log("SUMMARY")

    log(f"Files Planned: {len(COPY_FILES)}")

    log(f"Models Planned: {len(MODEL_TARGETS)}")

    if args.apply:
        log(f"Generated Files: {len(state['generated_files'])}")

    #
    # Persist migration state
    #
    if args.apply:
        state = validate_state(state)

        save_state(state)

    #
    # Final report
    #
    write_report()

    print()
    print("=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
