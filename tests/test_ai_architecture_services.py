"""Unit tests for AI architecture service abstractions."""

from app.services.model_router_service import ModelRouterService
from app.services.vector_store_service import VectorStoreService


def test_model_router_resolves_by_prefix_and_default() -> None:
    service = ModelRouterService()

    assert service.resolve_provider("gpt-4o-mini") == "openai"
    assert service.resolve_provider("claude-3-5-sonnet") == "anthropic"
    assert service.resolve_provider("gemini-1.5-flash") == "gemini"

    org_id = "org-test"
    service.set_default_provider(org_id, "mistral")
    assert service.resolve_provider("custom-model", organization_id=org_id) == "mistral"


def test_vector_store_requires_endpoint_for_managed_provider() -> None:
    service = VectorStoreService()
    org_id = "org-1"

    config = service.configure_org_provider(
        org_id,
        "pgvector",
        index_name="knowledge",
    )
    assert config["provider"] == "pgvector"
    assert config["index_name"] == "knowledge"

    try:
        service.configure_org_provider(org_id, "pinecone")
        assert False, "Expected ValueError when endpoint is missing"
    except ValueError as exc:
        assert "requires endpoint" in str(exc)
