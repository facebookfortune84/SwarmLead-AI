"""
migration_config.py

Central migration configuration.

ALL migration scripts MUST import from this file.

Do NOT hardcode:

    SOURCE_ROOT
    TARGET_ROOT
    BACKUP_ROOT
    REPORT_ROOT

inside migration scripts.

This file is the single source of truth.
"""

from pathlib import Path

# ============================================================
# SOURCE REPOSITORY
# ============================================================

SOURCE_ROOT = Path(r"C:\SwarmEnterprise-v2")

BACKEND_ROOT = SOURCE_ROOT / "backend"

# ============================================================
# TARGET REPOSITORY
# ============================================================

TARGET_ROOT = Path(r"C:\SwarmLead-AI")

# ============================================================
# BACKUPS
# ============================================================

BACKUP_ROOT = TARGET_ROOT / "backups"

BACKUP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

COPY_BACKUP_ROOT = BACKUP_ROOT / "copy_phase"

IMPORT_BACKUP_ROOT = BACKUP_ROOT / "import_rewrite"

MODEL_BACKUP_ROOT = BACKUP_ROOT / "model_split"

ENGINE_BACKUP_ROOT = BACKUP_ROOT / "migration_engine"

for path in (
    COPY_BACKUP_ROOT,
    IMPORT_BACKUP_ROOT,
    MODEL_BACKUP_ROOT,
    ENGINE_BACKUP_ROOT,
):
    path.mkdir(
        parents=True,
        exist_ok=True,
    )

# ============================================================
# REPORTS
# ============================================================

REPORT_ROOT = TARGET_ROOT / "migration_reports"

REPORT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

# ============================================================
# STATE TRACKING
# ============================================================

STATE_FILE = TARGET_ROOT / "migration_state.json"

# ============================================================
# MANIFEST
# ============================================================

MANIFEST_FILE = TARGET_ROOT / "scripts" / "migration_manifest.yaml"

# ============================================================
# MODEL SOURCE
# ============================================================

MODEL_SOURCE_FILE = BACKEND_ROOT / "db" / "models.py"

# ============================================================
# ENCODING FIXES
# ============================================================

ENCODING_REPLACEMENTS = {
    "â€”": "-",
    "â€“": "-",
    "â€¢": "*",
    "â†’": "->",
    "â‰¥": ">=",
    "â‰¤": "<=",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€™": "'",
    "\ufeff": "",
}

# ============================================================
# SAFETY
# ============================================================

if SOURCE_ROOT.resolve() == TARGET_ROOT.resolve():
    raise RuntimeError("SOURCE_ROOT and TARGET_ROOT cannot be identical.")

if not SOURCE_ROOT.exists():
    raise RuntimeError(f"Source repository does not exist:\n{SOURCE_ROOT}")

if not BACKEND_ROOT.exists():
    raise RuntimeError(f"Backend directory does not exist:\n{BACKEND_ROOT}")

if not TARGET_ROOT.exists():
    raise RuntimeError(f"Target repository does not exist:\n{TARGET_ROOT}")

# ============================================================
# BUILD SETTINGS
# ============================================================

DEFAULT_DRY_RUN = True

TRACK_GENERATED_FILES = True

ALLOW_DELETE_PREVIOUS_GENERATED = True

ALLOW_DELETE_UNKNOWN_FILES = False

OVERWRITE_EXISTING_FILES = False

CREATE_BACKUPS_BEFORE_OVERWRITE = True

VALIDATE_AST_BEFORE_WRITE = True

FIX_ENCODING_DURING_COPY = True

GENERATE_REPORTS = True

# ============================================================
# MIGRATION VERSION
# ============================================================

MIGRATION_VERSION = "v3"
