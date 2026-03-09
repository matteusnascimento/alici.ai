"""Multimodal media routes."""

import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import AudioRequest, ImageRequest, VideoRequest
from alici_api.services.ai import VISAO_DISPONIVEL, fazer_predicao
from alici_api.services.media_service import (
    analyze_image_bytes,
    generate_audio,
    generate_image,
    generate_video,
)
from logger import get_logger

router = APIRouter(tags=["media"])
logger_media = get_logger("route_media")


@router.post("/generate-image")
def generate_image_endpoint(req: ImageRequest, user=Depends(get_current_user)):
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Prompt vazio"},
        )

    image_url = generate_image(prompt)
    return success(Codes.MEDIA_IMAGE_OK, url=image_url, usuario=user["nome"])


@router.post("/generate-audio")
def generate_audio_endpoint(req: AudioRequest, user=Depends(get_current_user)):
    texto = (req.texto or "").strip()
    if not texto:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Texto vazio"},
        )

    audio_url = generate_audio(texto)
    return success(Codes.MEDIA_AUDIO_OK, audio_url=audio_url, usuario=user["nome"])


@router.post("/generate-video")
def generate_video_endpoint(req: VideoRequest, user=Depends(get_current_user)):
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Prompt vazio"},
        )

    payload = generate_video(prompt)
    payload["usuario"] = user["nome"]
    return success(Codes.MEDIA_VIDEO_OK, **payload)


@router.post("/analyze-image")
def analyze_image_endpoint(file: UploadFile = File(...), user=Depends(get_current_user)):
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Tipo de arquivo não suportado"},
        )

    content = file.file.read()
    if not content:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Arquivo vazio"},
        )

    if VISAO_DISPONIVEL:
        tmp_path = None
        try:
            suffix = os.path.splitext(file.filename or "imagem.png")[1] or ".png"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            prediction = fazer_predicao(tmp_path, top_k=3)
            return success(Codes.MEDIA_ANALYZE_OK, usuario=user["nome"], resultado=prediction)
        except Exception:
            logger_media.exception("Falha na análise com modelo de visão; aplicando fallback")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    logger_media.warning("Falha ao remover arquivo temporário", extra={"tmp_path": tmp_path})

    basic = analyze_image_bytes(content, file.filename or "imagem", file.content_type or "image/unknown")
    return success(Codes.MEDIA_ANALYZE_OK, usuario=user["nome"], resultado=basic)
