"""
ALICI Platform - Enterprise AI Infrastructure
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api.routes import chat, agents, platform, public_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    create_tables()
    print("🚀 ALICI Platform started!")

    yield

    # Shutdown
    print("👋 ALICI Platform stopped!")


# Create FastAPI app
app = FastAPI(
    title="ALICI Platform",
    description="Enterprise AI Infrastructure with Multi-tenant Support",
    version="2.2.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")


# Frontend routes
@app.get("/")
async def landing(request: Request):
    """Landing page"""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/chat")
async def chat_ui(request: Request):
    """Chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/platform")
async def platform_ui(request: Request):
    """Platform dashboard"""
    return templates.TemplateResponse("platform.html", {"request": request})


@app.get("/dashboard")
async def dashboard_ui(request: Request):
    """Alternative dashboard route"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse("register.html", {"request": request})


# API routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(platform.router, prefix="/api/platform", tags=["platform"])
app.include_router(public_api.router, prefix="/v1", tags=["public-api"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development"
    )
