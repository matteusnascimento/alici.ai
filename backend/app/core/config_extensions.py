"""Configuration extensions for AI providers - Add to app/core/config.py Settings class."""

from pydantic import Field

# ─────────────────────────────────────────────────────────────────
# Add these fields to the Settings class in app/core/config.py
# ─────────────────────────────────────────────────────────────────

# AI Provider Configuration
default_ai_provider: str = Field(default="groq", description="Default AI provider: groq, gemini, ollama, openai")

# Groq Configuration
groq_api_key: str = Field(default="", description="Groq API key")
groq_model_chat: str = Field(default="llama-3.1-8b-instant", description="Groq chat model")
groq_model_agent: str = Field(default="llama-3.1-8b-instant", description="Groq agent runtime model")
groq_model_code: str = Field(default="qwen/qwen3-coder", description="Groq code generation model")
groq_timeout_seconds: float = Field(default=30.0, description="Groq request timeout in seconds")

# Gemini Configuration
gemini_api_key: str = Field(default="", description="Google Gemini API key")
gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model to use")
gemini_timeout_seconds: float = Field(default=30.0, description="Gemini request timeout in seconds")

# Ollama Configuration
ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama server base URL")
ollama_model: str = Field(default="llama3", description="Ollama model to use")
ollama_timeout_seconds: float = Field(default=60.0, description="Ollama request timeout in seconds")

# Computed Properties (add to Settings class)
# ─────────────────────────────────────────────────────────────────

# @property
# def effective_openai_api_key(self) -> str | None:
#     """Return OpenAI API key with support for rotation."""
#     return (self.openai_api_key_rotated or "").strip() or (self.openai_api_key or "").strip() or None
