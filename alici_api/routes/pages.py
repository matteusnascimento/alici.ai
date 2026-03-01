"""HTML pages routes."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])


def _read_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@router.get("/", response_class=HTMLResponse)
def home():
    return _read_template("templates/landing.html")


@router.get("/login", response_class=HTMLResponse)
def login_page():
    return _read_template("templates/login.html")


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return _read_template("templates/dashboard.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return _read_template("templates/dashboard.html")
