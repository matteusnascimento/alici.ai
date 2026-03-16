from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import generate

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
async def chat(request: ChatRequest):
    response = generate(request.message)
    return {"response": response}