from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, auth, chat, dashboard, marketing, settings as settings_routes
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(marketing.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
