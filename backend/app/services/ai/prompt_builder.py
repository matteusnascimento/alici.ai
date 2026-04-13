from __future__ import annotations

from typing import Any


def build_chat_prompt(*, user_prompt: str, agent_system_prompt: str | None = None) -> tuple[str, str]:
    system = (
        agent_system_prompt
        or "Você é a assistente AXI da plataforma. Responda em pt-BR com clareza, objetividade e foco em execução."
    )
    return system, user_prompt


def build_agent_builder_prompt(*, context: str) -> tuple[str, str]:
    system = (
        "Gere definição de agente em JSON válido com campos: "
        "name, role, goal, tone, system_prompt, welcome_message, suggested_channels, suggested_tools."
    )
    return system, context


def build_caption_prompt(*, context: str) -> tuple[str, str]:
    return "Gere legendas de marketing em pt-BR com gancho, benefício e CTA.", context


def build_cta_prompt(*, context: str) -> tuple[str, str]:
    return "Gere CTAs curtos, diretos e orientados à conversão em pt-BR.", context


def build_ad_copy_prompt(*, context: str) -> tuple[str, str]:
    return "Gere copy de anúncio em pt-BR com proposta de valor clara e fechamento forte.", context


def build_image_analysis_prompt(*, context: str | None = None) -> tuple[str, str]:
    system = (
        "Analise a imagem e retorne descrição, tags, sugestões e contexto extraído. "
        "Seja objetivo e útil para criação de marketing."
    )
    return system, context or "Analise a imagem enviada."


def build_document_summary_prompt(*, context: str) -> tuple[str, str]:
    return (
        "Analise o documento e retorne resumo, pontos-chave, ações e FAQ em formato estruturado.",
        context,
    )


def build_workflow_prompt(*, context: str) -> tuple[str, str]:
    return (
        "Modele um workflow em JSON com trigger, conditions, actions, fallbacks e channel_targets.",
        context,
    )


def build_analytics_prompt(*, context: str) -> tuple[str, str]:
    return (
        "Converta métricas em insights executivos com warnings, oportunidades e recomendações.",
        context,
    )


def build_prompt_for_task(task_name: str, *, context: str, extra: dict[str, Any] | None = None) -> tuple[str, str]:
    extra = extra or {}
    if task_name == "agent_builder":
        return build_agent_builder_prompt(context=context)
    if task_name == "caption_generator":
        return build_caption_prompt(context=context)
    if task_name == "cta_generator":
        return build_cta_prompt(context=context)
    if task_name in {"ad_copy_generator", "social_post_generator", "product_description_generator"}:
        return build_ad_copy_prompt(context=context)
    if task_name == "document_analysis":
        return build_document_summary_prompt(context=context)
    if task_name == "workflow_builder":
        return build_workflow_prompt(context=context)
    if task_name == "analytics_insights":
        return build_analytics_prompt(context=context)
    if task_name == "platform_assistant":
        return (
            "Você é o assistente interno da AXI e deve orientar uso da plataforma com precisão.",
            context,
        )
    return build_chat_prompt(user_prompt=context, agent_system_prompt=extra.get("system_prompt"))
