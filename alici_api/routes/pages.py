"""HTML pages routes."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from alici_api.config import get_settings

router = APIRouter(tags=["pages"])

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
settings = get_settings()


def _read_template(filename: str) -> str:
    template_path = _PROJECT_ROOT / "templates" / filename
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")

    docs_hint = (
        "<p>Acesse <a href='/docs'>/docs</a> para usar a API em desenvolvimento.</p>"
        if settings.api_docs_enabled
        else "<p>Interface temporariamente indisponivel.</p>"
    )
    return (
        "<html><body><h1>ALICI API</h1>"
        "<p>Template nao encontrado.</p>"
        f"{docs_hint}"
        "</body></html>"
    )


@router.get("/", response_class=HTMLResponse)
def home():
    return _read_template("login.html")


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return _read_template("chat.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return _read_template("chat.html")


@router.get("/jobs", response_class=HTMLResponse)
def jobs_page():
    return _read_template("jobs.html")
