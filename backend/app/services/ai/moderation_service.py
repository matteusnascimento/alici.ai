from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModerationResult:
    allowed: bool
    reason: str | None = None


class ModerationService:
    # Guardrail simples local; pode ser substituído por endpoint dedicado depois.
    _blocked_terms = {
        "hack account",
        "bypass payment",
        "credit card dump",
        "exploit production",
        "sql injection payload",
    }

    def check_text(self, text: str) -> ModerationResult:
        lowered = (text or "").strip().lower()
        if not lowered:
            return ModerationResult(allowed=True)
        for term in self._blocked_terms:
            if term in lowered:
                return ModerationResult(allowed=False, reason=f"Conteúdo bloqueado por política interna: {term}")
        return ModerationResult(allowed=True)
