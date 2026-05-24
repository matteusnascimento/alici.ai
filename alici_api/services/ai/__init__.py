"""AI provider package and legacy availability exports."""

from __future__ import annotations

from .manager import AIManager

try:
    from model_inference import fazer_predicao, gerar_resposta_predicao

    VISAO_DISPONIVEL = True
except ImportError:
    VISAO_DISPONIVEL = False

    def fazer_predicao(*args, **kwargs):
        raise RuntimeError("Modelo de visao indisponivel")

    def gerar_resposta_predicao(*args, **kwargs):
        raise RuntimeError("Modelo de visao indisponivel")


IA_DISPONIVEL = True


def gerar_resposta(pergunta: str) -> str:
    """Compatibility wrapper for older imports.

    New chat endpoints should use alici_api.services.ai_service instead.
    """
    from engine import gerar_resposta as legacy_gerar_resposta

    return legacy_gerar_resposta(pergunta)


def gerar_resposta_com_emocao(pergunta: str) -> dict:
    from sistema_emocoes import adicionar_metadados_resposta

    return adicionar_metadados_resposta(gerar_resposta(pergunta))


__all__ = [
    "AIManager",
    "IA_DISPONIVEL",
    "VISAO_DISPONIVEL",
    "gerar_resposta",
    "gerar_resposta_com_emocao",
    "fazer_predicao",
    "gerar_resposta_predicao",
]
