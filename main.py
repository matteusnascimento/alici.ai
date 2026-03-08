"""
ALICI Platform - Enterprise AI Infrastructure
"""
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api.routes import (
    agents,
    analytics,
    auth,
    billing,
    chat,
    conversations,
    expansion,
    integrations,
    knowledge,
    platform,
    public_api,
    user_settings,
    users,
)


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


class LegacyChatRequest(BaseModel):
    mensagem: str


# Frontend routes
@app.get("/")
async def landing(request: Request):
    """Landing page"""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/chat")
async def chat_ui(request: Request):
    """Chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/chat")
async def legacy_chat(payload: LegacyChatRequest):
    """Legacy compatibility endpoint used by older template variants."""
    text = (payload.mensagem or "").strip()
    if not text:
        return {"status": "error", "data": None, "error": "mensagem obrigatoria", "resposta": ""}

    resposta = f"Recebido: {text}"
    return {
        "status": "success",
        "data": {"resposta": resposta},
        "error": None,
        "resposta": resposta,
    }


@app.get("/platform")
async def platform_ui(request: Request):
    """Platform dashboard"""
    return templates.TemplateResponse("platform.html", {"request": request})


@app.get("/dashboard")
async def dashboard_ui(request: Request):
    """Alternative dashboard route"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/agents")
async def agents_page(request: Request):
    """Agent showcase and management page"""
    return templates.TemplateResponse("agents.html", {"request": request})


@app.get("/agents/create")
async def create_agent_page(request: Request):
    """Agent creation form page"""
    return templates.TemplateResponse("create_agent.html", {"request": request})


@app.get("/integrations")
async def integrations_page(request: Request):
    """Integrations catalog page"""
    return templates.TemplateResponse("integrations.html", {"request": request})


@app.get("/settings")
async def settings_page(request: Request):
    """User settings hub page"""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/health")
def health():
    """Compatibility health check endpoint."""
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    """Kubernetes/Docker health check endpoint."""
    return {"status": "ok"}


# API routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/user", tags=["user"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(platform.router, prefix="/api/platform", tags=["platform"])
app.include_router(public_api.router, prefix="/v1", tags=["public-api"])
app.include_router(user_settings.router, prefix="/api", tags=["settings"])
app.include_router(expansion.router, prefix="/api", tags=["expansion"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development"
    )
