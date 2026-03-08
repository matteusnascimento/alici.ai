"""Expanded enterprise routes to close product-module gaps.

These endpoints provide compatibility paths requested by product audit,
with a standard envelope: {status, data, error}.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import APIKey, Agent, Conversation, Integration, Message, Organization, Subscription, UsageLog, User
from app.services.auth_service import AuthService

logger = logging.getLogger("alici.expansion")
router = APIRouter()

# Lightweight stores for metadata/features that do not have DB schema yet.
_CHAT_META: dict[str, dict[str, dict[str, Any]]] = {}
_MODEL_SELECTION: dict[str, str] = {}
_MODEL_JOBS: dict[str, dict[str, Any]] = {}
_TOOL_RUNS: list[dict[str, Any]] = []
_FILE_INDEX: dict[str, dict[str, Any]] = {}
_ORG_INVITES: list[dict[str, Any]] = []


class Envelope(BaseModel):
    status: str
    data: Any | None = None
    error: str | None = None


def _ok(data: Any = None) -> dict[str, Any]:
    return {"status": "success", "data": data, "error": None}


def _fail(message: str) -> dict[str, Any]:
    return {"status": "error", "data": None, "error": message}


def _log_usage(
    db: Session,
    *,
    current_user: User,
    endpoint: str,
    method: str,
    status_code: int,
    model: str = "system",
) -> None:
    log = UsageLog(
        id=str(uuid.uuid4()),
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        model=model,
        tokens_used=0,
        cost=0.0,
    )
    db.add(log)


def _chat_meta_for_user(user_id: str) -> dict[str, dict[str, Any]]:
    return _CHAT_META.setdefault(user_id, {})


class ChatCreateRequest(BaseModel):
    title: str | None = None
    agent_id: str | None = None


class ChatRenameRequest(BaseModel):
    conversation_id: str
    title: str


class ChatPinRequest(BaseModel):
    conversation_id: str
    pinned: bool = True


class ModelSelectRequest(BaseModel):
    model: str


class ModelTrainRequest(BaseModel):
    model: str
    dataset: str | None = None


class AgentCompatCreateRequest(BaseModel):
    name: str
    description: str | None = None
    system_prompt: str = "You are ALICI, a helpful assistant."
    model: str = "gpt-4o-mini"


class AgentCompatUpdateRequest(BaseModel):
    agent_id: str
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    is_active: bool | None = None


class ToolRunRequest(BaseModel):
    tool: str
    input: str | None = None


class SubscribeRequest(BaseModel):
    plan: str


class OrgCreateRequest(BaseModel):
    name: str
    slug: str | None = None


class OrgInviteRequest(BaseModel):
    email: str
    role: str = "member"


class APIKeyCreateRequest(BaseModel):
    name: str


class VoiceTTSRequest(BaseModel):
    text: str


class VoiceSTTRequest(BaseModel):
    transcript_hint: str | None = None


class VisionGenerateRequest(BaseModel):
    prompt: str


class CodeGenerateRequest(BaseModel):
    task: str
    language: str = "python"


class CodeExplainRequest(BaseModel):
    code: str


@router.post("/chat/create", response_model=Envelope)
def chat_create(
    payload: ChatCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        agent_id = payload.agent_id
        if not agent_id:
            agent = (
                db.query(Agent)
                .filter(
                    Agent.organization_id == current_user.organization_id,
                    Agent.is_active.is_(True),
                )
                .first()
            )
            if not agent:
                _log_usage(
                    db,
                    current_user=current_user,
                    endpoint="/api/chat/create",
                    method="POST",
                    status_code=400,
                )
                db.commit()
                return _fail("No active agent available")
            agent_id = agent.id

        conversation = Conversation(
            id=str(uuid.uuid4()),
            title=(payload.title or "Nova conversa").strip(),
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            agent_id=agent_id,
            is_active=True,
            last_message_at=datetime.now(timezone.utc),
        )
        db.add(conversation)
        _log_usage(
            db,
            current_user=current_user,
            endpoint="/api/chat/create",
            method="POST",
            status_code=200,
        )
        db.commit()
        db.refresh(conversation)

        return _ok(
            {
                "id": conversation.id,
                "title": conversation.title,
                "agent_id": conversation.agent_id,
                "created_at": conversation.created_at,
            }
        )
    except Exception as exc:
        logger.exception("chat_create failed")
        db.rollback()
        return _fail(str(exc))


@router.get("/chat/history", response_model=Envelope)
def chat_history(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        rows = (
            db.query(Conversation)
            .filter(
                Conversation.organization_id == current_user.organization_id,
                Conversation.user_id == current_user.id,
                Conversation.is_active.is_(True),
            )
            .order_by(Conversation.updated_at.desc().nullslast(), Conversation.created_at.desc())
            .limit(limit)
            .all()
        )
        meta = _chat_meta_for_user(current_user.id)
        data = []
        for row in rows:
            m = meta.get(row.id, {})
            data.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "pinned": bool(m.get("pinned", False)),
                    "folder": m.get("folder"),
                    "updated_at": row.updated_at,
                    "created_at": row.created_at,
                }
            )

        _log_usage(
            db,
            current_user=current_user,
            endpoint="/api/chat/history",
            method="GET",
            status_code=200,
        )
        db.commit()
        return _ok(data)
    except Exception as exc:
        logger.exception("chat_history failed")
        db.rollback()
        return _fail(str(exc))


@router.get("/chat/{conversation_id}", response_model=Envelope)
def chat_get(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == current_user.organization_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )
        if not conv:
            _log_usage(
                db,
                current_user=current_user,
                endpoint=f"/api/chat/{conversation_id}",
                method="GET",
                status_code=404,
            )
            db.commit()
            return _fail("Conversation not found")

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        meta = _chat_meta_for_user(current_user.id).get(conv.id, {})

        _log_usage(
            db,
            current_user=current_user,
            endpoint=f"/api/chat/{conversation_id}",
            method="GET",
            status_code=200,
        )
        db.commit()
        return _ok(
            {
                "id": conv.id,
                "title": conv.title,
                "pinned": bool(meta.get("pinned", False)),
                "folder": meta.get("folder"),
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at,
                    }
                    for msg in messages
                ],
            }
        )
    except Exception as exc:
        logger.exception("chat_get failed")
        db.rollback()
        return _fail(str(exc))


@router.delete("/chat/{conversation_id}", response_model=Envelope)
def chat_delete(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == current_user.organization_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )
        if not conv:
            _log_usage(
                db,
                current_user=current_user,
                endpoint=f"/api/chat/{conversation_id}",
                method="DELETE",
                status_code=404,
            )
            db.commit()
            return _fail("Conversation not found")

        db.query(Message).filter(Message.conversation_id == conv.id).delete()
        db.delete(conv)
        _chat_meta_for_user(current_user.id).pop(conversation_id, None)

        _log_usage(
            db,
            current_user=current_user,
            endpoint=f"/api/chat/{conversation_id}",
            method="DELETE",
            status_code=200,
        )
        db.commit()
        return _ok({"deleted": True, "conversation_id": conversation_id})
    except Exception as exc:
        logger.exception("chat_delete failed")
        db.rollback()
        return _fail(str(exc))


@router.patch("/chat/rename", response_model=Envelope)
def chat_rename(
    payload: ChatRenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.id == payload.conversation_id,
                Conversation.organization_id == current_user.organization_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )
        if not conv:
            _log_usage(
                db,
                current_user=current_user,
                endpoint="/api/chat/rename",
                method="PATCH",
                status_code=404,
            )
            db.commit()
            return _fail("Conversation not found")

        title = payload.title.strip()
        if not title:
            return _fail("Title is required")

        conv.title = title
        _log_usage(
            db,
            current_user=current_user,
            endpoint="/api/chat/rename",
            method="PATCH",
            status_code=200,
        )
        db.commit()
        return _ok({"conversation_id": conv.id, "title": conv.title})
    except Exception as exc:
        logger.exception("chat_rename failed")
        db.rollback()
        return _fail(str(exc))


@router.patch("/chat/pin", response_model=Envelope)
def chat_pin(
    payload: ChatPinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        conv_exists = (
            db.query(Conversation.id)
            .filter(
                Conversation.id == payload.conversation_id,
                Conversation.organization_id == current_user.organization_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )
        if not conv_exists:
            _log_usage(
                db,
                current_user=current_user,
                endpoint="/api/chat/pin",
                method="PATCH",
                status_code=404,
            )
            db.commit()
            return _fail("Conversation not found")

        user_meta = _chat_meta_for_user(current_user.id)
        current = user_meta.setdefault(payload.conversation_id, {})
        current["pinned"] = bool(payload.pinned)

        _log_usage(
            db,
            current_user=current_user,
            endpoint="/api/chat/pin",
            method="PATCH",
            status_code=200,
        )
        db.commit()
        return _ok({"conversation_id": payload.conversation_id, "pinned": current["pinned"]})
    except Exception as exc:
        logger.exception("chat_pin failed")
        db.rollback()
        return _fail(str(exc))


@router.get("/models", response_model=Envelope)
def list_models(current_user: User = Depends(AuthService.get_current_user)):
    models = [
        {"id": "gpt-4o-mini", "provider": "openai", "supports_stream": True},
        {"id": "deepseek-r1", "provider": "deepseek", "supports_stream": False},
        {"id": "alici-cpu-simple", "provider": "local", "supports_stream": False},
    ]
    return _ok({"selected": _MODEL_SELECTION.get(current_user.id, "gpt-4o-mini"), "items": models})


@router.post("/models/select", response_model=Envelope)
def select_model(payload: ModelSelectRequest, current_user: User = Depends(AuthService.get_current_user)):
    model = payload.model.strip()
    if not model:
        return _fail("Model is required")

    _MODEL_SELECTION[current_user.id] = model
    return _ok({"selected": model})


@router.post("/models/train", response_model=Envelope)
def train_model(payload: ModelTrainRequest, current_user: User = Depends(AuthService.get_current_user)):
    model = payload.model.strip()
    if not model:
        return _fail("Model is required")

    job_id = str(uuid.uuid4())
    _MODEL_JOBS[job_id] = {
        "job_id": job_id,
        "model": model,
        "dataset": payload.dataset,
        "status": "queued",
        "user_id": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return _ok(_MODEL_JOBS[job_id])


@router.get("/models/status", response_model=Envelope)
def model_status(job_id: str | None = None):
    if job_id:
        job = _MODEL_JOBS.get(job_id)
        if not job:
            return _fail("Job not found")
        return _ok(job)
    return _ok({"jobs": list(_MODEL_JOBS.values())[-20:]})


@router.post("/agents/create", response_model=Envelope)
def agent_create_compat(
    payload: AgentCompatCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        item = Agent(
            id=str(uuid.uuid4()),
            name=payload.name.strip(),
            description=(payload.description or "").strip() or None,
            system_prompt=payload.system_prompt,
            model=payload.model,
            organization_id=current_user.organization_id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return _ok({"id": item.id, "name": item.name, "model": item.model})
    except Exception as exc:
        db.rollback()
        logger.exception("agent_create_compat failed")
        return _fail(str(exc))


@router.put("/agents/update", response_model=Envelope)
def agent_update_compat(
    payload: AgentCompatUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        item = (
            db.query(Agent)
            .filter(Agent.id == payload.agent_id, Agent.organization_id == current_user.organization_id)
            .first()
        )
        if not item:
            return _fail("Agent not found")

        values = payload.model_dump(exclude_unset=True)
        values.pop("agent_id", None)
        for key, value in values.items():
            setattr(item, key, value)

        db.commit()
        return _ok({"id": item.id, "updated": True})
    except Exception as exc:
        db.rollback()
        logger.exception("agent_update_compat failed")
        return _fail(str(exc))


@router.delete("/agents/delete", response_model=Envelope)
def agent_delete_compat(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        item = (
            db.query(Agent)
            .filter(Agent.id == agent_id, Agent.organization_id == current_user.organization_id)
            .first()
        )
        if not item:
            return _fail("Agent not found")

        db.delete(item)
        db.commit()
        return _ok({"deleted": True, "agent_id": agent_id})
    except Exception as exc:
        db.rollback()
        logger.exception("agent_delete_compat failed")
        return _fail(str(exc))


@router.get("/tools", response_model=Envelope)
def list_tools(current_user: User = Depends(AuthService.get_current_user)):
    _ = current_user
    return _ok(
        {
            "tools": [
                "web_search",
                "database_query",
                "send_email",
                "execute_code",
                "http_request",
                "file_read",
                "generate_document",
            ]
        }
    )


@router.post("/tools/run", response_model=Envelope)
def run_tool(payload: ToolRunRequest, current_user: User = Depends(AuthService.get_current_user)):
    tool = payload.tool.strip().lower()
    input_text = (payload.input or "").strip()

    try:
        if tool == "web_search":
            result = {"summary": f"Resultados simulados para: {input_text}"}
        elif tool == "database_query":
            result = {"rows": [{"message": "Use endpoint SQL dedicado para consultas reais"}]}
        elif tool == "send_email":
            result = {"sent": True, "to": "masked", "note": "Simulado em ambiente local"}
        elif tool == "execute_code":
            result = {"executed": False, "reason": "Execucao arbitraria desabilitada por seguranca"}
        elif tool == "http_request":
            result = {"status_code": 200, "body": "Request stub executado"}
        elif tool == "file_read":
            target = input_text or "README.md"
            if not os.path.exists(target):
                return _fail(f"File not found: {target}")
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                result = {"path": target, "preview": f.read(4000)}
        elif tool == "generate_document":
            os.makedirs("generated/docs", exist_ok=True)
            doc_id = str(uuid.uuid4())
            path = os.path.join("generated", "docs", f"{doc_id}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(input_text or "Documento gerado pela tool")
            result = {"id": doc_id, "path": path}
        else:
            return _fail("Unknown tool")

        _TOOL_RUNS.append(
            {
                "id": str(uuid.uuid4()),
                "tool": tool,
                "user_id": current_user.id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        return _ok(result)
    except Exception as exc:
        logger.exception("run_tool failed")
        return _fail(str(exc))


@router.get("/integrations/list", response_model=Envelope)
def integrations_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    rows = (
        db.query(Integration)
        .filter(
            Integration.user_id == current_user.id,
            Integration.organization_id == current_user.organization_id,
            Integration.is_active.is_(True),
        )
        .all()
    )
    return _ok(
        [
            {
                "id": row.id,
                "type": row.type,
                "status": row.status,
                "updated_at": row.updated_at,
            }
            for row in rows
        ]
    )


@router.delete("/integrations/remove", response_model=Envelope)
def integrations_remove(
    integration_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    row = (
        db.query(Integration)
        .filter(
            Integration.user_id == current_user.id,
            Integration.organization_id == current_user.organization_id,
            Integration.type == integration_type.strip().lower(),
            Integration.is_active.is_(True),
        )
        .first()
    )
    if not row:
        return _fail("Integration not found")

    row.is_active = False
    db.commit()
    return _ok({"removed": True, "type": integration_type.strip().lower()})


@router.get("/analytics/usage", response_model=Envelope)
def analytics_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    total = (
        db.query(func.sum(UsageLog.tokens_used))
        .filter(UsageLog.organization_id == current_user.organization_id)
        .scalar()
        or 0
    )
    return _ok({"tokens_used": int(total)})


@router.get("/analytics/messages", response_model=Envelope)
def analytics_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    count = (
        db.query(func.count(Message.id))
        .join(Conversation, Conversation.id == Message.conversation_id)
        .filter(Conversation.organization_id == current_user.organization_id)
        .scalar()
        or 0
    )
    return _ok({"messages": int(count)})


@router.get("/analytics/tokens", response_model=Envelope)
def analytics_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    by_model = (
        db.query(UsageLog.model, func.sum(UsageLog.tokens_used))
        .filter(UsageLog.organization_id == current_user.organization_id)
        .group_by(UsageLog.model)
        .all()
    )
    return _ok({"by_model": [{"model": m or "unknown", "tokens": int(t or 0)} for m, t in by_model]})


@router.post("/billing/subscribe", response_model=Envelope)
def billing_subscribe(
    payload: SubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    plan = payload.plan.strip().lower()
    if plan not in {"free", "pro", "enterprise"}:
        return _fail("Invalid plan")

    current_user.organization.plan = plan
    db.commit()
    return _ok({"plan": plan, "subscribed": True})


@router.post("/billing/cancel", response_model=Envelope)
def billing_cancel(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    current_user.organization.plan = "free"
    db.commit()
    return _ok({"plan": "free", "canceled": True})


@router.get("/billing/history", response_model=Envelope)
def billing_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    rows = (
        db.query(Subscription)
        .filter(Subscription.organization_id == current_user.organization_id)
        .order_by(Subscription.created_at.desc())
        .limit(50)
        .all()
    )
    return _ok(
        [
            {
                "id": row.id,
                "plan": row.plan,
                "status": row.status,
                "current_period_start": row.current_period_start,
                "current_period_end": row.current_period_end,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    )


@router.post("/org/create", response_model=Envelope)
def org_create(
    payload: OrgCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    name = payload.name.strip()
    if not name:
        return _fail("Organization name is required")

    slug = (payload.slug or name.lower().replace(" ", "-")).strip()
    exists = db.query(Organization).filter(Organization.slug == slug).first()
    if exists:
        return _fail("Organization slug already exists")

    org = Organization(
        id=str(uuid.uuid4()),
        name=name,
        slug=slug,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    current_user.organization_id = org.id
    db.commit()

    return _ok({"id": org.id, "name": org.name, "slug": org.slug})


@router.post("/org/invite", response_model=Envelope)
def org_invite(payload: OrgInviteRequest, current_user: User = Depends(AuthService.get_current_user)):
    invite = {
        "id": str(uuid.uuid4()),
        "organization_id": current_user.organization_id,
        "email": payload.email.strip().lower(),
        "role": payload.role,
        "invited_at": datetime.now(timezone.utc).isoformat(),
    }
    _ORG_INVITES.append(invite)
    return _ok(invite)


@router.get("/org/members", response_model=Envelope)
def org_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    members = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return _ok(
        [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
            }
            for user in members
        ]
    )


@router.post("/api-keys/create", response_model=Envelope)
def create_api_key_compat(
    payload: APIKeyCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    key = AuthService.create_api_key(db, current_user.organization_id, payload.name)
    return _ok({"id": key.id, "name": key.name, "key": key.key, "created_at": key.created_at})


@router.get("/api-keys", response_model=Envelope)
def list_api_keys_compat(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    rows = (
        db.query(APIKey)
        .filter(APIKey.organization_id == current_user.organization_id, APIKey.is_active.is_(True))
        .all()
    )
    return _ok(
        [
            {
                "id": row.id,
                "name": row.name,
                "key_prefix": row.key[:12],
                "created_at": row.created_at,
            }
            for row in rows
        ]
    )


@router.delete("/api-keys/{key_id}", response_model=Envelope)
def delete_api_key_compat(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    row = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.organization_id == current_user.organization_id)
        .first()
    )
    if not row:
        return _fail("API key not found")

    row.is_active = False
    db.commit()
    return _ok({"deleted": True, "id": key_id})


@router.get("/logs", response_model=Envelope)
def list_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    rows = (
        db.query(UsageLog)
        .filter(UsageLog.organization_id == current_user.organization_id)
        .order_by(UsageLog.created_at.desc())
        .limit(100)
        .all()
    )
    return _ok(
        [
            {
                "id": row.id,
                "endpoint": row.endpoint,
                "method": row.method,
                "status_code": row.status_code,
                "model": row.model,
                "tokens_used": row.tokens_used,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    )


@router.get("/logs/errors", response_model=Envelope)
def list_error_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    rows = (
        db.query(UsageLog)
        .filter(
            UsageLog.organization_id == current_user.organization_id,
            UsageLog.status_code >= 400,
        )
        .order_by(UsageLog.created_at.desc())
        .limit(100)
        .all()
    )
    return _ok(
        [
            {
                "id": row.id,
                "endpoint": row.endpoint,
                "method": row.method,
                "status_code": row.status_code,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    )


@router.post("/files/upload", response_model=Envelope)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(AuthService.get_current_user),
):
    if not file.filename:
        return _fail("Filename is required")

    os.makedirs("generated/uploads", exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    path = os.path.join("generated", "uploads", f"{file_id}{ext}")

    payload = await file.read()
    with open(path, "wb") as f:
        f.write(payload)

    _FILE_INDEX[file_id] = {
        "id": file_id,
        "name": file.filename,
        "path": path,
        "size": len(payload),
        "owner": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return _ok(_FILE_INDEX[file_id])


@router.get("/files", response_model=Envelope)
def list_files(current_user: User = Depends(AuthService.get_current_user)):
    files = [item for item in _FILE_INDEX.values() if item["owner"] == current_user.id]
    return _ok(files)


@router.delete("/files/{file_id}", response_model=Envelope)
def delete_file(file_id: str, current_user: User = Depends(AuthService.get_current_user)):
    item = _FILE_INDEX.get(file_id)
    if not item or item["owner"] != current_user.id:
        return _fail("File not found")

    try:
        if os.path.exists(item["path"]):
            os.remove(item["path"])
    except OSError:
        logger.warning("failed to remove file path=%s", item["path"])

    _FILE_INDEX.pop(file_id, None)
    return _ok({"deleted": True, "id": file_id})


@router.post("/voice/stt", response_model=Envelope)
def voice_stt(payload: VoiceSTTRequest, current_user: User = Depends(AuthService.get_current_user)):
    _ = current_user
    transcript = payload.transcript_hint or "transcricao simulada"
    return _ok({"transcript": transcript, "confidence": 0.51})


@router.post("/voice/tts", response_model=Envelope)
def voice_tts(payload: VoiceTTSRequest, current_user: User = Depends(AuthService.get_current_user)):
    _ = current_user
    return _ok({"audio_url": f"/generated/audios/{uuid.uuid4()}.mp3", "text": payload.text})


@router.post("/vision/analyze", response_model=Envelope)
def vision_analyze(current_user: User = Depends(AuthService.get_current_user)):
    _ = current_user
    return _ok({"labels": ["document", "text"], "ocr": "resultado de OCR simulado"})


@router.post("/vision/generate", response_model=Envelope)
def vision_generate(payload: VisionGenerateRequest, current_user: User = Depends(AuthService.get_current_user)):
    _ = current_user
    return _ok({"image_url": f"/generated/images/{uuid.uuid4()}.png", "prompt": payload.prompt})


@router.post("/code/generate", response_model=Envelope)
def code_generate(payload: CodeGenerateRequest, current_user: User = Depends(AuthService.get_current_user)):
    _ = current_user
    snippet = "print('hello from ALICI')" if payload.language.lower() == "python" else "console.log('hello from ALICI');"
    return _ok({"language": payload.language, "task": payload.task, "code": snippet})


@router.post("/code/explain", response_model=Envelope)
def code_explain(payload: CodeExplainRequest, current_user: User = Depends(AuthService.get_current_user)):
    _ = current_user
    explanation = "O codigo define uma rotina simples e sem efeitos colaterais complexos."
    return _ok({"summary": explanation, "length": len(payload.code)})
