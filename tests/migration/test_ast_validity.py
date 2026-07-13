"""
Migration Validation

Ensures every generated migration artifact is valid Python
and can be parsed by the AST.

This catches:

- broken import rewrites
- malformed model generation
- indentation failures
- accidental syntax regressions
"""

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

STATE_FILE = ROOT / "migration_state.json"


def load_state():

    assert STATE_FILE.exists(), f"Missing migration state file:\n{STATE_FILE}"

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    generated = state.get("generated_files", [])

    assert isinstance(
        generated,
        list,
    )

    return generated


def test_all_generated_files_parse():

    generated_files = load_state()

    failures = []

    for relative_path in generated_files:
        file_path = ROOT / relative_path

        if not file_path.exists():
            failures.append(f"MISSING FILE: {relative_path}")

            continue

        try:
            ast.parse(
                file_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )

        except Exception as exc:
            failures.append(f"{relative_path}: {exc}")

    assert not failures, "\n\n".join(failures)


def test_generated_files_are_python():

    generated_files = load_state()

    non_python = []

    for relative_path in generated_files:
        if not relative_path.endswith(".py"):
            non_python.append(relative_path)

    assert not non_python, "\n".join(non_python)


def test_generated_files_exist_before_ast_parse():

    generated_files = load_state()

    missing = []

    for relative_path in generated_files:
        file_path = ROOT / relative_path

        if not file_path.exists():
            missing.append(relative_path)

    assert not missing, "\n".join(missing)
