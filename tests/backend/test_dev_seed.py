from app.core.config import settings


def test_local_dev_user_can_login(client):
    response = client.post(
        '/api/auth/login',
        json={
            'email': settings.dev_seed_email,
            'password': settings.dev_seed_password,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['user']['email'] == settings.dev_seed_email
    assert body['user']['username'] == settings.dev_seed_username
