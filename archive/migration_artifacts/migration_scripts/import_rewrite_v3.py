"""
import_rewrite_v3.py

SwarmEnterprise v2 -> SwarmLead-AI

Phase 2 Import Rewrite Engine

Features
--------
- Dry run by default
- Apply mode
- Migration-state driven
- Only touches generated files
- Backs up modified files
- Import-only rewriting
- Model-symbol-aware rewriting
- Outreach model rewriting
- AST validation before write
- Full repository AST validation
- Rewrite manifest generation
- Unresolved dependency reporting
- Metrics and reporting

Usage
-----

Dry Run

    python -m scripts.import_rewrite_v3

Apply

    python -m scripts.import_rewrite_v3 --apply
"""

import argparse
import ast
import json
import shutil
from pathlib import Path

from scripts.migration_config import (
    BACKUP_ROOT,
    REPORT_ROOT,
    STATE_FILE,
    TARGET_ROOT,
)

# ============================================================
# GLOBALS
# ============================================================

REPORT = []

MANIFEST: dict[str, list[dict[str, str]]] = {}

UNRESOLVED_IMPORTS = set()

METRICS = {
    "files_scanned": 0,
    "files_rewritten": 0,
    "imports_rewritten": 0,
    "syntax_failures": 0,
}

# ============================================================
# REWRITE MAPS
# ============================================================

IMPORT_REWRITES = {
    "backend.db.base": "core.persistence.base",
    "backend.db.session": "core.persistence.session",
    "backend.db.ticket_history": "core.persistence.ticket_history",
    "backend.auth.jwt_handler": "interfaces.api.auth.jwt_handler",
    "backend.auth.middleware": "interfaces.api.auth.middleware",
    "backend.auth.user_service": "interfaces.api.auth.user_service",
    "backend.auth.permissions": "interfaces.api.auth.permissions",
    "backend.api.ws": "interfaces.api.ws",
    "backend.services.notification_service": "core.services.notification_service",
    "backend.services.workflow_service": "core.services.workflow_service",
    "backend.services.ticket_service": "core.services.ticket_service",
    "backend.services.event_bus": "core.events.event_bus",
    "backend.tasks.notification_tasks": "infrastructure.celery.notification_tasks",
    "backend.tasks.ticket_tasks": "infrastructure.celery.ticket_tasks",
    "backend.tasks.workflow_tasks": "infrastructure.celery.workflow_tasks",
    "backend.celery_app": "infrastructure.celery.celery_app",
    "backend.core.tenants": "core.services.tenant_service",
    "backend.db.linear_engine": "core.persistence.linear_engine",
}

# ============================================================
# MODEL MAP
# ============================================================

MODEL_IMPORT_MAP = {
    "User": "core.models.user",
    "APIKey": "core.models.api_key",
    "Lead": "core.models.lead",
    "UsageEvent": "core.models.usage",
    "Deployment": "core.models.deployment",
    "CompanyTenant": "core.models.tenant",
    "Notification": "core.models.notification",
    "Message": "core.models.message",
    "MessageThread": "core.models.message_thread",
    "Workflow": "core.models.workflow",
    "WorkflowStep": "core.models.workflow_step",
    "Ticket": "core.models.ticket",
    "TicketHistory": "core.models.ticket_history",
    "TicketComment": "core.models.ticket_comment",
    "LeadTimeline": "core.models.outreach",
}

# ============================================================
# IMPORTS TO REPORT ONLY
# ============================================================

UNRESOLVED_TARGETS = {
    "backend.orchestration.box_deployer",
    "backend.core.factory",
    "backend.replicator",
    "backend.db.linear_engine",
}

# ============================================================
# HELPERS
# ============================================================


def log(message):
    print(message)
    REPORT.append(message)


# ============================================================
# STATE
# ============================================================


def load_state():

    if not STATE_FILE.exists():
        raise RuntimeError(f"Missing migration state file:\n{STATE_FILE}")

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    if not isinstance(state, dict):
        raise RuntimeError("Invalid migration state format.")

    generated = state.get(
        "generated_files",
        [],
    )

    if not isinstance(generated, list):
        raise RuntimeError("generated_files must be a list.")

    state["generated_files"] = sorted(list(set(generated)))

    return state


# ============================================================
# BACKUPS
# ============================================================


def backup_file(path: Path):

    backup_root = BACKUP_ROOT / "import_rewrite"

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


# ============================================================
# VALIDATION
# ============================================================


def validate_python(code):

    ast.parse(code)


def validate_repository():

    failures = []

    state = load_state()

    for relative in state["generated_files"]:
        file_path = TARGET_ROOT / relative

        if not file_path.exists():
            continue

        try:
            ast.parse(
                file_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )

        except Exception as exc:
            failures.append(f"{relative}: {exc}")

    if failures:
        raise RuntimeError("Repository validation failed:\n" + "\n".join(failures))


# ============================================================
# UNRESOLVED TRACKING
# ============================================================


def track_unresolved(text):

    for dependency in UNRESOLVED_TARGETS:
        if dependency in text:
            UNRESOLVED_IMPORTS.add(dependency)


# ============================================================
# MANIFEST
# ============================================================


def add_manifest_entry(
    relative_path,
    old,
    new,
):

    MANIFEST.setdefault(
        relative_path,
        [],
    )

    MANIFEST[relative_path].append(
        {
            "old": old,
            "new": new,
        }
    )


# ============================================================
# REWRITE ENGINE
# ============================================================


def rewrite_source(
    text,
    relative_path,
):

    lines = text.splitlines()

    output = []

    rewrites = set()

    for line in lines:
        updated = line

        leading_ws = updated[: len(updated) - len(updated.lstrip())]

        stripped = updated.strip()

        if stripped.startswith("from "):
            #
            # backend.db.models
            #
            if stripped.startswith("from backend.db.models import "):
                import_part = stripped.split(
                    "import",
                    1,
                )[1].strip()

                symbols = [x.strip() for x in import_part.split(",")]

                generated = []

                unresolved = []

                for symbol in symbols:
                    target_module = MODEL_IMPORT_MAP.get(symbol)

                    if target_module:
                        generated.append(leading_ws + f"from {target_module} import {symbol}")

                        rewrites.add(
                            (
                                f"backend.db.models.{symbol}",
                                f"{target_module}.{symbol}",
                            )
                        )

                    else:
                        unresolved.append(symbol)

                output.extend(generated)

                if unresolved:
                    output.append(line)

                continue

            #
            # outreach
            #
            if stripped.startswith("from backend.db.models_outreach import "):
                output.append(leading_ws + "from core.models.outreach import LeadTimeline")

                rewrites.add(
                    (
                        "backend.db.models_outreach.LeadTimeline",
                        "core.models.outreach.LeadTimeline",
                    )
                )

                continue

            handled = False

            for old, new in IMPORT_REWRITES.items():
                prefix = f"from {old} import "

                if stripped.startswith(prefix):
                    output.append(
                        updated.replace(
                            old,
                            new,
                            1,
                        )
                    )

                    rewrites.add(
                        (
                            old,
                            new,
                        )
                    )

                    handled = True

                    break

            if handled:
                continue

        #
        # direct imports
        #
        if stripped.startswith("import "):
            handled = False

            for old, new in IMPORT_REWRITES.items():
                if stripped == f"import {old}":
                    output.append(leading_ws + f"import {new}")

                    rewrites.add(
                        (
                            old,
                            new,
                        )
                    )

                    handled = True

                    break

            if handled:
                continue

        #
        # leave strings untouched
        #
        output.append(updated)

    rewritten = "\n".join(output)

    validate_python(rewritten)

    for old, new in sorted(rewrites):
        log(f"{relative_path}: {old} -> {new}")

        METRICS["imports_rewritten"] += 1

        add_manifest_entry(
            relative_path,
            old,
            new,
        )

    return rewritten


# ============================================================
# FILE PROCESSING
# ============================================================


def process_file(
    path,
    apply_changes,
):

    METRICS["files_scanned"] += 1

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    track_unresolved(text)

    relative = str(path.relative_to(TARGET_ROOT))

    rewritten = rewrite_source(
        text,
        relative,
    )

    if rewritten == text:
        return

    METRICS["files_rewritten"] += 1

    log(f"REWRITE {relative}")

    if not apply_changes:
        return

    backup_file(path)

    path.write_text(
        rewritten,
        encoding="utf-8",
    )


# ============================================================
# REPORTS
# ============================================================


def write_report():

    report_file = REPORT_ROOT / "import_rewrite_report.txt"

    REPORT.append("")
    REPORT.append("SUMMARY")
    REPORT.append(
        json.dumps(
            METRICS,
            indent=2,
        )
    )

    report_file.write_text(
        "\n".join(REPORT),
        encoding="utf-8",
    )


def write_unresolved_report():

    report_file = REPORT_ROOT / "unresolved_imports.txt"

    report_file.write_text(
        "\n".join(sorted(UNRESOLVED_IMPORTS)),
        encoding="utf-8",
    )


def write_manifest():

    manifest_file = REPORT_ROOT / "rewrite_manifest.json"

    manifest_file.write_text(
        json.dumps(
            MANIFEST,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


# ============================================================
# MAIN
# ============================================================


def main():

    parser = argparse.ArgumentParser(description="SwarmLead Import Rewrite Engine")

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply rewrites",
    )

    args = parser.parse_args()

    print()
    print("=" * 70)

    if args.apply:
        print("IMPORT REWRITE V3.1 - APPLY")

    else:
        print("IMPORT REWRITE V3.1 - DRY RUN")

    print("=" * 70)
    print()

    state = load_state()

    for relative in state["generated_files"]:
        file_path = TARGET_ROOT / relative

        if not file_path.exists():
            continue

        try:
            process_file(
                file_path,
                args.apply,
            )

        except Exception as exc:
            METRICS["syntax_failures"] += 1

            log(f"FAILED {relative}: {exc}")

    if args.apply:
        validate_repository()

    write_report()

    write_unresolved_report()

    write_manifest()

    print()
    print("=" * 70)
    print("IMPORT REWRITE COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
