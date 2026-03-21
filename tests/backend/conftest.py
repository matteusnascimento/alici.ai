import os
import sys
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / 'test_axi.db'
os.environ['DATABASE_URL'] = f"sqlite:///{TEST_DB.as_posix()}"

BACKEND_PATH = Path(__file__).resolve().parents[2] / 'backend'
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app


def pytest_sessionstart(session):
    if TEST_DB.exists():
        TEST_DB.unlink()
    Base.metadata.create_all(bind=engine)


def pytest_sessionfinish(session, exitstatus):
    if TEST_DB.exists():
        TEST_DB.unlink()


import pytest


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
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
        'password': '12345678',
    }
    response = client.post('/api/auth/register', json=payload)
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
