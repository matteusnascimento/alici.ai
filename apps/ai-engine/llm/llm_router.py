class LLMRouter:
    def pick_model(self, task: str) -> str:
        task_lower = task.lower()
        if "code" in task_lower:
            return "gpt-4.1"
        if "vision" in task_lower:
            return "gpt-4o"
        return "gpt-4.1-mini"


def generate_response(prompt: str) -> str:
    return f"Resposta da IA: {prompt}"
