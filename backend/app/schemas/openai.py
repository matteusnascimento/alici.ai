from pydantic import BaseModel


class OpenAIChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    temperature: float = 0.2


class OpenAIChatResponse(BaseModel):
    content: str
    model: str
    usage: dict | None = None
