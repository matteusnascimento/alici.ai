"""
🎓 TRAINING MODULE
Orquestração de treinamento multimodal
"""

from .trainer import TrainerMultimodal, NeonLoggingCallback, gerar_dados_dummy

__all__ = [
    'TrainerMultimodal',
    'NeonLoggingCallback',
    'gerar_dados_dummy'
]
