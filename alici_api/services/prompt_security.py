"""Prompt sanitization and jailbreak protection.

This layer is intentionally conservative: it catches obvious attempts to
override system instructions or exfiltrate secrets before the prompt reaches an
AI provider or consumes credits. It is not a replacement for provider-side
moderation, but it closes the common low-cost abuse paths.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from alici_api.config import get_settings


class PromptSecurityError(ValueError):
    """Raised when a prompt is unsafe or invalid."""

    def __init__(self, message: str, *, risk_score: int = 0, findings: list[str] | None = None):
        super().__init__(message)
        self.risk_score = risk_score
        self.findings = findings or []


@dataclass(frozen=True)
class PromptRule:
    name: str
    pattern: re.Pattern[str]
    weight: int


_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_EXCESSIVE_NEWLINES = re.compile(r"\n{4,}")
_EXCESSIVE_SPACES = re.compile(r"[ \t]{4,}")

_RULES: tuple[PromptRule, ...] = (
    PromptRule(
        "override_previous_instructions",
        re.compile(
            r"\b(ignore|disregard|forget|bypass|override)\b.{0,80}"
            r"\b(previous|prior|above|system|developer)\b.{0,40}"
            r"\b(instructions?|message|prompt|rules?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        2,
    ),
    PromptRule(
        "override_previous_instructions_pt",
        re.compile(
            r"\b(ignore|ignorar|desconsidere|esqueca|esqueça|burle|sobrescreva)\b.{0,80}"
            r"\b(instrucoes|instruções|mensagem|prompt|sistema|desenvolvedor|anteriores?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        2,
    ),
    PromptRule(
        "reveal_hidden_prompt",
        re.compile(
            r"\b(reveal|show|print|leak|dump|expose|display)\b.{0,80}"
            r"\b(system|developer|hidden|internal)\b.{0,40}"
            r"\b(prompt|instructions?|message|policy|rules?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        3,
    ),
    PromptRule(
        "reveal_hidden_prompt_pt",
        re.compile(
            r"\b(mostre|revele|imprima|vaze|exponha|exiba)\b.{0,80}"
            r"\b(prompt|sistema|desenvolvedor|interno|oculto|politica|política|regras?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        3,
    ),
    PromptRule(
        "secret_exfiltration",
        re.compile(
            r"\b(show|print|leak|dump|exfiltrate|return|reveal)\b.{0,80}"
            r"\b(api[_ -]?key|secret|token|password|env vars?|environment variables|credentials?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        3,
    ),
    PromptRule(
        "secret_exfiltration_pt",
        re.compile(
            r"\b(mostre|imprima|vaze|retorne|revele|exfiltre)\b.{0,80}"
            r"\b(chave|segredo|token|senha|credenciais|variaveis de ambiente|variáveis de ambiente)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        3,
    ),
    PromptRule(
        "jailbreak_persona",
        re.compile(r"\b(act as|modo|roleplay as|finja ser)\b.{0,40}\b(DAN|jailbreak|sem filtros)\b", re.IGNORECASE),
        3,
    ),
    PromptRule(
        "disable_safety",
        re.compile(
            r"\b(disable|turn off|remove|bypass|ignore|sem|desative|remova|burle)\b.{0,60}"
            r"\b(safety|guardrails?|filters?|restrictions?|policy|seguranca|segurança|filtros?|restricoes|restrições)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        2,
    ),
)


def sanitize_prompt(prompt: str, *, max_chars: int | None = None) -> str:
    settings = get_settings()
    limit = max_chars or settings.prompt_max_chars

    if not isinstance(prompt, str):
        raise PromptSecurityError("Prompt invalido")

    cleaned = _CONTROL_CHARS.sub(" ", prompt)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = _EXCESSIVE_NEWLINES.sub("\n\n\n", cleaned)
    cleaned = _EXCESSIVE_SPACES.sub("   ", cleaned)

    if not cleaned:
        raise PromptSecurityError("Prompt vazio")
    if len(cleaned) > limit:
        raise PromptSecurityError(
            f"Prompt excede o limite de {limit} caracteres",
            risk_score=1,
            findings=["max_length"],
        )

    return cleaned


def assess_prompt_risk(prompt: str) -> tuple[int, list[str]]:
    score = 0
    findings: list[str] = []

    for rule in _RULES:
        if rule.pattern.search(prompt):
            score += rule.weight
            findings.append(rule.name)

    return score, findings


def validate_prompt(prompt: str, *, purpose: str = "chat", max_chars: int | None = None) -> str:
    settings = get_settings()
    cleaned = sanitize_prompt(prompt, max_chars=max_chars)

    if not settings.prompt_security_enabled:
        return cleaned

    score, findings = assess_prompt_risk(cleaned)
    if settings.prompt_block_high_risk and score >= settings.prompt_risk_threshold:
        raise PromptSecurityError(
            "Prompt bloqueado por conter tentativa de burlar instrucoes, politicas ou segredos do sistema",
            risk_score=score,
            findings=findings,
        )

    return cleaned
