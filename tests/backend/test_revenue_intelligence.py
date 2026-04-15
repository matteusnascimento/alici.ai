import json

from app.core.database import SessionLocal
from app.models.agent import Agent
from app.models.agent_action import AgentAction
from app.models.agent_channel import AgentChannel
from app.models.agent_conversation import AgentConversation
from app.models.agent_log import AgentLog
from app.models.user import User
from app.services.agent_runtime_service import AgentRuntimeService


def test_revenue_intelligence_snapshot(client, auth_headers):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'ana@example.com').first()
        assert user is not None

        agent = Agent(
            user_id=user.id,
            nome='Agente Receita',
            funcao='Comercial',
            tipo='sales',
            linguagem='pt-BR',
            prompt='Fechar reservas e propostas.',
            ativo=True,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

        conv_closed = AgentConversation(
            agent_id=agent.id,
            channel_type='whatsapp',
            channel_id='wa-1',
            external_user_id='Cliente Joao',
            external_conversation_id='conv-1',
            status='closed_won',
            sales_stage='fechado',
            reservation_value=980,
            lead_source='Remarketing Abril',
            is_remarketing=True,
        )
        conv_open = AgentConversation(
            agent_id=agent.id,
            channel_type='instagram',
            channel_id='ig-1',
            external_user_id='Cliente Maria',
            external_conversation_id='conv-2',
            status='proposal_sent',
            sales_stage='proposta_enviada',
            lead_source='Campanha Midia Social',
        )
        db.add_all([conv_closed, conv_open])
        db.commit()
        db.refresh(conv_closed)
        db.refresh(conv_open)

        db.add(
            AgentLog(
                agent_id=agent.id,
                conversation_id=conv_closed.id,
                event_type='message_processed',
                status='success',
                summary='Reserva fechada',
                metadata_json=json.dumps(
                    {
                        'source': 'Remarketing Abril',
                        'reservation_value': 980,
                        'actions': [
                            {'type': 'qualify_lead'},
                            {'type': 'close_reservation', 'amount': 980, 'source': 'Remarketing Abril'},
                            {'type': 'reactivate_lead'},
                        ],
                    }
                ),
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.get('/api/dashboard/revenue-intelligence?days=30', headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert body['summary']['receita_total'] >= 980
    assert body['summary']['reservas_fechadas'] >= 1
    assert body['summary']['leads_recebidos'] >= 2
    assert body['remarketing']['receita_recuperada'] >= 980
    assert len(body['funil']) == 5
    assert len(body['reservas']) >= 1
    assert any(item['label'] == 'Whatsapp' or item['label'] == 'Whatsapp' for item in body['receita_por_canal'])


def test_revenue_series_endpoint(client, auth_headers):
    response = client.get('/api/dashboard/revenue-series?days=30&granularity=daily', headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['granularity'] == 'daily'
    assert body['days'] == 30
    assert isinstance(body['points'], list)


def test_runtime_persists_structured_commercial_fields(client, auth_headers):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'ana@example.com').first()
        assert user is not None

        agent = Agent(
            user_id=user.id,
            nome='Agente Comercial',
            funcao='Conversao',
            tipo='sales',
            linguagem='pt-BR',
            prompt='Conduzir lead para fechamento.',
            ativo=True,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

        db.add(
            AgentChannel(
                user_id=user.id,
                agent_id=agent.id,
                channel_type='whatsapp',
                provider_name='whatsapp',
                channel_id='wa-comercial',
                enabled=True,
                test_mode=True,
                config_json='{}',
            )
        )

        db.add(
            AgentAction(
                user_id=user.id,
                agent_id=agent.id,
                name='Registrar venda',
                action_type='crm_event',
                trigger_keywords=None,
                config_json=json.dumps({'reservation_value': 1250, 'source': 'Remarketing VIP'}),
                enabled=True,
            )
        )
        db.commit()

        AgentRuntimeService.process_inbound_message(
            db,
            user_id=user.id,
            channel_type='whatsapp',
            channel_id='wa-comercial',
            external_user_id='cliente-123',
            external_conversation_id='conv-structured-1',
            text='Cliente pronto para fechar reserva',
            metadata={'sales_stage': 'interesse_alto', 'source': 'Remarketing VIP', 'is_remarketing': True},
            test_mode=True,
        )

        conversation = (
            db.query(AgentConversation)
            .filter(AgentConversation.agent_id == agent.id, AgentConversation.external_conversation_id == 'conv-structured-1')
            .first()
        )
        assert conversation is not None
        assert conversation.sales_stage in {'fechado', 'recuperacao'}
        assert (conversation.reservation_value or 0) >= 1250
        assert conversation.lead_source == 'Remarketing VIP'
        assert bool(conversation.is_remarketing) is True
    finally:
        db.close()
