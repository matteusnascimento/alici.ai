def test_register(client):
    response = client.post(
        '/api/auth/register',
        json={
            'name': 'Ana Silva',
            'username': 'ana',
            'email': 'ana@example.com',
            'phone': '11999999999',
            'password': '12345678',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['access_token']
    assert body['user']['email'] == 'ana@example.com'


def test_login_and_me(client):
    client.post(
        '/api/auth/register',
        json={
            'name': 'Ana Silva',
            'username': 'ana',
            'email': 'ana@example.com',
            'phone': '11999999999',
            'password': '12345678',
        },
    )

    login_response = client.post('/api/auth/login', json={'email': 'ana@example.com', 'password': '12345678'})
    assert login_response.status_code == 200

    token = login_response.json()['access_token']
    me_response = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me_response.status_code == 200
    assert me_response.json()['username'] == 'ana'
