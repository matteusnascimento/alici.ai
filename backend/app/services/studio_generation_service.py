from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.studio_generation import StudioGeneration
from app.services.ai_service import AIService


class StudioGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()

    def create_generation(
        self,
        *,
        user_id: int,
        project_id: int | None,
        generation_type: str,
        prompt: str,
        input_payload: dict[str, Any],
        result_payload: dict[str, Any],
    ) -> StudioGeneration:
        item = StudioGeneration(
            user_id=user_id,
            project_id=project_id,
            generation_type=generation_type,
            prompt=prompt,
            input_json=json.dumps(input_payload, ensure_ascii=True),
            output_json=json.dumps(result_payload, ensure_ascii=True),
            status="completed",
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def generate_poster_variations(self, prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        base_style = options.get("style", "premium-cyan")
        schema = {
            "type": "object",
            "properties": {
                "variations": {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 4,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "headline": {"type": "string"},
                            "cta": {"type": "string"},
                            "style": {"type": "string"},
                        },
                        "required": ["id", "headline", "cta", "style"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["variations"],
            "additionalProperties": False,
        }
        result = self.ai.generate_structured_output(
            prompt=f"Prompt criativo: {prompt}\nEstilo base: {base_style}",
            schema=schema,
            system_prompt=(
                "Crie 4 variacoes de poster em pt-BR para anuncios premium. "
                "Cada variacao precisa de headline curta, CTA forte e style descritivo."
            ),
            function_name="ad_copy_generator",
        )
        return {
            "kind": "poster",
            "generated_at": datetime.utcnow().isoformat(),
            "variations": result.get("variations", []),
            "prompt": prompt,
        }

    def generate_copy(self, prompt: str, mode: str) -> dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {
                "result": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "items": {"type": "string"},
                }
            },
            "required": ["result"],
            "additionalProperties": False,
        }
        generated = self.ai.generate_structured_output(
            prompt=f"Modo: {mode}\nBriefing: {prompt}",
            schema=schema,
            system_prompt="Gere 3 variacoes de texto em pt-BR para o modo solicitado. Retorne apenas JSON valido.",
            function_name="social_post_generator",
        )
        return {
            "mode": mode,
            "prompt": prompt,
            "result": generated.get("result", []),
        }

    def generate_brand_style(self, prompt: str) -> dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {
                "brand_direction": {"type": "string"},
                "colors": {"type": "array", "items": {"type": "string"}},
                "typography": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["brand_direction", "colors", "typography"],
            "additionalProperties": False,
        }
        generated = self.ai.generate_structured_output(
            prompt=prompt,
            schema=schema,
            system_prompt="Crie uma direcao visual de marca em pt-BR com posicionamento, paleta e tipografia. Retorne apenas JSON valido.",
            function_name="product_description_generator",
        )
        generated["prompt"] = prompt
        return generated
