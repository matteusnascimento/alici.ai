from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "alici-ai", "docs": "/docs"}


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
