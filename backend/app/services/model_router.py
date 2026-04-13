from enum import Enum

from app.core.config import settings
from app.services.ai.model_router import get_model_for_task as get_model_for_task_central


class AIFunction(str, Enum):
    CHAT = "chat_general"
    CHAT_PREMIUM = "chat_support"
    MARKETING_COPY = "prompt_generation"
    STRUCTURED_EXTRACTION = "classification"
    IMAGE_ANALYSIS = "vision_analysis"
    IMAGE_GENERATION = "image_generation"
    IMAGE_EDIT = "image_generation"
    AUDIO_TRANSCRIPTION = "transcription"
    AUDIO_TRANSCRIPTION_FAST = "transcription"
    TEXT_TO_SPEECH = "tool_reasoning"
    EMBEDDING = "embedding"
    EMBEDDING_HIGH = "embedding"
    AGENT_RUNTIME = "agent_runtime"
    SUMMARIZATION = "summarization"
    KNOWLEDGE_QA = "knowledge_qa"
    TOOL_REASONING = "tool_reasoning"


MODEL_BY_FUNCTION = {
    AIFunction.CHAT: settings.openai_model_chat_general or settings.openai_model,
    AIFunction.CHAT_PREMIUM: settings.openai_model_support or settings.openai_model,
    AIFunction.MARKETING_COPY: settings.openai_model_copy or settings.openai_model,
    AIFunction.STRUCTURED_EXTRACTION: settings.openai_model_classifier or settings.openai_model,
    AIFunction.IMAGE_ANALYSIS: settings.openai_model_vision or settings.openai_model,
    AIFunction.IMAGE_GENERATION: settings.openai_image_model,
    AIFunction.IMAGE_EDIT: settings.openai_image_model,
    AIFunction.AUDIO_TRANSCRIPTION: settings.openai_model_transcription,
    AIFunction.AUDIO_TRANSCRIPTION_FAST: settings.openai_model_transcription,
    AIFunction.TEXT_TO_SPEECH: settings.openai_model_support or settings.openai_model,
    AIFunction.EMBEDDING: settings.openai_model_embeddings,
    AIFunction.EMBEDDING_HIGH: settings.openai_model_embeddings,
    AIFunction.AGENT_RUNTIME: settings.openai_model_agent_runtime or settings.openai_model,
    AIFunction.SUMMARIZATION: settings.openai_model_summarization or settings.openai_model,
    AIFunction.KNOWLEDGE_QA: settings.openai_model_knowledge_qa or settings.openai_model,
    AIFunction.TOOL_REASONING: settings.openai_model_support or settings.openai_model,
}


def get_model_for(function_name: AIFunction) -> str:
    return MODEL_BY_FUNCTION.get(function_name) or settings.openai_model_chat_general or settings.openai_model


def get_model_for_task(task_name: str) -> str:
    return get_model_for_task_central(task_name)
