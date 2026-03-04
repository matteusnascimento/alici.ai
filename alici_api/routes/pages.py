"""HTML pages routes."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_template(filename: str) -> str:
    template_path = _PROJECT_ROOT / "templates" / filename
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return (
        "<html><body><h1>ALICI API</h1>"
        "<p>Template não encontrado.</p>"
        "<p>Acesse <a href='/docs'>/docs</a> para usar a API.</p>"
        "</body></html>"
    )


@router.get("/", response_class=HTMLResponse)
def home():
    # marketing landing page
    return _read_template("landing.html")


@router.get("/login", response_class=HTMLResponse)
def login_page():
    return _read_template("login.html")


@router.get("/register", response_class=HTMLResponse)
def register_page():
    return _read_template("register.html")


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return _read_template("chat.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return _read_template("dashboard.html")


@router.get("/portfolio", response_class=HTMLResponse)
def portfolio():
    return _read_template("portfolio.html")
