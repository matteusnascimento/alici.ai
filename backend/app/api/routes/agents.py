import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
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
    AgentCreatedFlowResponse,
    AgentChannelConnectRequest,
    AgentChannelStatusResponse,
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
from app.services.agent_runtime_service import AgentRuntimeError, AgentRuntimeService
from app.services.agent_activation_service import AgentActivationService
from app.services.agent_action_service import AgentActionService
from app.services.agent_analytics_service import AgentAnalyticsService
from app.services.agent_channel_service import AgentChannelService
from app.services.agent_knowledge_service import AgentKnowledgeService
from app.services.agent_logs_service import AgentLogsService
from app.services.agent_setup_service import AgentSetupService
from app.services.agent_test_service import AgentTestService

router = APIRouter(prefix="/agents", tags=["agents"])


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


@router.get("", response_model=list[AgentRead])
def list_agents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentRead]:
    return [AgentRead.model_validate(item) for item in AgentService(db).list_agents(current_user)]


@router.post("", response_model=AgentRead)
def create_agent(
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRead:
    agent = AgentService(db).create_agent(current_user, payload)
    return AgentRead.model_validate(agent)


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
    item = AgentChannelService(db).connect_channel(current_user, agent_id, payload.model_dump())
    return {
        "id": item.id,
        "channel_type": item.channel_type,
        "channel_id": item.channel_id,
        "status": "Conectado" if item.enabled else "Nao conectado",
        "conexao_do_agente": item.provider_name,
    }


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
    channels = AgentChannelService(db).list_channels(current_user, agent_id)
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
                "channel_type": item.channel_type,
                "status": "Conectado" if item.enabled else "Nao conectado",
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
        return AgentSettingsResponse.model_validate({
            "basic": {
                "name": agent.nome,
                "role": agent.funcao,
                "language": agent.linguagem,
                "tone": None,
                "working_hours": None,
                "active": agent.ativo,
                "fallback_to_human": True,
            },
            "advanced": {},
        })

    return AgentSettingsResponse.model_validate({
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
            "modelo": cfg.model_name,
            "temperature": cfg.temperature,
            "opcoes_avancadas": _json_loads(cfg.advanced_json),
        },
    })


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
    _agent_or_404(db, current_user, agent_id)
    item = (
        db.query(AgentKnowledge)
        .filter(AgentKnowledge.id == source_id, AgentKnowledge.agent_id == agent_id, AgentKnowledge.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found")
    db.delete(item)
    db.commit()
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


@router.get("/{agent_id}/channels", response_model=list[AgentChannelRead])
def list_agent_channels(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentChannelRead]:
    _agent_or_404(db, current_user, agent_id)
    items = (
        db.query(AgentChannel)
        .filter(AgentChannel.user_id == current_user.id, AgentChannel.agent_id == agent_id)
        .order_by(AgentChannel.created_at.desc())
        .all()
    )
    return [
        AgentChannelRead(
            id=item.id,
            agent_id=item.agent_id,
            channel_type=item.channel_type,
            provider_name=item.provider_name,
            external_account_id=item.external_account_id,
            channel_id=item.channel_id,
            credential_ref=item.credential_ref,
            enabled=item.enabled,
            test_mode=item.test_mode,
            config=_json_loads(item.config_json),
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in items
    ]


@router.post("/{agent_id}/channels", response_model=AgentChannelRead)
def create_agent_channel(
    agent_id: int,
    payload: AgentChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelRead:
    _agent_or_404(db, current_user, agent_id)
    api_key = payload.api_key or AgentRuntimeService.build_channel_api_key(current_user.id, agent_id, payload.channel_id)
    channel = AgentChannel(
        user_id=current_user.id,
        agent_id=agent_id,
        channel_type=payload.channel_type,
        provider_name=payload.provider_name,
        external_account_id=payload.external_account_id,
        channel_id=payload.channel_id,
        credential_ref=payload.credential_ref,
        api_key_hash=_hash_key(api_key),
        enabled=payload.enabled,
        test_mode=payload.test_mode,
        config_json=json.dumps(payload.config, ensure_ascii=True),
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return AgentChannelRead(
        id=channel.id,
        agent_id=channel.agent_id,
        channel_type=channel.channel_type,
        provider_name=channel.provider_name,
        external_account_id=channel.external_account_id,
        channel_id=channel.channel_id,
        credential_ref=channel.credential_ref,
        enabled=channel.enabled,
        test_mode=channel.test_mode,
        config=_json_loads(channel.config_json),
        created_at=channel.created_at,
        updated_at=channel.updated_at,
    )


@router.patch("/{agent_id}/channels/{channel_id}", response_model=AgentChannelRead)
def update_agent_channel(
    agent_id: int,
    channel_id: int,
    payload: AgentChannelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentChannelRead:
    _agent_or_404(db, current_user, agent_id)
    channel = (
        db.query(AgentChannel)
        .filter(AgentChannel.id == channel_id, AgentChannel.user_id == current_user.id, AgentChannel.agent_id == agent_id)
        .first()
    )
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    data = payload.model_dump(exclude_unset=True)
    if "config" in data:
        channel.config_json = json.dumps(data.pop("config") or {}, ensure_ascii=True)
    if "api_key" in data and data["api_key"]:
        channel.api_key_hash = _hash_key(data.pop("api_key"))
    else:
        data.pop("api_key", None)

    for key, value in data.items():
        setattr(channel, key, value)

    db.commit()
    db.refresh(channel)
    return AgentChannelRead(
        id=channel.id,
        agent_id=channel.agent_id,
        channel_type=channel.channel_type,
        provider_name=channel.provider_name,
        external_account_id=channel.external_account_id,
        channel_id=channel.channel_id,
        credential_ref=channel.credential_ref,
        enabled=channel.enabled,
        test_mode=channel.test_mode,
        config=_json_loads(channel.config_json),
        created_at=channel.created_at,
        updated_at=channel.updated_at,
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
    _agent_or_404(db, current_user, agent_id)
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
        )
    except AgentRuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

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
