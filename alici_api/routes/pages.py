"""HTML pages routes."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])

_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"


def _read_template(name: str) -> str:
    return (_TEMPLATES_DIR / name).read_text(encoding="utf-8")


@router.get("/", response_class=HTMLResponse)
def home():
    return _read_template("login.html")


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return _read_template("chat.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return _read_template("chat.html")
