"""R2-backed intent model loader and inference helpers for textual chat."""

from __future__ import annotations

import json
import os
import pickle
import random
import threading
from pathlib import Path

import boto3
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from logger import get_logger

logger_text_model = get_logger("text_model_r2")

_LOCK = threading.Lock()
_MODEL = None
_TOKENIZER = None
_LABEL_ENCODER = None
_MAX_LEN = 40
_INTENT_RESPONSES: dict[str, list[str]] = {}
_INITIALIZED = False
_AVAILABLE = False
_LAST_ERROR = "não inicializado"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _build_r2_client():
    account_id = os.getenv("ALICI_R2_ACCOUNT_ID", "")
    access_key = os.getenv("ALICI_R2_ACCESS_KEY", "")
    secret_key = os.getenv("ALICI_R2_SECRET_KEY", "")

    if not account_id or not access_key or not secret_key:
        raise RuntimeError(
            "Credenciais do R2 ausentes. Defina ALICI_R2_ACCOUNT_ID, ALICI_R2_ACCESS_KEY e ALICI_R2_SECRET_KEY"
        )

    endpoint = os.getenv("ALICI_R2_ENDPOINT", f"https://{account_id}.r2.cloudflarestorage.com")

    return boto3.client(
        service_name="s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def _cache_dir() -> Path:
    return Path(os.getenv("ALICI_MODEL_CACHE_DIR", "/tmp/alici_cpu_simple_r2_cache"))


def _load_intent_responses() -> dict[str, list[str]]:
    intents_path = Path(os.getenv("ALICI_INTENTS_PATH", str(_project_root() / "intents.json")))
    if not intents_path.exists():
        logger_text_model.warning(f"intents.json não encontrado em: {intents_path}")
        return {}

    with intents_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    responses: dict[str, list[str]] = {}
    for intent in data.get("intents", []):
        tag = intent.get("tag")
        values = intent.get("responses", [])
        if tag and isinstance(values, list) and values:
            responses[str(tag)] = [str(v) for v in values if str(v).strip()]
    return responses


def _ensure_artifacts_local(force_download: bool = False) -> dict[str, Path]:
    bucket = os.getenv("ALICI_R2_BUCKET", "")
    prefix = os.getenv("ALICI_R2_MODEL_PREFIX", "")
    if not bucket or not prefix:
        raise RuntimeError(
            "Configuração do R2 incompleta. Defina ALICI_R2_BUCKET e ALICI_R2_MODEL_PREFIX"
        )

    cache_dir = _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "model": "alici_cpu_simple.keras",
        "tokenizer": "tokenizer.pkl",
        "label_encoder": "label_encoder.pkl",
        "metadata": "metadata.json",
    }

    s3 = _build_r2_client()

    local_paths: dict[str, Path] = {}
    for key_name, filename in files.items():
        local_path = cache_dir / filename
        remote_key = f"{prefix.rstrip('/')}/{filename}"

        if force_download or not local_path.exists():
            logger_text_model.info(f"Baixando artefato do R2: {remote_key}")
            s3.download_file(bucket, remote_key, str(local_path))

        local_paths[key_name] = local_path

    return local_paths


def initialize_text_model_from_r2(force_download: bool = False) -> bool:
    global _MODEL, _TOKENIZER, _LABEL_ENCODER, _MAX_LEN, _INTENT_RESPONSES
    global _INITIALIZED, _AVAILABLE, _LAST_ERROR

    with _LOCK:
        if _INITIALIZED and _AVAILABLE and not force_download:
            return True

        try:
            artifacts = _ensure_artifacts_local(force_download=force_download)

            _MODEL = load_model(str(artifacts["model"]))

            with artifacts["tokenizer"].open("rb") as file:
                _TOKENIZER = pickle.load(file)

            with artifacts["label_encoder"].open("rb") as file:
                _LABEL_ENCODER = pickle.load(file)

            with artifacts["metadata"].open("r", encoding="utf-8") as file:
                metadata = json.load(file)
                _MAX_LEN = int(metadata.get("max_len", 40))

            _INTENT_RESPONSES = _load_intent_responses()
            _INITIALIZED = True
            _AVAILABLE = True
            _LAST_ERROR = ""
            logger_text_model.info("✅ Modelo textual carregado do R2 com sucesso")
            return True
        except Exception as exc:
            _INITIALIZED = True
            _AVAILABLE = False
            _LAST_ERROR = str(exc)
            logger_text_model.warning(f"⚠ Falha ao carregar modelo textual do R2: {exc}")
            return False


def get_text_model_status() -> dict:
    return {
        "disponivel": _AVAILABLE,
        "inicializado": _INITIALIZED,
        "erro": _LAST_ERROR if not _AVAILABLE else "",
        "cache_dir": str(_cache_dir()),
    }


def predict_intent_from_text(text: str) -> dict | None:
    if not text or not text.strip():
        return None

    if not _AVAILABLE and not initialize_text_model_from_r2():
        return None

    normalized = " ".join(text.lower().strip().split())
    sequence = _TOKENIZER.texts_to_sequences([normalized])
    x = pad_sequences(sequence, maxlen=_MAX_LEN, padding="post", truncating="post")

    probs = _MODEL.predict(x, verbose=0)[0]
    best_idx = int(np.argmax(probs))
    confidence = float(probs[best_idx])
    predicted_tag = str(_LABEL_ENCODER.inverse_transform([best_idx])[0])

    response = None
    if predicted_tag in _INTENT_RESPONSES and _INTENT_RESPONSES[predicted_tag]:
        response = random.choice(_INTENT_RESPONSES[predicted_tag])

    return {
        "tag": predicted_tag,
        "confidence": confidence,
        "response": response,
    }


__all__ = [
    "initialize_text_model_from_r2",
    "get_text_model_status",
    "predict_intent_from_text",
]
