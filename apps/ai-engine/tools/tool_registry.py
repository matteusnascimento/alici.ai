class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, callable] = {}

    def register(self, name: str, fn: callable) -> None:
        self._tools[name] = fn

    def call(self, name: str, payload: dict):
        if name not in self._tools:
            raise KeyError(f"tool not found: {name}")
        return self._tools[name](payload)
