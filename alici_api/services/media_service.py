"""Serviços multimodais básicos para geração e análise de mídia."""

from __future__ import annotations

import base64
import html
import math
import struct
import uuid
import wave
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
GENERATED_DIR = BASE_DIR / "generated"
IMAGES_DIR = GENERATED_DIR / "images"
AUDIOS_DIR = GENERATED_DIR / "audios"
VIDEOS_DIR = GENERATED_DIR / "videos"

for directory in (GENERATED_DIR, IMAGES_DIR, AUDIOS_DIR, VIDEOS_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def _safe_slug(text: str, max_len: int = 60) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in text.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    if not cleaned:
        cleaned = "prompt"
    return cleaned[:max_len]


def generate_image(prompt: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_name = f"{timestamp}_{_safe_slug(prompt)}_{uuid.uuid4().hex[:8]}.svg"
    file_path = IMAGES_DIR / file_name

    escaped_prompt = html.escape(prompt)
    svg_content = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1024\" height=\"1024\" viewBox=\"0 0 1024 1024\">\n  <defs>\n    <linearGradient id=\"bg\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">\n      <stop offset=\"0%\" stop-color=\"#030307\"/>\n      <stop offset=\"50%\" stop-color=\"#13243a\"/>\n      <stop offset=\"100%\" stop-color=\"#0a3f46\"/>\n    </linearGradient>\n  </defs>\n  <rect width=\"1024\" height=\"1024\" fill=\"url(#bg)\"/>\n  <circle cx=\"300\" cy=\"280\" r=\"180\" fill=\"#00ffe1\" fill-opacity=\"0.2\"/>\n  <circle cx=\"760\" cy=\"720\" r=\"220\" fill=\"#7a5cff\" fill-opacity=\"0.2\"/>\n  <text x=\"64\" y=\"140\" fill=\"#e8ecff\" font-size=\"40\" font-family=\"Arial\">ALICI • Imagem Gerada</text>\n  <foreignObject x=\"64\" y=\"220\" width=\"896\" height=\"700\">\n    <div xmlns=\"http://www.w3.org/1999/xhtml\" style=\"color:#e8ecff;font-family:Arial;font-size:34px;line-height:1.4;\">\n      <strong>Prompt:</strong> {escaped_prompt}\n    </div>\n  </foreignObject>\n</svg>\n"""
    file_path.write_text(svg_content, encoding="utf-8")
    return f"/generated/images/{file_name}"


def generate_audio(text: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_name = f"{timestamp}_{uuid.uuid4().hex[:8]}.wav"
    file_path = AUDIOS_DIR / file_name

    duration_seconds = max(1.2, min(6.0, len(text) * 0.06))
    sample_rate = 22050
    frequency = 440.0
    amplitude = 12000
    frame_count = int(sample_rate * duration_seconds)

    with wave.open(str(file_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for index in range(frame_count):
            envelope = 1.0 - (index / frame_count) * 0.35
            value = int(amplitude * envelope * math.sin(2 * math.pi * frequency * (index / sample_rate)))
            wav_file.writeframes(struct.pack("<h", value))

    return f"/generated/audios/{file_name}"


def generate_video(prompt: str) -> dict:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    job_id = f"video_{timestamp}_{uuid.uuid4().hex[:8]}"
    file_name = f"{job_id}.json"
    file_path = VIDEOS_DIR / file_name

    payload = {
        "job_id": job_id,
        "status": "queued",
        "prompt": prompt,
        "created_at": datetime.utcnow().isoformat(),
        "message": "MVP: geração de vídeo marcada como processamento assíncrono.",
    }

    file_path.write_text(str(payload), encoding="utf-8")
    return {
        "job_id": job_id,
        "status": "queued",
        "video_url": f"/generated/videos/{file_name}",
        "message": payload["message"],
    }


def analyze_image_bytes(content: bytes, filename: str, content_type: str) -> dict:
    size_bytes = len(content)
    snippet_b64 = base64.b64encode(content[:24]).decode("utf-8")

    return {
        "descricao": (
            "Análise básica concluída (MVP sem modelo de visão ativo). "
            f"Arquivo {filename}, tipo {content_type}, tamanho {size_bytes} bytes."
        ),
        "arquivo": filename,
        "tipo": content_type,
        "tamanho_bytes": size_bytes,
        "assinatura_base64": snippet_b64,
    }
