"""Isolated HuggingFace inference service with automatic retry.

Uses the HuggingFace Inference API (not a local model load).
Configure via environment variables:
  HUGGINGFACE_API_KEY      — Bearer token for the HF Inference API
  HUGGINGFACE_MODEL_URL    — Full inference endpoint URL
  HUGGINGFACE_TIMEOUT_SECONDS — Request timeout in seconds (default 30)
  HUGGINGFACE_MAX_NEW_TOKENS  — Max tokens for generation (default 300)
"""

from __future__ import annotations

import os

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from logger import get_logger

logger_hf = get_logger("huggingface_service")

HF_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
HF_MODEL_URL: str = os.getenv("HUGGINGFACE_MODEL_URL", "")
TIMEOUT: int = int(os.getenv("HUGGINGFACE_TIMEOUT_SECONDS", 30))
MAX_NEW_TOKENS: int = int(os.getenv("HUGGINGFACE_MAX_NEW_TOKENS", 300))

_HEADERS: dict[str, str] = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def query_text_generation(prompt: str) -> list | dict:
    """Call the HuggingFace text-generation inference endpoint with automatic retries.

    Args:
        prompt: The input text prompt.

    Returns:
        Parsed JSON response from the HuggingFace API.

    Raises:
        RuntimeError: When HUGGINGFACE_MODEL_URL is not configured.
        requests.HTTPError: On non-2xx responses after all retries are exhausted.
    """
    if not HF_MODEL_URL:
        raise RuntimeError("HUGGINGFACE_MODEL_URL não configurado")

    payload: dict = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": MAX_NEW_TOKENS,
        },
    }

    response = requests.post(
        HF_MODEL_URL,
        headers=_HEADERS,
        json=payload,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def query_huggingface(prompt: str) -> str:
    """High-level wrapper that returns the generated text as a plain string.

    Falls back by raising an exception if the API is unavailable so callers
    can handle the fallback logic themselves.

    Args:
        prompt: User input.

    Returns:
        Generated text string.

    Raises:
        Exception: When the HuggingFace API is unreachable or returns an error.
    """
    result = query_text_generation(prompt)

    if isinstance(result, list) and result:
        first = result[0]
        if isinstance(first, dict):
            return str(first.get("generated_text", first.get("text", prompt)))
        return str(first)

    if isinstance(result, dict):
        return str(result.get("generated_text", result.get("text", prompt)))

    return str(result)
