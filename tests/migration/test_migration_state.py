"""
Migration State Validation

Ensures migration_state.json remains
accurate and consistent.

This catches:

- stale state entries
- duplicate state entries
- deleted generated files
- corrupt state structure
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

STATE_FILE = ROOT / "migration_state.json"


def load_state():

    assert STATE_FILE.exists(), f"Missing migration state file:\n{STATE_FILE}"

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    return state


def test_state_is_dictionary():

    state = load_state()

    assert isinstance(
        state,
        dict,
    )


def test_generated_files_key_exists():

    state = load_state()

    assert "generated_files" in state


def test_generated_files_is_list():

    state = load_state()

    assert isinstance(
        state["generated_files"],
        list,
    )


def test_generated_files_not_empty():

    state = load_state()

    assert len(state["generated_files"]) > 0


def test_no_duplicate_generated_files():

    state = load_state()

    generated = state["generated_files"]

    assert len(generated) == len(set(generated))


def test_every_generated_file_exists():

    state = load_state()

    missing = []

    for relative_path in state["generated_files"]:
        file_path = ROOT / relative_path

        if not file_path.exists():
            missing.append(relative_path)

    assert not missing, "\n".join(missing)


def test_generated_files_use_forward_slashes():

    state = load_state()

    invalid = []

    for relative_path in state["generated_files"]:
        if "\\" in relative_path:
            invalid.append(relative_path)

    assert not invalid, "\n".join(invalid)


def test_generated_files_are_relative_paths():

    state = load_state()

    invalid = []

    for relative_path in state["generated_files"]:
        path = Path(relative_path)

        if path.is_absolute():
            invalid.append(relative_path)

    assert not invalid, "\n".join(invalid)
