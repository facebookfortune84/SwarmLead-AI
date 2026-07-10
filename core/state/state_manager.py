class StateManager:
    """
    Shared runtime state for agents and workflows.
    """

    def __init__(self):
        self._state = {}

    def set(self, key, value):
        self._state[key] = value

    def get(self, key, default=None):
        return self._state.get(key, default)

    def delete(self, key):
        self._state.pop(key, None)

    def clear(self):
        self._state.clear()

    def all(self):
        return self._state.copy()
