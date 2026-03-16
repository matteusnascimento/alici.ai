class AgentRuntime:
    def __init__(self, name: str, model: str, system_prompt: str):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt

    def run(self, user_input: str) -> str:
        return f"[{self.name}:{self.model}] {self.system_prompt} :: {user_input}"
