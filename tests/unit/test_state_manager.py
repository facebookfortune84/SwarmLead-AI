from core.state.state_manager import StateManager


def test_set_and_get():
    manager = StateManager()

    manager.set("user", "alice")

    assert manager.get("user") == "alice"


def test_default_value():
    manager = StateManager()

    assert manager.get("missing", "default") == "default"


def test_delete_key():
    manager = StateManager()

    manager.set("x", 1)

    manager.delete("x")

    assert manager.get("x") is None


def test_clear():
    manager = StateManager()

    manager.set("a", 1)
    manager.set("b", 2)

    manager.clear()

    assert manager.all() == {}


def test_all_returns_copy():
    manager = StateManager()

    manager.set("key", "value")

    snapshot = manager.all()

    snapshot["key"] = "changed"

    assert manager.get("key") == "value"
