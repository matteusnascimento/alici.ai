"""Chat routes."""

import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from alici_api.dependencies import get_current_user
from alici_api.schemas import ChatRequest
from alici_api.services.ai import (
    IA_DISPONIVEL,
    VISAO_DISPONIVEL,
    fazer_predicao,
    gerar_resposta,
    gerar_resposta_com_emocao,
    gerar_resposta_predicao,
)
from database import salvar_historico

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(req: ChatRequest, user=Depends(get_current_user)):
    if not IA_DISPONIVEL:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")

    if not req.pergunta or not req.pergunta.strip():
        raise HTTPException(status_code=400, detail="Pergunta vazia")

    try:
        if req.incluir_emocao:
            resultado_emocao = gerar_resposta_com_emocao(req.pergunta)
            resposta = resultado_emocao.get("resposta", "")
        else:
            resultado_emocao = None
            resposta = gerar_resposta(req.pergunta)

        salvar_historico(user["id"], req.pergunta, resposta)

        resultado = {
            "status": "sucesso",
            "resposta": resposta,
            "usuario": user["nome"],
        }

        if resultado_emocao:
            resultado["emocao"] = resultado_emocao.get("emocao")
            resultado["intensidade"] = resultado_emocao.get("intensidade")

        return resultado

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/chat/image")
def chat_image(user=Depends(get_current_user), imagem: UploadFile = File(...)):
    if not IA_DISPONIVEL or not VISAO_DISPONIVEL:
        raise HTTPException(status_code=503, detail="Modelo não disponível")

    if imagem.content_type not in ["image/png", "image/jpeg", "image/gif", "image/bmp"]:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            conteudo = imagem.file.read()
            tmp.write(conteudo)
            tmp_path = tmp.name

        resultado = fazer_predicao(tmp_path, top_k=3)

        os.remove(tmp_path)

        if resultado.get("status") == "erro":
            raise HTTPException(status_code=400, detail=resultado.get("erro"))

        resposta = gerar_resposta_predicao(resultado)
        pergunta = f"[Análise de imagem] {resultado.get('classe')}"
        salvar_historico(user["id"], pergunta, resposta)

        return {
            "status": "sucesso",
            "classe": resultado["classe"],
            "confianca": resultado["confianca"],
            "resposta": resposta,
            "alternativas": resultado.get("top_k", [])[1:],
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
