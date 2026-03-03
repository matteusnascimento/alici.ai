"""HuggingFace Inference API service.

This module provides a clean HTTP-based client for the HuggingFace Inference API,
separate from the model-loading utilities in text_model_hf.py.
"""

from __future__ import annotations

import os
import time

import requests

from logger import get_logger

logger_hf = get_logger("huggingface_service")

HF_API_KEY: str | None = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
HF_MODEL_URL: str = os.getenv("HUGGINGFACE_MODEL_URL", "")
HF_TIMEOUT: int = int(os.getenv("HUGGINGFACE_TIMEOUT_SECONDS", "25"))
HF_MAX_RETRIES: int = int(os.getenv("HUGGINGFACE_MAX_RETRIES", "2"))
HF_MAX_NEW_TOKENS: int = int(os.getenv("HUGGINGFACE_MAX_NEW_TOKENS", "200"))

_INFERENCE_BASE = "https://api-inference.huggingface.co/models/"


def _build_headers() -> dict[str, str]:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if HF_API_KEY:
        headers["Authorization"] = f"Bearer {HF_API_KEY}"
    return headers


def query_text_generation(text: str, model_url: str | None = None) -> str:
    """Call HuggingFace Inference API for text generation.

    Args:
        text: The input prompt.
        model_url: Full API URL (optional; falls back to HUGGINGFACE_MODEL_URL env var).

    Returns:
        Generated text string.

    Raises:
        RuntimeError: On persistent failure after retries.
    """
    url = model_url or HF_MODEL_URL
    if not url:
        raise RuntimeError(
            "HUGGINGFACE_MODEL_URL não configurado. "
            "Defina a variável de ambiente HUGGINGFACE_MODEL_URL com a URL do modelo."
        )

    payload: dict = {"inputs": text, "parameters": {"max_new_tokens": HF_MAX_NEW_TOKENS, "return_full_text": False}}

    last_error: Exception | None = None
    for attempt in range(HF_MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=_build_headers(), json=payload, timeout=HF_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, list) and data:
                first = data[0]
                if isinstance(first, dict):
                    return str(first.get("generated_text") or first.get("label") or first)
                return str(first)

            if isinstance(data, dict):
                return str(data.get("generated_text") or data.get("error") or data)

            return str(data)

        except requests.exceptions.Timeout as exc:
            last_error = exc
            logger_hf.warning(f"Timeout na tentativa {attempt + 1}/{HF_MAX_RETRIES + 1}: {exc}")
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            logger_hf.error(f"HTTP {status} da HuggingFace API: {exc}")
            raise RuntimeError(f"HuggingFace API retornou HTTP {status}") from exc
        except Exception as exc:
            last_error = exc
            logger_hf.warning(f"Erro na tentativa {attempt + 1}: {exc}")

        if attempt < HF_MAX_RETRIES:
            time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(
        f"HuggingFace API indisponível após {HF_MAX_RETRIES + 1} tentativas: {last_error}"
    )


def query_feature_extraction(text: str, model_id: str) -> list[float]:
    """Extract feature embeddings from HuggingFace Inference API.

    Args:
        text: Input text.
        model_id: HuggingFace model ID (e.g. 'sentence-transformers/all-MiniLM-L6-v2').

    Returns:
        List of float embeddings.
    """
    url = f"{_INFERENCE_BASE}{model_id}"
    resp = requests.post(url, headers=_build_headers(), json={"inputs": text}, timeout=HF_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        return data
    raise RuntimeError(f"Formato inesperado da resposta: {type(data)}")


def is_configured() -> bool:
    """Return True if the HuggingFace Inference API is configured."""
    return bool(HF_MODEL_URL)


def get_service_status() -> dict:
    """Return a status dict for the HuggingFace Inference API service."""
    return {
        "configurado": is_configured(),
        "model_url": HF_MODEL_URL or None,
        "timeout_segundos": HF_TIMEOUT,
        "max_retries": HF_MAX_RETRIES,
        "api_key_presente": bool(HF_API_KEY),
    }


__all__ = [
    "query_text_generation",
    "query_feature_extraction",
    "is_configured",
    "get_service_status",
]
