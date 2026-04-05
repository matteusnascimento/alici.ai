from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatSendRequest, ChatSendResponse, ChatUploadResponse, ConversationRead, MessageRead
from app.services.ai_service import AIServiceError
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatSendResponse)
def send_message(
    payload: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSendResponse:
    try:
        conversation, user_message, assistant_message = ChatService(db).send(current_user, payload)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc
    return ChatSendResponse(
        conversation=ConversationRead.model_validate(conversation),
        user_message=MessageRead.model_validate(user_message),
        assistant_message=MessageRead.model_validate(assistant_message),
    )


@router.post("", response_model=ChatSendResponse)
def send_message_v2(
    payload: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSendResponse:
    return send_message(payload=payload, current_user=current_user, db=db)


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ConversationRead]:
    return [ConversationRead.model_validate(item) for item in ChatService(db).list_conversations(current_user)]


@router.get("/history")
def chat_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    return ChatService(db).history(current_user)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageRead]:
    return [MessageRead.model_validate(item) for item in ChatService(db).list_messages(current_user, conversation_id)]


@router.post("/upload", response_model=ChatUploadResponse)
async def upload_chat_file(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
) -> ChatUploadResponse:
    content = await file.read()
    return ChatUploadResponse(
        filename=file.filename,
        size=len(content),
        content_type=file.content_type,
        message="Arquivo recebido com sucesso.",
    )
