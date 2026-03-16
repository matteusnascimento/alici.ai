class MemoryManager:
    def __init__(self):
        self._state: dict[str, list[str]] = {}

    def append(self, session_id: str, text: str) -> None:
        self._state.setdefault(session_id, []).append(text)

    def history(self, session_id: str) -> list[str]:
        return self._state.get(session_id, [])
