from enum import Enum


class AIFunction(str, Enum):
    CHAT = "chat"
    CHAT_PREMIUM = "chat_premium"
    MARKETING_COPY = "marketing_copy"
    STRUCTURED_EXTRACTION = "structured_extraction"
    IMAGE_ANALYSIS = "image_analysis"
    IMAGE_GENERATION = "image_generation"
    IMAGE_EDIT = "image_edit"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_TRANSCRIPTION_FAST = "audio_transcription_fast"
    TEXT_TO_SPEECH = "text_to_speech"
    EMBEDDING = "embedding"
    EMBEDDING_HIGH = "embedding_high"


MODEL_BY_FUNCTION = {
    AIFunction.CHAT: "gpt-4o-mini",
    AIFunction.CHAT_PREMIUM: "gpt-5.4-mini",
    AIFunction.MARKETING_COPY: "gpt-4o-mini",
    AIFunction.STRUCTURED_EXTRACTION: "gpt-4o-mini",
    AIFunction.IMAGE_ANALYSIS: "gpt-4o-mini",
    AIFunction.IMAGE_GENERATION: "gpt-image-1",
    AIFunction.IMAGE_EDIT: "gpt-image-1",
    AIFunction.AUDIO_TRANSCRIPTION: "gpt-4o-transcribe",
    AIFunction.AUDIO_TRANSCRIPTION_FAST: "gpt-4o-mini-transcribe",
    AIFunction.TEXT_TO_SPEECH: "gpt-4o-mini-tts",
    AIFunction.EMBEDDING: "text-embedding-3-small",
    AIFunction.EMBEDDING_HIGH: "text-embedding-3-large",
}


def get_model_for(function_name: AIFunction) -> str:
    return MODEL_BY_FUNCTION[function_name]
