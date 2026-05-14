from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatSendRequest, ChatSendResponse, ChatUploadResponse, ConversationRead, MessageRead
from app.schemas.openai_responses import AIToolRegistry, OpenAIResponsesOutput
from app.services.ai_service import AIServiceError
from app.services.billing_service import BillingService
from app.services.chat_service import ChatService
from app.services.openai_responses_service import OpenAIResponsesError

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatSendResponse)
def send_message(
    payload: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSendResponse:
    billing = BillingService(db)
    billing.check_limit(current_user, "messages")
    try:
        conversation, user_message, assistant_message = ChatService(db).send(current_user, payload)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc
    billing.log_usage(current_user.id, "messages", source="chat")
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
    current_user: User = Depends(get_current_user),
) -> ChatUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo sem nome")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio")

    max_size = 10 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo excede 10MB")

    safe_name = Path(file.filename).name.replace(" ", "_")
    ext = Path(safe_name).suffix.lower()
    allowed_extensions = {".txt", ".md", ".csv", ".json", ".pdf", ".docx"}
    if ext not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de arquivo nao permitido")

    upload_root = Path(__file__).resolve().parents[3] / "uploads" / "chat" / f"user_{current_user.id}"
    upload_root.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{ext}"
    file_path = upload_root / stored_name
    file_path.write_bytes(content)
    file_url = f"/uploads/chat/user_{current_user.id}/{stored_name}"

    return ChatUploadResponse(
        filename=file.filename,
        size=len(content),
        content_type=file.content_type,
        file_url=file_url,
        message="Arquivo armazenado com sucesso.",
    )


# ────────────────────────────────────────────────────────────────────
# Novas rotas para OpenAI Responses API
# ────────────────────────────────────────────────────────────────────


@router.post("/responses", response_model=OpenAIResponsesOutput)
def send_message_with_responses_api(
    payload: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OpenAIResponsesOutput:
    """
    Envia uma mensagem usando OpenAI Responses API.
    Suporta context injection, multi-turno e tool calling.
    """
    billing = BillingService(db)
    billing.check_limit(current_user, "messages")
    try:
        payload.use_responses_api = True
        conversation, user_message, assistant_message = ChatService(db).send(
            current_user,
            payload,
        )
    except OpenAIResponsesError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc

    billing.log_usage(current_user.id, "messages", source="chat_responses_api")

    return OpenAIResponsesOutput(
        output_text=assistant_message.text,
        conversation_id=conversation.id,
        message_id=assistant_message.id,
    )


@router.post("/agent-respond", response_model=OpenAIResponsesOutput)
def send_message_to_agent(
    payload: ChatSendRequest,
    agent_name: str = "sales",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OpenAIResponsesOutput:
    """
    Envia uma mensagem para um agente especializado.
    O agente combina instruções base + contexto especializado.
    
    Agentes disponíveis: sales, support, operations
    """
    if agent_name not in ["sales", "support", "operations"]:
        raise HTTPException(
            status_code=400,
            detail=f"Agente '{agent_name}' não encontrado. Disponíveis: sales, support, operations",
        )

    billing = BillingService(db)
    billing.check_limit(current_user, "messages")
    try:
        payload.agent_name = agent_name
        payload.use_responses_api = True
        conversation, user_message, assistant_message = ChatService(db).send(
            current_user,
            payload,
        )
    except OpenAIResponsesError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc

    billing.log_usage(current_user.id, "messages", source=f"chat_agent_{agent_name}")

    return OpenAIResponsesOutput(
        output_text=assistant_message.text,
        conversation_id=conversation.id,
        message_id=assistant_message.id,
    )


@router.get("/tools", tags=["tools"])
def list_available_tools(_: User = Depends(get_current_user)) -> dict[str, list[dict]]:
    """Lista todas as ferramentas disponíveis para a IA executar."""
    tools = []
    for tool in AIToolRegistry.list_all_tools():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                }
                for param in tool.parameters
            ],
        })

    return {"tools": tools}
