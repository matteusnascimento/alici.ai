from datetime import datetime, timedelta, timezone

from app.models.notification import Notification
from app.models.user import User


def _current_user(db_session):
    return db_session.query(User).filter(User.email == "ana@example.com").one()


def test_system_notifications_flow(client, auth_headers, db_session):
    user = _current_user(db_session)
    db_session.add_all(
        [
            Notification(
                user_id=user.id,
                tipo="whatsapp",
                titulo="Nova mensagem no WhatsApp",
                descricao="Juliana Santos respondeu sua cotacao.",
                destino="/app/chats",
                lida=False,
                horario=datetime.now(timezone.utc),
            ),
            Notification(
                user_id=user.id,
                tipo="pagamento",
                titulo="Pagamento recebido",
                descricao="A fatura Pro foi paga com sucesso.",
                destino="/app/admin/billing",
                lida=True,
                horario=datetime.now(timezone.utc) - timedelta(hours=1),
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/notifications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data[0]["titulo"] == "Nova mensagem no WhatsApp"
    assert data[0]["destino"] == "/app/chats"
    assert data[0]["lida"] is False

    read_response = client.patch(f"/api/notifications/{data[0]['id']}/read", headers=auth_headers)
    assert read_response.status_code == 200
    assert read_response.json()["lida"] is True

    read_all_response = client.patch("/api/notifications/read-all", headers=auth_headers)
    assert read_all_response.status_code == 200
    assert all(item["lida"] for item in read_all_response.json())


def test_account_notifications_remain_preferences(client, auth_headers):
    response = client.get("/api/account/notifications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "push_notifications" in data
    assert "email_notifications" in data
    assert "titulo" not in data
