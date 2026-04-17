import hashlib
import hmac
import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Request, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.integrations.channel_adapters import ChannelAdapters
from app.models.agent import Agent
from app.models.agent_action import AgentAction
from app.models.agent_channel import AgentChannel
from app.models.agent_knowledge import AgentKnowledge
from app.models.agent_log import AgentLog
from app.models.agent_configuration import AgentConfiguration
from app.models.agent_test_session import AgentTestSession
from app.models.user import User
from app.schemas.agent_runtime import (
    AgentActionCreate,
    AgentActionRead,
    AgentActionUpdate,
    AgentAnalyticsRead,
    AgentChannelCreate,
    AgentChannelRead,
    AgentChannelUpdate,
    AgentCreate,
    AgentKnowledgeCreate,
    AgentKnowledgeRead,
    AgentKnowledgeUpdate,
    AgentLogRead,
    AgentRead,
    AgentTestRequest,
    AgentTestResponse,
    AgentToggleResponse,
    ChannelApiInboundRequest,
    ChannelApiInboundResponse,
    InboundWebhookResponse,
    WidgetConversationResponse,
    WidgetMessageRequest,
    WidgetMessageResponse,
    WidgetSessionCreateRequest,
    WidgetSessionCreateResponse,
)
from app.schemas.agents_v2 import (
    AgentChannelBindingActionResponse,
    AgentChannelBindingConnectRequest,
    AgentChannelBindingDisconnectRequest,
    AgentChannelBindingRead,
    AgentChannelBindingTestRequest,
    AgentChannelConnectRequest,
    AgentChannelStatusResponse,
    AgentConnectionActionResponse,
    AgentConnectionConnectRequest,
    AgentConnectionRead,
    AgentConnectionUpdateRequest,
    AgentCreatedFlowResponse,
    AgentKnowledgeFaqRequest,
    AgentKnowledgeManualRequest,
    AgentKnowledgeSourceRequest,
    AgentKnowledgeSourceResponse,
    AgentOverviewResponse,
    AgentReadinessResponse,
    AgentRunTestRequest,
    AgentRunTestResponse,
    AgentSetupStatusResponse,
    AgentSettingsResponse,
    AgentSettingsUpdateRequest,
    AgentsImportConfigRequest,
    AgentsTemplateRead,
)
from app.services.agent_service import AgentService
from app.services.billing_service import BillingService
from app.services.agent_runtime_service import AgentRuntimeError, AgentRuntimeService
from app.services.agent_activation_service import AgentActivationService
from app.services.agent_action_service import AgentActionService
from app.services.agent_analytics_service import AgentAnalyticsService
from app.services.agent_channel_service import AgentChannelService
from app.services.agent_knowledge_service import AgentKnowledgeService
from app.services.agent_logs_service import AgentLogsService
from app.services.agent_setup_service import AgentSetupService
from app.services.agent_test_service import AgentTestService
from app.services.channel_integration_service import ChannelIntegrationService

router = APIRouter(prefix="/agents", tags=["agents"])

_KNOWLEDGE_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".json"}
_KNOWLEDGE_UPLOAD_MAX_BYTES = 10 * 1024 * 1024


def _agent_or_404(db: Session, user: User, agent_id: int) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


def _json_loads(value: str | None) -> dict:
    if not value:
        return {}
    try:
        data = json.loads(value)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def _hash_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _knowledge_storage_dir() -> Path:
    base_dir = Path(__file__).resolve().parents[3]
    path = base_dir / "uploads" / "agent_knowledge"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_filename(filename: str) -> str:
    name = Path(filename or "material").name.strip() or "material"
    return name.replace(" ", "_")


def _extract_text_for_supported_files(ext: str, content: bytes) -> str:
    if ext not in {".txt", ".csv", ".json"}:
        return ""
    for encoding in ("utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""


def _parse_bool_form(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "sim", "on"}


@router.get("", response_model=list[AgentRead])
def list_agents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentRead]:
    return [AgentRead.model_validate(item) for item in AgentService(db).list_agents(current_user)]


@router.post("", response_model=AgentRead)
def create_agent(
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRead:
    try:
        BillingService(db).check_limit(current_user, "agents")
        agent = AgentService(db).create_agent(current_user, payload)
        return AgentRead.model_validate(agent)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar agente: {error_msg}"
        )


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentRead:
    agent = AgentService(db).get_agent(current_user, agent_id)
    return AgentRead.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentRead)
def update_agent(
    agent_id: int,
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRead:
    agent = AgentService(db).update_agent(current_user, agent_id, payload)
    return AgentRead.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentRead)
def put_agent(
    agent_id: int,
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRead:
    agent = AgentService(db).update_agent(current_user, agent_id, payload)
    return AgentRead.model_validate(agent)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    AgentService(db).delete_agent(current_user, agent_id)
    return Response(status_code=204)


@router.post("/{agent_id}/toggle", response_model=AgentToggleResponse)
def toggle_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentToggleResponse:
    agent = AgentService(db).toggle_agent(current_user, agent_id)
    return AgentToggleResponse(id=agent.id, ativo=agent.ativo)


@router.post("/{agent_id}/activate", response_model=AgentRead)
def activate_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentRead:
    agent = AgentActivationService(db).activate(current_user, agent_id)
    return AgentRead.model_validate(agent)


@router.post("/{agent_id}/pause", response_model=AgentRead)
def pause_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentRead:
    agent = _agent_or_404(db, current_user, agent_id)
    agent.ativo = False
    db.commit()
    db.refresh(agent)
    return AgentRead.model_validate(agent)


@router.post("/{agent_id}/archive", response_model=AgentRead)
def archive_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentRead:
    agent = _agent_or_404(db, current_user, agent_id)
    agent.archived = True
    agent.ativo = False
    db.commit()
    db.refresh(agent)
    return AgentRead.model_validate(agent)


@router.post("/create", response_model=AgentCreatedFlowResponse)
def create_agent_alias(
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentCreatedFlowResponse:
    agent = AgentService(db).create_agent(current_user, payload)
    setup = AgentSetupService(db).get_setup_status(current_user, agent.id)
    return AgentCreatedFlowResponse.model_validate(
        {
            "agent": {
                "id": agent.id,
                "user_id": agent.user_id,
                "nome": agent.nome,
                "funcao": agent.funcao,
                "tipo": agent.tipo,
                "linguagem": agent.linguagem,
                "prompt": agent.prompt,
                "whatsapp": agent.whatsapp,
                "instagram": agent.instagram,
                "api": agent.api,
                "outros": agent.outros,
                "outros_nome": agent.outros_nome,
                "ativo": agent.ativo,
                "archived": agent.archived,
                "created_at": agent.created_at.isoformat(),
                "updated_at": agent.updated_at.isoformat(),
            },
            "setup": {
                "progress_percent": setup["progress_percent"],
                "completed_steps": setup["completed_steps"],
                "total_steps": setup["total_steps"],
                "activation_ready": setup["activation_ready"],
                "summary_message": setup["summary_message"],
                "recommended_next_step": setup["recommended_next_step"],
                "checklist": setup["checklist"],
            },
        }
    )


@router.post("/{agent_id}/duplicate", response_model=AgentRead)
def duplicate_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentRead:
    copy = AgentActivationService(db).duplicate(current_user, agent_id)
    return AgentRead.model_validate(copy)


@router.post("/{agent_id}/connect-channel")
def connect_channel(
    agent_id: int,
    payload: AgentChannelConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelStatusResponse:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint legado removido. Use /agents/{agent_id}/channels/connect com agent_channel_bindings.",
    )


@router.get("/{agent_id}/channels", response_model=list[AgentChannelBindingRead])
def list_agent_bound_channels(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AgentChannelBindingRead]:
    service = ChannelIntegrationService(db)
    bindings = service.list_agent_channels(current_user, agent_id)
    return [AgentChannelBindingRead(**service.serialize_binding(item)) for item in bindings]


@router.post("/{agent_id}/channels/connect", response_model=AgentChannelBindingRead)
def connect_agent_bound_channel(
    agent_id: int,
    payload: AgentChannelBindingConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelBindingRead:
    service = ChannelIntegrationService(db)
    binding = service.connect_agent_channel(current_user, agent_id, payload.model_dump())
    fresh = service.list_agent_channels(current_user, agent_id)
    current = next(item for item in fresh if item.id == binding.id)
    return AgentChannelBindingRead(**service.serialize_binding(current))


@router.post("/{agent_id}/channels/disconnect", response_model=AgentChannelBindingRead)
def disconnect_agent_bound_channel(
    agent_id: int,
    payload: AgentChannelBindingDisconnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelBindingRead:
    service = ChannelIntegrationService(db)
    binding = service.disconnect_agent_channel(current_user, agent_id, payload.binding_id)
    refreshed = service.list_agent_channels(current_user, agent_id)
    current = next(item for item in refreshed if item.id == binding.id)
    return AgentChannelBindingRead(**service.serialize_binding(current))


@router.post("/{agent_id}/channels/test", response_model=AgentChannelBindingActionResponse)
def test_agent_bound_channel(
    agent_id: int,
    payload: AgentChannelBindingTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelBindingActionResponse:
    result = ChannelIntegrationService(db).test_agent_channel(current_user, agent_id, payload.model_dump())
    return AgentChannelBindingActionResponse(**result)


@router.post("/{agent_id}/upload-knowledge")
def upload_knowledge(
    agent_id: int,
    payload: AgentKnowledgeSourceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeSourceResponse:
    item = AgentKnowledgeService(db).add_source(current_user, agent_id, payload.model_dump())
    return {
        "id": item.id,
        "materiais_e_informacoes_do_agente": item.title,
        "tipo": item.kind,
        "status": "Processado",
    }


@router.post("/{agent_id}/knowledge/upload-file", response_model=AgentKnowledgeRead)
async def upload_knowledge_file(
    agent_id: int,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    enabled: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeRead:
    _agent_or_404(db, current_user, agent_id)
    original_name = _safe_filename(file.filename or "material")
    ext = Path(original_name).suffix.lower()
    if ext not in _KNOWLEDGE_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato nao suportado. Use PDF, DOCX, TXT, CSV ou JSON.",
        )

    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio")
    if len(content_bytes) > _KNOWLEDGE_UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo excede 10MB")

    user_dir = _knowledge_storage_dir() / f"user_{current_user.id}" / f"agent_{agent_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{ext}"
    file_path = user_dir / stored_name
    file_path.write_bytes(content_bytes)

    preview_text = _extract_text_for_supported_files(ext, content_bytes)[:6000]
    metadata = {
        "filename": original_name,
        "stored_name": stored_name,
        "size_bytes": len(content_bytes),
        "content_type": file.content_type,
        "storage": str(file_path.relative_to(_knowledge_storage_dir().parent)).replace("\\", "/"),
        "preview": preview_text,
    }

    item = AgentKnowledgeService(db).add_source(
        current_user,
        agent_id,
        {
            "title": (title or Path(original_name).stem).strip() or "Material de arquivo",
            "kind": f"file:{ext[1:]}",
            "content": json.dumps(metadata, ensure_ascii=True),
            "tags": tags,
            "enabled": _parse_bool_form(enabled, default=True),
        },
    )
    return AgentKnowledgeRead.model_validate(item)


@router.post("/{agent_id}/knowledge/manual", response_model=AgentKnowledgeRead)
def create_manual_knowledge(
    agent_id: int,
    payload: AgentKnowledgeManualRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeRead:
    item = AgentKnowledgeService(db).create_manual_content(
        current_user,
        agent_id,
        title=payload.title,
        content=payload.content,
        tags=payload.tags,
        enabled=payload.enabled,
    )
    return AgentKnowledgeRead.model_validate(item)


@router.post("/{agent_id}/knowledge/faq", response_model=AgentKnowledgeRead)
def create_faq_knowledge(
    agent_id: int,
    payload: AgentKnowledgeFaqRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeRead:
    item = AgentKnowledgeService(db).create_faq(
        current_user,
        agent_id,
        question=payload.question,
        answer=payload.answer,
        tags=payload.tags,
        enabled=payload.enabled,
    )
    return AgentKnowledgeRead.model_validate(item)


@router.post("/{agent_id}/run-test")
def run_test(
    agent_id: int,
    payload: AgentRunTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRunTestResponse:
    try:
        return AgentTestService(db).run_test(current_user, agent_id, payload.model_dump())
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{agent_id}/overview")
def agent_overview(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentOverviewResponse:
    agent = _agent_or_404(db, current_user, agent_id)
    analytics = AgentAnalyticsService(db).overview_metrics(current_user, agent_id)
    binding_service = ChannelIntegrationService(db)
    channels = binding_service.list_agent_channels(current_user, agent_id)
    logs = AgentLogsService(db).list_logs(current_user, agent_id)[:8]
    setup = AgentSetupService(db).get_setup_status(current_user, agent_id)

    return AgentOverviewResponse(
        agent={
            "id": agent.id,
            "nome": agent.nome,
            "funcao": agent.funcao,
            "linguagem": agent.linguagem,
            "status": setup["status"],
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat(),
        },
        kpis={
            "conversas_atendidas": analytics.get("total_conversations", 0),
            "leads_capturados": analytics.get("leads_captured", 0),
            "encaminhamentos_humano": analytics.get("human_handoffs", 0),
            "tempo_medio_resposta_ms": analytics.get("average_response_time_ms", 0),
        },
        canais_ativos=[
            {
                "channel_type": item.provider,
                "status": "Conectado" if item.is_active else "Nao conectado",
            }
            for item in channels
        ],
        historico_de_atividade=logs,
        setup={
            "progress_percent": setup["progress_percent"],
            "completed_steps": setup["completed_steps"],
            "total_steps": setup["total_steps"],
            "activation_ready": setup["activation_ready"],
            "summary_message": setup["summary_message"],
            "recommended_next_step": setup["recommended_next_step"],
            "checklist": setup["checklist"],
        },
    )


@router.get("/{agent_id}/setup-status", response_model=AgentSetupStatusResponse)
def get_agent_setup_status(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentSetupStatusResponse:
    setup = AgentSetupService(db).get_setup_status(current_user, agent_id)
    return AgentSetupStatusResponse.model_validate(
        {
            "progress_percent": setup["progress_percent"],
            "completed_steps": setup["completed_steps"],
            "total_steps": setup["total_steps"],
            "activation_ready": setup["activation_ready"],
            "summary_message": setup["summary_message"],
            "recommended_next_step": setup["recommended_next_step"],
            "checklist": setup["checklist"],
        }
    )


@router.get("/{agent_id}/readiness", response_model=AgentReadinessResponse)
def get_agent_readiness(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentReadinessResponse:
    readiness = AgentSetupService(db).get_readiness(current_user, agent_id)
    return AgentReadinessResponse.model_validate(readiness)


@router.get("/{agent_id}/settings")
def get_agent_settings(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentSettingsResponse:
    agent = _agent_or_404(db, current_user, agent_id)
    cfg = db.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id, AgentConfiguration.user_id == current_user.id).first()

    if not cfg:
        return AgentSettingsResponse.model_validate(
            {
                "basic": {
                    "name": agent.nome,
                    "role": agent.funcao,
                    "language": agent.linguagem,
                    "tone": None,
                    "working_hours": None,
                    "active": agent.ativo,
                    "fallback_to_human": True,
                },
                "advanced": {
                    "modelo": agent.preferred_model,
                },
            }
        )

    return AgentSettingsResponse.model_validate(
        {
            "basic": {
                "name": agent.nome,
                "role": agent.funcao,
                "language": cfg.language,
                "tone": cfg.tone,
                "working_hours": cfg.working_hours,
                "active": agent.ativo,
                "fallback_to_human": cfg.fallback_to_human,
            },
            "advanced": {
                "instrucoes_principais_do_agente": cfg.system_instructions,
                "modelo": cfg.model_name or agent.preferred_model,
                "temperature": cfg.temperature,
                "opcoes_avancadas": _json_loads(cfg.advanced_json),
            },
        }
    )


@router.patch("/{agent_id}/settings")
def update_agent_settings(
    agent_id: int,
    payload: AgentSettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    agent = _agent_or_404(db, current_user, agent_id)
    basic = payload.basic.model_dump()
    advanced = payload.advanced.model_dump()

    if "name" in basic:
        agent.nome = str(basic["name"])
    if "role" in basic:
        agent.funcao = str(basic["role"])
    if "active" in basic:
        agent.ativo = bool(basic["active"])

    cfg = db.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id, AgentConfiguration.user_id == current_user.id).first()
    if not cfg:
        cfg = AgentConfiguration(user_id=current_user.id, agent_id=agent_id)
        db.add(cfg)

    if "language" in basic:
        cfg.language = str(basic["language"])
    if "tone" in basic:
        cfg.tone = basic["tone"]
    if "working_hours" in basic:
        cfg.working_hours = basic["working_hours"]
    if "fallback_to_human" in basic:
        cfg.fallback_to_human = bool(basic["fallback_to_human"])

    if "instrucoes_principais_do_agente" in advanced:
        cfg.system_instructions = advanced["instrucoes_principais_do_agente"]
    if "modelo" in advanced:
        cfg.model_name = advanced["modelo"]
        agent.preferred_model = advanced["modelo"]
    if "temperature" in advanced:
        cfg.temperature = str(advanced["temperature"])
    cfg.advanced_json = json.dumps(advanced.get("opcoes_avancadas") or {}, ensure_ascii=True)

    db.commit()
    return {"saved": True}


@router.put("/{agent_id}/settings")
def put_agent_settings(
    agent_id: int,
    payload: AgentSettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return update_agent_settings(agent_id, payload, current_user, db)


@router.get("/{agent_id}/metrics")
def get_agent_metrics(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    _agent_or_404(db, current_user, agent_id)
    analytics = AgentAnalyticsService(db).overview_metrics(current_user, agent_id)
    return {"metrics": analytics}


@router.post("/{agent_id}/channels/{channel_id}/connect", response_model=AgentChannelStatusResponse)
def connect_existing_channel(
    agent_id: int,
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelStatusResponse:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentChannel)
        .filter(AgentChannel.id == channel_id, AgentChannel.agent_id == agent_id, AgentChannel.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    item.enabled = True
    db.commit()
    return AgentChannelStatusResponse(
        id=item.id,
        channel_type=item.channel_type,
        channel_id=item.channel_id,
        status="Conectado",
        conexao_do_agente=item.provider_name,
    )


@router.post("/{agent_id}/channels/{channel_id}/disconnect", response_model=AgentChannelStatusResponse)
def disconnect_channel(
    agent_id: int,
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelStatusResponse:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentChannel)
        .filter(AgentChannel.id == channel_id, AgentChannel.agent_id == agent_id, AgentChannel.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    item.enabled = False
    db.commit()
    return AgentChannelStatusResponse(
        id=item.id,
        channel_type=item.channel_type,
        channel_id=item.channel_id,
        status="Nao conectado",
        conexao_do_agente=item.provider_name,
    )


@router.post("/{agent_id}/channels/{channel_id}/sync", response_model=AgentChannelStatusResponse)
def sync_channel(
    agent_id: int,
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelStatusResponse:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentChannel)
        .filter(AgentChannel.id == channel_id, AgentChannel.agent_id == agent_id, AgentChannel.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return AgentChannelStatusResponse(
        id=item.id,
        channel_type=item.channel_type,
        channel_id=item.channel_id,
        status="Sincronizando",
        conexao_do_agente=item.provider_name,
    )


@router.post("/{agent_id}/knowledge/files", response_model=AgentKnowledgeSourceResponse)
def add_knowledge_file(
    agent_id: int,
    payload: AgentKnowledgeSourceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeSourceResponse:
    return upload_knowledge(agent_id, payload, current_user, db)


@router.post("/{agent_id}/knowledge/faqs", response_model=AgentKnowledgeSourceResponse)
def add_knowledge_faq(
    agent_id: int,
    payload: AgentKnowledgeSourceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeSourceResponse:
    return upload_knowledge(agent_id, payload, current_user, db)


@router.post("/{agent_id}/knowledge/links", response_model=AgentKnowledgeSourceResponse)
def add_knowledge_link(
    agent_id: int,
    payload: AgentKnowledgeSourceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeSourceResponse:
    return upload_knowledge(agent_id, payload, current_user, db)


@router.put("/{agent_id}/knowledge/{source_id}")
def update_knowledge_source(
    agent_id: int,
    source_id: int,
    payload: AgentKnowledgeSourceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentKnowledge)
        .filter(AgentKnowledge.id == source_id, AgentKnowledge.agent_id == agent_id, AgentKnowledge.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found")
    data = payload.model_dump()
    item.title = data["title"]
    item.kind = data["kind"]
    item.content = data["content"]
    item.tags = data.get("tags")
    item.enabled = data.get("enabled", True)
    db.commit()
    return {"updated": True}


@router.delete("/{agent_id}/knowledge/{source_id}")
def delete_knowledge_source(
    agent_id: int,
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    AgentKnowledgeService(db).delete_source(current_user, agent_id, source_id)
    return {"deleted": True}


@router.post("/{agent_id}/knowledge/reprocess")
def reprocess_knowledge(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    _agent_or_404(db, current_user, agent_id)
    return {"reprocessed": True, "status": "processing"}


@router.put("/{agent_id}/actions/{action_id}")
def put_action(
    agent_id: int,
    action_id: int,
    payload: AgentActionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentActionRead:
    return update_agent_action(agent_id, action_id, payload, current_user, db)


@router.post("/{agent_id}/actions/{action_id}/enable")
def enable_action(agent_id: int, action_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentAction)
        .filter(AgentAction.id == action_id, AgentAction.agent_id == agent_id, AgentAction.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    item.enabled = True
    db.commit()
    return {"enabled": True}


@router.post("/{agent_id}/actions/{action_id}/disable")
def disable_action(agent_id: int, action_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentAction)
        .filter(AgentAction.id == action_id, AgentAction.agent_id == agent_id, AgentAction.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    item.enabled = False
    db.commit()
    return {"enabled": False}


@router.post("/{agent_id}/test/run", response_model=AgentRunTestResponse)
def run_test_session(
    agent_id: int,
    payload: AgentRunTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRunTestResponse:
    return run_test(agent_id, payload, current_user, db)


@router.get("/{agent_id}/test/sessions")
def list_test_sessions(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    items = AgentTestService(db).list_tests(current_user, agent_id)
    return [
        {
            "id": item.id,
            "scenario": item.scenario,
            "status": item.status,
            "session_summary": item.output_text[:180],
            "created_at": item.created_at.isoformat(),
        }
        for item in items
    ]


@router.get("/{agent_id}/test/sessions/{session_id}")
def get_test_session(
    agent_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return AgentTestService(db).get_test(current_user, agent_id, session_id)


@router.get("/{agent_id}/templates", response_model=list[AgentsTemplateRead])
def get_agent_templates(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentsTemplateRead]:
    _agent_or_404(db, current_user, agent_id)
    return [
        AgentsTemplateRead(
            id="support",
            nome="Atendimento Premium",
            descricao="Fluxo para suporte e duvidas frequentes.",
            funcao="Atendimento",
            objetivos=["Responder clientes", "Encaminhar para humano"],
        ),
        AgentsTemplateRead(
            id="sales",
            nome="Vendas Conversao",
            descricao="Fluxo de captacao e qualificacao de leads.",
            funcao="Vendas",
            objetivos=["Converter leads", "Gerar oportunidades"],
        ),
    ]


@router.get("/templates", response_model=list[AgentsTemplateRead])
def get_global_agent_templates() -> list[AgentsTemplateRead]:
    return [
        AgentsTemplateRead(
            id="support",
            nome="Atendimento Premium",
            descricao="Fluxo para suporte e duvidas frequentes.",
            funcao="Atendimento",
            objetivos=["Responder clientes", "Encaminhar para humano"],
        ),
        AgentsTemplateRead(
            id="sales",
            nome="Vendas Conversao",
            descricao="Fluxo de captacao e qualificacao de leads.",
            funcao="Vendas",
            objetivos=["Converter leads", "Gerar oportunidades"],
        ),
    ]


@router.post("/import-config", response_model=AgentRead)
def import_agent_config(
    payload: AgentsImportConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRead:
    agent = AgentService(db).create_agent(
        current_user,
        AgentCreate(
            nome=payload.nome,
            funcao=payload.funcao,
            tipo=payload.tipo,
            linguagem=payload.linguagem,
            prompt=payload.prompt,
            ativo=False,
        ),
    )

    channel_service = AgentChannelService(db)
    knowledge_service = AgentKnowledgeService(db)
    action_service = AgentActionService(db)

    for channel in payload.channels:
        channel_service.connect_channel(
            current_user,
            agent.id,
            {
                "channel_type": channel.get("channel_type", "website"),
                "provider_name": channel.get("provider_name", "internal"),
                "channel_id": channel.get("channel_id", f"import:{agent.id}:{channel.get('channel_type', 'website')}"),
                "enabled": bool(channel.get("enabled", True)),
                "test_mode": bool(channel.get("test_mode", True)),
                "config": channel.get("config", {}),
            },
        )

    for source in payload.knowledge:
        knowledge_service.add_source(
            current_user,
            agent.id,
            {
                "title": source.get("title", "Fonte importada"),
                "kind": source.get("kind", "note"),
                "content": source.get("content", ""),
                "tags": source.get("tags"),
                "enabled": bool(source.get("enabled", True)),
            },
        )

    for action in payload.actions:
        action_service.add_or_update_action(
            current_user,
            agent.id,
            {
                "name": action.get("name", "Acao importada"),
                "action_type": action.get("action_type", "custom"),
                "trigger_keywords": action.get("trigger_keywords"),
                "config": action.get("config", {}),
                "enabled": bool(action.get("enabled", True)),
            },
        )

    return AgentRead.model_validate(agent)


@router.get("/{agent_id}/channels/registry", response_model=list[AgentChannelRead])
def list_agent_channels(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentChannelRead]:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint legado removido. Use /agents/{agent_id}/channels.",
    )


@router.post("/{agent_id}/channels/registry", response_model=AgentChannelRead)
def create_agent_channel(
    agent_id: int,
    payload: AgentChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelRead:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint legado removido. Use /agents/{agent_id}/channels/connect.",
    )


@router.patch("/{agent_id}/channels/registry/{channel_id}", response_model=AgentChannelRead)
def update_agent_channel(
    agent_id: int,
    channel_id: int,
    payload: AgentChannelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelRead:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint legado removido. Use /agents/{agent_id}/channels/disconnect e /channels/connect.",
    )


@router.get("/{agent_id}/knowledge", response_model=list[AgentKnowledgeRead])
def list_agent_knowledge(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentKnowledgeRead]:
    _agent_or_404(db, current_user, agent_id)
    items = (
        db.query(AgentKnowledge)
        .filter(AgentKnowledge.user_id == current_user.id, AgentKnowledge.agent_id == agent_id)
        .order_by(AgentKnowledge.updated_at.desc())
        .all()
    )
    return [AgentKnowledgeRead.model_validate(item) for item in items]


@router.post("/{agent_id}/knowledge", response_model=AgentKnowledgeRead)
def create_agent_knowledge(
    agent_id: int,
    payload: AgentKnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeRead:
    _agent_or_404(db, current_user, agent_id)
    item = AgentKnowledge(user_id=current_user.id, agent_id=agent_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return AgentKnowledgeRead.model_validate(item)


@router.patch("/{agent_id}/knowledge/{knowledge_id}", response_model=AgentKnowledgeRead)
def update_agent_knowledge(
    agent_id: int,
    knowledge_id: int,
    payload: AgentKnowledgeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentKnowledgeRead:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentKnowledge)
        .filter(AgentKnowledge.id == knowledge_id, AgentKnowledge.user_id == current_user.id, AgentKnowledge.agent_id == agent_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return AgentKnowledgeRead.model_validate(item)


@router.get("/{agent_id}/actions", response_model=list[AgentActionRead])
def list_agent_actions(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentActionRead]:
    _agent_or_404(db, current_user, agent_id)
    items = (
        db.query(AgentAction)
        .filter(AgentAction.user_id == current_user.id, AgentAction.agent_id == agent_id)
        .order_by(AgentAction.updated_at.desc())
        .all()
    )
    return [
        AgentActionRead(
            id=item.id,
            agent_id=item.agent_id,
            name=item.name,
            action_type=item.action_type,
            trigger_keywords=item.trigger_keywords,
            config=_json_loads(item.config_json),
            enabled=item.enabled,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in items
    ]


@router.post("/{agent_id}/actions", response_model=AgentActionRead)
def create_agent_action(
    agent_id: int,
    payload: AgentActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentActionRead:
    _agent_or_404(db, current_user, agent_id)
    item = AgentAction(
        user_id=current_user.id,
        agent_id=agent_id,
        name=payload.name,
        action_type=payload.action_type,
        trigger_keywords=payload.trigger_keywords,
        config_json=json.dumps(payload.config, ensure_ascii=True),
        enabled=payload.enabled,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return AgentActionRead(
        id=item.id,
        agent_id=item.agent_id,
        name=item.name,
        action_type=item.action_type,
        trigger_keywords=item.trigger_keywords,
        config=_json_loads(item.config_json),
        enabled=item.enabled,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.patch("/{agent_id}/actions/{action_id}", response_model=AgentActionRead)
def update_agent_action(
    agent_id: int,
    action_id: int,
    payload: AgentActionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentActionRead:
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentAction)
        .filter(AgentAction.id == action_id, AgentAction.user_id == current_user.id, AgentAction.agent_id == agent_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")

    data = payload.model_dump(exclude_unset=True)
    if "config" in data:
        item.config_json = json.dumps(data.pop("config") or {}, ensure_ascii=True)
    for key, value in data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return AgentActionRead(
        id=item.id,
        agent_id=item.agent_id,
        name=item.name,
        action_type=item.action_type,
        trigger_keywords=item.trigger_keywords,
        config=_json_loads(item.config_json),
        enabled=item.enabled,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("/{agent_id}/test", response_model=AgentTestResponse)
def test_agent(
    agent_id: int,
    payload: AgentTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentTestResponse:
    agent = _agent_or_404(db, current_user, agent_id)
    channel_id = f"test:{agent_id}:{payload.channel_type}"
    existing = (
        db.query(AgentChannel)
        .filter(
            AgentChannel.user_id == current_user.id,
            AgentChannel.agent_id == agent_id,
            AgentChannel.channel_type == payload.channel_type,
            AgentChannel.channel_id == channel_id,
        )
        .first()
    )
    if not existing:
        db.add(
            AgentChannel(
                user_id=current_user.id,
                agent_id=agent_id,
                channel_type=payload.channel_type,
                provider_name="internal-test",
                channel_id=channel_id,
                enabled=True,
                test_mode=True,
                config_json=json.dumps({}, ensure_ascii=True),
            )
        )
        db.commit()

    was_active = bool(agent.ativo)
    if not was_active:
        agent.ativo = True
        db.flush()

    try:
        try:
            result = AgentRuntimeService.process_inbound_message(
                db,
                user_id=current_user.id,
                channel_type=payload.channel_type,
                channel_id=channel_id,
                external_user_id=f"tester:{current_user.id}",
                external_conversation_id=f"test-conv:{agent_id}",
                text=payload.text,
                metadata={"source": "agent-test"},
                test_mode=True,
            )
        except AgentRuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        if not was_active:
            agent.ativo = False
            db.commit()

    return AgentTestResponse(**result)


@router.get("/{agent_id}/logs", response_model=list[AgentLogRead])
def get_agent_logs(
    agent_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AgentLogRead]:
    _agent_or_404(db, current_user, agent_id)
    logs = AgentRuntimeService.logs_for_agent(db, user_id=current_user.id, agent_id=agent_id, limit=min(limit, 500))
    return [
        AgentLogRead(
            id=log.id,
            agent_id=log.agent_id,
            conversation_id=log.conversation_id,
            event_type=log.event_type,
            status=log.status,
            summary=log.summary,
            input_text=log.input_text,
            output_text=log.output_text,
            metadata=_json_loads(log.metadata_json),
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.get("/{agent_id}/analytics", response_model=AgentAnalyticsRead)
def get_agent_analytics(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentAnalyticsRead:
    _agent_or_404(db, current_user, agent_id)
    analytics = AgentRuntimeService.analytics_for_agent(db, user_id=current_user.id, agent_id=agent_id)
    return AgentAnalyticsRead(**analytics)


@router.post("/runtime/widget/session", response_model=WidgetSessionCreateResponse)
def create_widget_session(
    payload: WidgetSessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WidgetSessionCreateResponse:
    try:
        result = AgentRuntimeService.create_widget_session(
            db,
            user_id=current_user.id,
            agent_id=payload.agent_id,
            visitor_id=payload.visitor_id,
        )
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return WidgetSessionCreateResponse(**result)


@router.post("/runtime/widget/message", response_model=WidgetMessageResponse)
def widget_send_message(payload: WidgetMessageRequest, db: Session = Depends(get_db)) -> WidgetMessageResponse:
    try:
        result = AgentRuntimeService.widget_send_message(db, session_token=payload.session_token, text=payload.text)
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return WidgetMessageResponse(
        conversation_id=result["conversation_id"],
        response=result["response"],
        status=result["status"],
    )


@router.get("/runtime/widget/conversation/{session_token}", response_model=WidgetConversationResponse)
def widget_get_conversation(session_token: str, db: Session = Depends(get_db)) -> WidgetConversationResponse:
    try:
        result = AgentRuntimeService.widget_get_conversation(db, session_token=session_token)
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return WidgetConversationResponse(**result)


@router.post("/runtime/channel-api/inbound", response_model=ChannelApiInboundResponse)
def channel_api_inbound(
    payload: ChannelApiInboundRequest,
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> ChannelApiInboundResponse:
    channel = db.query(AgentChannel).filter(AgentChannel.channel_id == payload.channel_id, AgentChannel.enabled.is_(True)).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    if not channel.api_key_hash or not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
    if not hmac.compare_digest(channel.api_key_hash, _hash_key(x_api_key)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    try:
        result = AgentRuntimeService.process_inbound_message(
            db,
            user_id=channel.user_id,
            channel_type=channel.channel_type,
            channel_id=channel.channel_id,
            external_user_id=payload.external_user_id,
            external_conversation_id=payload.external_conversation_id,
            text=payload.text,
            metadata=payload.metadata,
        )
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ChannelApiInboundResponse(
        conversation_id=result["conversation_id"],
        response=result["response"],
        status=result["status"],
    )


@router.post("/runtime/webhooks/whatsapp", response_model=InboundWebhookResponse)
async def webhook_whatsapp(request: Request, db: Session = Depends(get_db)) -> InboundWebhookResponse:
    body = await request.body()
    payload = AgentRuntimeService.parse_json_body(body)
    normalized = ChannelAdapters.normalize_whatsapp(payload)

    channel = (
        db.query(AgentChannel)
        .filter(
            AgentChannel.channel_type == "whatsapp",
            AgentChannel.channel_id == normalized["channel_id"],
            AgentChannel.enabled.is_(True),
        )
        .first()
    )
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WhatsApp channel not found")

    try:
        AgentRuntimeService.process_inbound_message(
            db,
            user_id=channel.user_id,
            channel_type="whatsapp",
            channel_id=normalized["channel_id"],
            external_user_id=normalized["external_user_id"],
            external_conversation_id=normalized["external_conversation_id"],
            text=normalized["text"],
            metadata=normalized["metadata"],
        )
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return InboundWebhookResponse(ok=True, detail="whatsapp processed")


@router.post("/runtime/webhooks/instagram", response_model=InboundWebhookResponse)
async def webhook_instagram(request: Request, db: Session = Depends(get_db)) -> InboundWebhookResponse:
    body = await request.body()
    payload = AgentRuntimeService.parse_json_body(body)
    normalized = ChannelAdapters.normalize_instagram(payload)

    channel = (
        db.query(AgentChannel)
        .filter(
            AgentChannel.channel_type == "instagram",
            AgentChannel.channel_id == normalized["channel_id"],
            AgentChannel.enabled.is_(True),
        )
        .first()
    )
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instagram channel not found")

    try:
        AgentRuntimeService.process_inbound_message(
            db,
            user_id=channel.user_id,
            channel_type="instagram",
            channel_id=normalized["channel_id"],
            external_user_id=normalized["external_user_id"],
            external_conversation_id=normalized["external_conversation_id"],
            text=normalized["text"],
            metadata=normalized["metadata"],
        )
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return InboundWebhookResponse(ok=True, detail="instagram processed")


# =============================================================================
# Connections API — gerencia integrações por provider
# =============================================================================

def _mark_connections_deprecated(response: Response) -> None:
    response.headers["Deprecation"] = "true"
    response.headers["X-API-Deprecated"] = "connections"
    response.headers["X-API-Replacement"] = "Use /agents/{agent_id}/channels* endpoints"

@router.get("/{agent_id}/connections", response_model=list[AgentConnectionRead])
def list_connections(
    agent_id: int,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AgentConnectionRead]:
    _mark_connections_deprecated(response)
    rows = AgentChannelService(db).get_connections(current_user, agent_id)
    return [AgentConnectionRead.from_orm(item) for item in rows]


@router.post("/{agent_id}/connections/{provider}/connect", response_model=AgentConnectionRead)
def connect_provider(
    agent_id: int,
    provider: str,
    payload: AgentConnectionConnectRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentConnectionRead:
    _mark_connections_deprecated(response)
    item = AgentChannelService(db).connect_provider(current_user, agent_id, provider, payload.config or {})
    return AgentConnectionRead.from_orm(item)


@router.post("/{agent_id}/connections/{provider}/disconnect", response_model=AgentConnectionRead)
def disconnect_provider(
    agent_id: int,
    provider: str,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentConnectionRead:
    _mark_connections_deprecated(response)
    item = AgentChannelService(db).disconnect_provider(current_user, agent_id, provider)
    return AgentConnectionRead.from_orm(item)


@router.post("/{agent_id}/connections/{provider}/sync", response_model=AgentConnectionRead)
def sync_provider(
    agent_id: int,
    provider: str,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentConnectionRead:
    _mark_connections_deprecated(response)
    item = AgentChannelService(db).sync_provider(current_user, agent_id, provider)
    return AgentConnectionRead.from_orm(item)


@router.post("/{agent_id}/connections/{provider}/test", response_model=AgentConnectionActionResponse)
def test_provider(
    agent_id: int,
    provider: str,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentConnectionActionResponse:
    _mark_connections_deprecated(response)
    result = AgentChannelService(db).test_provider(current_user, agent_id, provider)
    return AgentConnectionActionResponse(
        success=bool(result.get("success")),
        message=str(result.get("message") or "Teste de conexao executado."),
        data=result.get("data") or {},
        channel_type=str(result.get("channel_type") or provider),
    )


@router.put("/{agent_id}/connections/{provider}", response_model=AgentConnectionRead)
def update_provider_config(
    agent_id: int,
    provider: str,
    payload: AgentConnectionUpdateRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentConnectionRead:
    _mark_connections_deprecated(response)
    item = AgentChannelService(db).update_provider_config(current_user, agent_id, provider, payload.model_dump(exclude_none=True))
    return AgentConnectionRead.from_orm(item)
