from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_action import AgentAction
from app.models.agent_channel import AgentChannel
from app.models.agent_conversation import AgentConversation
from app.models.agent_knowledge import AgentKnowledge
from app.models.agent_log import AgentLog
from app.models.agent_message import AgentMessage
from app.models.widget_session import WidgetSession
from app.services.ai_service import AIService, AIServiceError


class AgentRuntimeError(Exception):
    pass


class AgentRuntimeService:
    @staticmethod
    def _json_loads(value: str | None) -> dict[str, Any]:
        if not value:
            return {}
        try:
            data = json.loads(value)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    @staticmethod
    def _select_agent_for_channel(db: Session, user_id: int, channel_type: str, channel_id: str) -> tuple[Agent, AgentChannel]:
        channel = (
            db.query(AgentChannel)
            .join(Agent, Agent.id == AgentChannel.agent_id)
            .filter(
                Agent.user_id == user_id,
                AgentChannel.channel_type == channel_type,
                AgentChannel.channel_id == channel_id,
                AgentChannel.enabled.is_(True),
                Agent.ativo.is_(True),
                Agent.archived.is_(False),
            )
            .first()
        )
        if not channel:
            raise AgentRuntimeError("Canal nao encontrado ou desabilitado")
        return channel.agent, channel

    @staticmethod
    def _get_or_create_conversation(
        db: Session,
        *,
        agent_id: int,
        channel_type: str,
        external_user_id: str,
        external_conversation_id: str,
        channel_id: str,
    ) -> AgentConversation:
        conversation = (
            db.query(AgentConversation)
            .filter(
                AgentConversation.agent_id == agent_id,
                AgentConversation.channel_type == channel_type,
                AgentConversation.external_conversation_id == external_conversation_id,
            )
            .first()
        )
        if conversation:
            return conversation

        conversation = AgentConversation(
            agent_id=agent_id,
            channel_type=channel_type,
            channel_id=channel_id,
            external_user_id=external_user_id,
            external_conversation_id=external_conversation_id,
            status="active",
        )
        db.add(conversation)
        db.flush()
        return conversation

    @staticmethod
    def _save_message(
        db: Session,
        *,
        conversation_id: int,
        role: str,
        content: str,
        message_type: str = "text",
        raw_payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentMessage:
        message = AgentMessage(
            conversation_id=conversation_id,
            role=role,
            message_type=message_type,
            content=content,
            raw_payload_json=json.dumps(raw_payload or {}, ensure_ascii=True),
            metadata_json=json.dumps(metadata or {}, ensure_ascii=True),
        )
        db.add(message)
        db.flush()
        return message

    @staticmethod
    def _log_event(
        db: Session,
        *,
        agent_id: int,
        conversation_id: int | None,
        event_type: str,
        status: str,
        summary: str,
        input_text: str | None = None,
        output_text: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        db.add(
            AgentLog(
                agent_id=agent_id,
                conversation_id=conversation_id,
                event_type=event_type,
                status=status,
                summary=summary,
                input_text=input_text,
                output_text=output_text,
                metadata_json=json.dumps(metadata or {}, ensure_ascii=True),
            )
        )

    @staticmethod
    def _knowledge_context(db: Session, user_id: int, agent_id: int) -> str:
        items = (
            db.query(AgentKnowledge)
            .filter(
                AgentKnowledge.user_id == user_id,
                AgentKnowledge.agent_id == agent_id,
                AgentKnowledge.enabled.is_(True),
            )
            .order_by(AgentKnowledge.updated_at.desc())
            .limit(8)
            .all()
        )
        if not items:
            return ""

        lines: list[str] = []
        for item in items:
            lines.append(f"[{item.kind}] {item.title}: {item.content[:300]}")
        return "\n".join(lines)

    @staticmethod
    def _build_response(agent: Agent, inbound_text: str, knowledge_context: str) -> str:
        lowered = inbound_text.strip().lower()
        if any(word in lowered for word in ["humano", "atendente", "pessoa"]):
            return "Vou transferir seu atendimento para um humano agora."

        system_parts = [
            f"Voce e o agente {agent.nome} da AXI Platform.",
            f"Funcao do agente: {agent.funcao}.",
            "Responda em pt-BR, com objetividade, clareza e foco operacional.",
        ]
        if agent.prompt:
            system_parts.append(f"Instrucoes base: {agent.prompt}")
        if knowledge_context:
            system_parts.append(f"Contexto do negocio e materiais:\n{knowledge_context}")

        try:
            return AIService().generate_text(
                system_prompt="\n\n".join(system_parts),
                user_prompt=inbound_text,
                temperature=0.4,
            )
        except AIServiceError as exc:
            raise AgentRuntimeError(exc.user_message) from exc

    @staticmethod
    def _execute_actions(db: Session, user_id: int, agent_id: int, inbound_text: str) -> list[dict[str, Any]]:
        actions = (
            db.query(AgentAction)
            .filter(
                AgentAction.user_id == user_id,
                AgentAction.agent_id == agent_id,
                AgentAction.enabled.is_(True),
            )
            .all()
        )

        lowered = inbound_text.lower()
        executed: list[dict[str, Any]] = []

        for action in actions:
            keywords = [k.strip().lower() for k in (action.trigger_keywords or "").split(",") if k.strip()]
            should_run = not keywords or any(k in lowered for k in keywords)
            if not should_run:
                continue

            result = {
                "action_id": action.id,
                "name": action.name,
                "type": action.action_type,
                "status": "executed",
            }
            executed.append(result)

        return executed

    @staticmethod
    def process_inbound_message(
        db: Session,
        *,
        user_id: int,
        channel_type: str,
        channel_id: str,
        external_user_id: str,
        external_conversation_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        start = datetime.utcnow()
        metadata = metadata or {}

        agent, _channel = AgentRuntimeService._select_agent_for_channel(db, user_id, channel_type, channel_id)
        conversation = AgentRuntimeService._get_or_create_conversation(
            db,
            agent_id=agent.id,
            channel_type=channel_type,
            external_user_id=external_user_id,
            external_conversation_id=external_conversation_id,
            channel_id=channel_id,
        )

        AgentRuntimeService._save_message(
            db,
            conversation_id=conversation.id,
            role="user",
            content=text,
            raw_payload=metadata,
            metadata=metadata,
        )

        knowledge_context = AgentRuntimeService._knowledge_context(db, user_id, agent.id)
        response_text = AgentRuntimeService._build_response(agent, text, knowledge_context)
        executed_actions = AgentRuntimeService._execute_actions(db, user_id, agent.id, text)

        if any(a["type"] == "transfer_human" for a in executed_actions) or "transferir" in response_text.lower():
            conversation.status = "handoff_human"

        AgentRuntimeService._save_message(
            db,
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            metadata={"actions": executed_actions},
        )

        elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

        AgentRuntimeService._log_event(
            db,
            agent_id=agent.id,
            conversation_id=conversation.id,
            event_type="message_processed",
            status="ok",
            summary="Mensagem processada no runtime",
            input_text=text,
            output_text=response_text,
            metadata={"elapsed_ms": elapsed_ms, "actions": executed_actions},
        )

        db.commit()

        return {
            "conversation_id": conversation.id,
            "status": conversation.status,
            "response": response_text,
            "actions": executed_actions,
        }

    @staticmethod
    def create_widget_session(db: Session, *, user_id: int, agent_id: int, visitor_id: str) -> dict[str, Any]:
        agent = (
            db.query(Agent)
            .filter(Agent.id == agent_id, Agent.user_id == user_id, Agent.ativo.is_(True), Agent.archived.is_(False))
            .first()
        )
        if not agent:
            raise AgentRuntimeError("Agente nao encontrado ou inativo")

        token_source = f"{user_id}:{agent_id}:{visitor_id}:{datetime.utcnow().isoformat()}"
        session_token = hashlib.sha256(token_source.encode("utf-8")).hexdigest()

        channel_id = f"widget:{agent_id}"
        existing_channel = (
            db.query(AgentChannel)
            .filter(
                AgentChannel.agent_id == agent_id,
                AgentChannel.channel_type == "website",
                AgentChannel.channel_id == channel_id,
            )
            .first()
        )
        if not existing_channel:
            db.add(
                AgentChannel(
                    user_id=user_id,
                    agent_id=agent_id,
                    channel_type="website",
                    provider_name="widget",
                    channel_id=channel_id,
                    enabled=True,
                    test_mode=True,
                    config_json=json.dumps({}, ensure_ascii=True),
                )
            )

        session = WidgetSession(
            agent_id=agent_id,
            channel_id=channel_id,
            visitor_id=visitor_id,
            session_token=session_token,
            external_conversation_id=session_token,
        )
        db.add(session)

        conversation = AgentRuntimeService._get_or_create_conversation(
            db,
            agent_id=agent_id,
            channel_type="website",
            external_user_id=visitor_id,
            external_conversation_id=session_token,
            channel_id=channel_id,
        )

        greeting = f"Oi! Eu sou o agente {agent.nome}. Como posso te ajudar hoje?"
        AgentRuntimeService._save_message(
            db,
            conversation_id=conversation.id,
            role="assistant",
            content=greeting,
            metadata={"kind": "greeting"},
        )

        db.commit()
        return {
            "session_token": session.session_token,
            "conversation_id": conversation.id,
            "greeting": greeting,
        }

    @staticmethod
    def widget_send_message(db: Session, *, session_token: str, text: str) -> dict[str, Any]:
        session = db.query(WidgetSession).filter(WidgetSession.session_token == session_token).first()
        if not session:
            raise AgentRuntimeError("Sessao do widget invalida")

        agent = db.query(Agent).filter(Agent.id == session.agent_id).first()
        if not agent:
            raise AgentRuntimeError("Agente da sessao nao encontrado")

        conversation = (
            db.query(AgentConversation)
            .filter(
                AgentConversation.agent_id == session.agent_id,
                AgentConversation.channel_type == "website",
                AgentConversation.external_user_id == session.visitor_id,
                AgentConversation.external_conversation_id == session_token,
            )
            .first()
        )
        if not conversation:
            raise AgentRuntimeError("Conversa do widget nao encontrada")

        result = AgentRuntimeService.process_inbound_message(
            db,
            user_id=agent.user_id,
            channel_type="website",
            channel_id=f"widget:{session.agent_id}",
            external_user_id=session.visitor_id,
            external_conversation_id=session.session_token,
            text=text,
            metadata={"source": "widget"},
        )
        return result

    @staticmethod
    def widget_get_conversation(db: Session, *, session_token: str) -> dict[str, Any]:
        session = db.query(WidgetSession).filter(WidgetSession.session_token == session_token).first()
        if not session:
            raise AgentRuntimeError("Sessao do widget invalida")

        conversation = (
            db.query(AgentConversation)
            .filter(
                AgentConversation.agent_id == session.agent_id,
                AgentConversation.channel_type == "website",
                AgentConversation.external_user_id == session.visitor_id,
                AgentConversation.external_conversation_id == session.external_conversation_id,
            )
            .first()
        )
        if not conversation:
            raise AgentRuntimeError("Conversa do widget nao encontrada")

        messages = (
            db.query(AgentMessage)
            .filter(AgentMessage.conversation_id == conversation.id)
            .order_by(AgentMessage.created_at.asc())
            .all()
        )

        return {
            "conversation_id": conversation.id,
            "status": conversation.status,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "metadata": AgentRuntimeService._json_loads(m.metadata_json),
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ],
        }

    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str, secret: str) -> bool:
        digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature)

    @staticmethod
    def analytics_for_agent(db: Session, *, user_id: int, agent_id: int) -> dict[str, Any]:
        inbound_count = (
            db.query(func.count(AgentMessage.id))
            .join(AgentConversation, AgentConversation.id == AgentMessage.conversation_id)
            .filter(AgentConversation.agent_id == agent_id, AgentMessage.role == "user")
            .scalar()
            or 0
        )

        outbound_count = (
            db.query(func.count(AgentMessage.id))
            .join(AgentConversation, AgentConversation.id == AgentMessage.conversation_id)
            .filter(AgentConversation.agent_id == agent_id, AgentMessage.role == "assistant")
            .scalar()
            or 0
        )

        total_conversations = (
            db.query(func.count(AgentConversation.id))
            .join(Agent, Agent.id == AgentConversation.agent_id)
            .filter(AgentConversation.agent_id == agent_id, Agent.user_id == user_id)
            .scalar()
            or 0
        )

        active_conversations = (
            db.query(func.count(AgentConversation.id))
            .join(Agent, Agent.id == AgentConversation.agent_id)
            .filter(
                AgentConversation.agent_id == agent_id,
                Agent.user_id == user_id,
                AgentConversation.status == "active",
            )
            .scalar()
            or 0
        )

        handoffs = (
            db.query(func.count(AgentConversation.id))
            .join(Agent, Agent.id == AgentConversation.agent_id)
            .filter(
                AgentConversation.agent_id == agent_id,
                Agent.user_id == user_id,
                AgentConversation.status == "handoff_human",
            )
            .scalar()
            or 0
        )

        actions_executed = (
            db.query(func.count(AgentLog.id))
            .filter(
                AgentLog.agent_id == agent_id,
                AgentLog.event_type == "message_processed",
            )
            .scalar()
            or 0
        )

        failed_responses = (
            db.query(func.count(AgentLog.id))
            .filter(
                AgentLog.agent_id == agent_id,
                AgentLog.status == "error",
            )
            .scalar()
            or 0
        )

        logs = (
            db.query(AgentLog)
            .filter(AgentLog.agent_id == agent_id)
            .order_by(AgentLog.created_at.desc())
            .limit(200)
            .all()
        )

        elapsed_values: list[int] = []
        for log in logs:
            value = AgentRuntimeService._json_loads(log.metadata_json).get("elapsed_ms")
            if isinstance(value, int):
                elapsed_values.append(value)

        average_response_time_ms = int(sum(elapsed_values) / len(elapsed_values)) if elapsed_values else 0

        channel_distribution_rows = (
            db.query(AgentConversation.channel_type, func.count(AgentConversation.id))
            .join(Agent, Agent.id == AgentConversation.agent_id)
            .filter(AgentConversation.agent_id == agent_id, Agent.user_id == user_id)
            .group_by(AgentConversation.channel_type)
            .all()
        )
        channel_distribution = {row[0]: int(row[1]) for row in channel_distribution_rows}

        leads_captured = 0
        for log in logs:
            metadata = AgentRuntimeService._json_loads(log.metadata_json)
            actions = metadata.get("actions")
            if isinstance(actions, list):
                for action in actions:
                    if isinstance(action, dict) and action.get("type") in {"save_lead", "qualify_lead"}:
                        leads_captured += 1

        return {
            "agent_id": agent_id,
            "total_inbound_messages": int(inbound_count),
            "total_outbound_messages": int(outbound_count),
            "total_conversations": int(total_conversations),
            "active_conversations": int(active_conversations),
            "human_handoffs": int(handoffs),
            "actions_executed": int(actions_executed),
            "failed_responses": int(failed_responses),
            "average_response_time_ms": average_response_time_ms,
            "channel_distribution": channel_distribution,
            "leads_captured": leads_captured,
        }

    @staticmethod
    def logs_for_agent(db: Session, *, user_id: int, agent_id: int, limit: int = 100) -> list[AgentLog]:
        return (
            db.query(AgentLog)
            .join(Agent, Agent.id == AgentLog.agent_id)
            .filter(AgentLog.agent_id == agent_id, Agent.user_id == user_id)
            .order_by(AgentLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def build_channel_api_key(user_id: int, agent_id: int, channel_id: str) -> str:
        raw = f"{user_id}:{agent_id}:{channel_id}:{settings.SECRET_KEY}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def validate_channel_api_key(expected: str, received: str | None) -> bool:
        if not received:
            return False
        return hmac.compare_digest(expected, received)

    @staticmethod
    def parse_json_body(raw_body: bytes) -> dict[str, Any]:
        try:
            data = json.loads(raw_body.decode("utf-8"))
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}
