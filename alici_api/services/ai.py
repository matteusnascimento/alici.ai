"""AI service helpers and availability flags."""

try:
    from engine import gerar_resposta, gerar_resposta_com_emocao

    IA_DISPONIVEL = True
except ImportError:
    IA_DISPONIVEL = False
    print("[WARNING] Módulos de IA textual não disponíveis (engine.py)")

try:
    from model_inference import fazer_predicao, gerar_resposta_predicao

    VISAO_DISPONIVEL = True
except ImportError:
    VISAO_DISPONIVEL = False

    def fazer_predicao(*args, **kwargs):
        raise RuntimeError("Modelo de visão indisponível")

    def gerar_resposta_predicao(*args, **kwargs):
        raise RuntimeError("Modelo de visão indisponível")

if not IA_DISPONIVEL:
    def gerar_resposta(*args, **kwargs):
        raise RuntimeError("IA textual indisponível")

    def gerar_resposta_com_emocao(*args, **kwargs):
        raise RuntimeError("IA textual indisponível")

__all__ = [
    "IA_DISPONIVEL",
    "VISAO_DISPONIVEL",
    "gerar_resposta",
    "gerar_resposta_com_emocao",
    "fazer_predicao",
    "gerar_resposta_predicao",
]
