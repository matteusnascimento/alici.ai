"""
🧠 ARQUITETURA MULTIMODAL - RAMOS SEPARADOS
"""

from .image_branch import image_branch
from .text_branch import text_branch
from .audio_branch import audio_branch
from .multimodal_model import criar_modelo_multimodal

__all__ = [
    'image_branch',
    'text_branch',
    'audio_branch',
    'criar_modelo_multimodal'
]
