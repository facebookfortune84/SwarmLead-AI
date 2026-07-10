class SessionMemory:
    """
    Runtime memory for a single campaign,
    agent execution, or conversation.
    """

    def __init__(self):
        self._memory = {}

    def set(self, key, value):
        self._memory[key] = value

    def get(self, key, default=None):
        return self._memory.get(key, default)

    def append(self, key, value):
        self._memory.setdefault(key, [])
        self._memory[key].append(value)

    def delete(self, key):
        self._memory.pop(key, None)

    def clear(self):
        self._memory.clear()

    def all(self):
        return self._memory.copy()
