"""HTML/SPA page routes."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["pages"])

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_INDEX = _PROJECT_ROOT / "frontend" / "dist" / "index.html"


def _read_spa_index() -> str:
    if _FRONTEND_INDEX.exists():
        return _FRONTEND_INDEX.read_text(encoding="utf-8")

    raise HTTPException(
        status_code=500,
        detail=(
            "Frontend React nao encontrado. Execute: "
            "cd frontend && npm install && npm run build"
        ),
    )


@router.get("/", response_class=HTMLResponse)
def home():
    return _read_spa_index()


@router.get("/login", response_class=HTMLResponse)
def login_page():
    return _read_spa_index()


@router.get("/register", response_class=HTMLResponse)
def register_page():
    return _read_spa_index()


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return RedirectResponse(url="/app/chat", status_code=307)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return RedirectResponse(url="/app/dashboard", status_code=307)


@router.get("/app", response_class=HTMLResponse)
def app_root():
    return _read_spa_index()


@router.get("/app/{path:path}", response_class=HTMLResponse)
def app_page(path: str):
    return _read_spa_index()


@router.get("/jobs", response_class=HTMLResponse)
def jobs_page():
    return RedirectResponse(url="/app/dashboard", status_code=307)
