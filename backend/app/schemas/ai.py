from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PromptPlaygroundRequest(BaseModel):
    system_prompt: str | None = None
    user_prompt: str
    history: list[dict[str, Any]] = Field(default_factory=list)
    temperature: float = 0.3


class TaskTextRequest(BaseModel):
    prompt: str


class AgentBuilderRequest(BaseModel):
    context: str


class WorkflowBuilderRequest(BaseModel):
    context: str


class AnalyticsInsightsRequest(BaseModel):
    metrics_json: dict[str, Any]


class ImageAnalysisRequest(BaseModel):
    image_url: str | None = None
    prompt: str | None = None


class DocumentAnalysisRequest(BaseModel):
    content: str


class AIStandardResponse(BaseModel):
    success: bool
    provider: str
    model: str
    task: str
    content: str | None
    structured_data: dict[str, Any] | None
    usage: dict[str, int]
    meta: dict[str, Any]
