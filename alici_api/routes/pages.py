"""HTML pages routes."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def home():
    with open("templates/login.html", "r", encoding="utf-8") as file:
        return file.read()


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        return file.read()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        return file.read()
