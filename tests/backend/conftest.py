import os
import sys
from pathlib import Path
from typing import Any

# Use um arquivo por processo para evitar lock compartilhado no Windows.
TEST_DB = Path(__file__).resolve().parent / f"test_axi_{os.getpid()}.db"
os.environ['DATABASE_URL'] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
# Habilitar dev seed com senha conhecida para que test_dev_seed funcione
os.environ['ENABLE_DEV_SEED_USER'] = 'true'
os.environ.setdefault('DEV_SEED_PASSWORD', 'AXITestDev123!')
# Chave fake para que _ensure_provider() nao rejeite sem chave; _post_json e mockado
os.environ.setdefault('OPENAI_API_KEY', 'test-openai-key')

BACKEND_PATH = Path(__file__).resolve().parents[2] / 'backend'
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app


def pytest_sessionstart(session):
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass
    Base.metadata.create_all(bind=engine)


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass


import pytest


def _fake_post_json(self: Any, endpoint: str, payload: dict) -> dict:
    """Mock para OpenAIService._post_json — evita chamadas reais de rede nos testes."""
    if "/chat/completions" in endpoint:
        return {
            "choices": [{"message": {"content": "Resposta de teste da IA"}, "finish_reason": "stop"}],
            "model": "gpt-4o-mini",
            "usage": {"total_tokens": 10},
        }
    if "/images/generations" in endpoint:
        return {"data": [{"b64_json": "dGVzdC1pbWFnZQ=="}]}
    # /responses (padrão para chat, structured_extract, etc.)
    return {
        "output": [{"content": [{"type": "output_text", "text": "Resposta de teste da IA"}]}],
        "model": "gpt-4o-mini",
    }


@pytest.fixture(autouse=True)
def mock_openai_network(monkeypatch):
    """Impede chamadas reais à API da OpenAI em todos os testes.

    Testes que precisam de comportamento específico da IA devem sobrescrever
    AIService.generate_text ou AIService.generate_structured_output via monkeypatch.
    """
    monkeypatch.setattr("app.services.openai_service.OpenAIService._post_json", _fake_post_json)


@pytest.fixture(autouse=True)
def reset_database():
    from app.services.dev_seed_service import DevSeedService

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        DevSeedService(db).ensure_local_dev_user()
    finally:
        db.close()
    yield
    db = SessionLocal()
    db.close()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient):
    payload = {
        'name': 'Ana Silva',
        'username': 'ana',
        'email': 'ana@example.com',
        'phone': '11999999999',
        'password': 'Senha123',
    }
    response = client.post('/api/auth/register', json=payload)
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
