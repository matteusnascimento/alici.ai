from __future__ import annotations

from datetime import datetime
from typing import Any

from app.services.ai_service import AIService
from app.services.model_router import AIFunction


class StudioVideoService:
    _ai = AIService()

    @staticmethod
    def generate(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "video-generate",
            "status": "completed",
            "prompt": prompt,
            "duration": options.get("duration", 15),
            "ratio": options.get("ratio", "9:16"),
            "output_url": f"video://generated/{int(datetime.utcnow().timestamp())}",
        }

    @staticmethod
    def captions(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        generated = StudioVideoService._ai.generate_structured_output(
            prompt=f"Briefing: {prompt}\nEstilo: {options.get('style', 'bold-modern')}",
            schema={
                "type": "object",
                "properties": {
                    "captions": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 3,
                        "items": {"type": "string"},
                    }
                },
                "required": ["captions"],
                "additionalProperties": False,
            },
            system_prompt="Gere 3 legendas de video em pt-BR com gancho, beneficio e CTA. Retorne apenas JSON valido.",
            function_name=AIFunction.MARKETING_COPY,
        )
        return {
            "operation": "video-captions",
            "status": "completed",
            "captions": generated.get("captions", []),
            "style": options.get("style", "bold-modern"),
            "source": prompt,
        }

    @staticmethod
    def cut(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "video-cut",
            "status": "completed",
            "scenes": [
                {"from": 0, "to": 3},
                {"from": 3, "to": 8},
                {"from": 8, "to": 15},
            ],
            "source": prompt,
            "options": options,
        }

    @staticmethod
    def voiceover(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        script = StudioVideoService._ai.generate_text(
            system_prompt="Escreva um roteiro curto de voiceover em pt-BR para video comercial, com abertura forte e CTA final.",
            user_prompt=prompt,
            temperature=0.5,
            function_name=AIFunction.MARKETING_COPY,
        )
        return {
            "operation": "video-voiceover",
            "status": "completed",
            "voice": options.get("voice", "pt-BR-female-pro"),
            "script": script,
            "audio_url": f"audio://voice/{int(datetime.utcnow().timestamp())}",
        }

    @staticmethod
    def export(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "video-export",
            "status": "completed",
            "preset": options.get("preset", "reel-hq"),
            "file_url": f"video://export/{int(datetime.utcnow().timestamp())}",
            "source": prompt,
        }

    @staticmethod
    def thumbnail(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "video-thumbnail",
            "status": "completed",
            "style": options.get("style", "high-contrast"),
            "thumbnail_url": f"image://thumbnail/{int(datetime.utcnow().timestamp())}",
            "source": prompt,
        }
