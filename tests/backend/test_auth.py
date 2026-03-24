def test_register(client):
    response = client.post(
        '/api/auth/register',
        json={
            'name': 'Ana Silva',
            'username': 'ana',
            'email': 'ana@example.com',
            'phone': '11999999999',
            'password': 'Senha123',
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
            'password': 'Senha123',
        },
    )

    login_response = client.post('/api/auth/login', json={'email': 'ana@example.com', 'password': 'Senha123'})
    assert login_response.status_code == 200

    token = login_response.json()['access_token']
    me_response = client.get('/api/user/me', headers={'Authorization': f'Bearer {token}'})
    assert me_response.status_code == 200
    assert me_response.json()['username'] == 'ana'


def test_patch_user_me(client):
    register_response = client.post(
        '/api/auth/register',
        json={
            'name': 'Ana Silva',
            'username': 'ana',
            'email': 'ana@example.com',
            'phone': '11999999999',
            'password': 'Senha123',
        },
    )
    token = register_response.json()['access_token']

    update_response = client.patch(
        '/api/user/me',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Ana Souza', 'phone': '11888887777'},
    )

    assert update_response.status_code == 200
    assert update_response.json()['name'] == 'Ana Souza'


def test_register_weak_password(client):
    response = client.post(
        '/api/auth/register',
        json={
            'name': 'Teste',
            'username': 'teste',
            'email': 'teste@example.com',
            'password': '12345678',
        },
    )
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        '/api/auth/register',
        json={
            'name': 'Teste',
            'username': 'teste2',
            'email': 'teste2@example.com',
            'password': 'Ab1',
        },
    )
    assert response.status_code == 422


def test_new_user_plan_is_free(client):
    response = client.post(
        '/api/auth/register',
        json={
            'name': 'Novo Usuario',
            'username': 'novousr',
            'email': 'novo@example.com',
            'password': 'Senha123',
        },
    )
    assert response.status_code == 200
    assert response.json()['user']['plan'] == 'free'


def test_profile_update_cannot_change_plan(client):
    register_response = client.post(
        '/api/auth/register',
        json={
            'name': 'Ana Silva',
            'username': 'ana',
            'email': 'ana@example.com',
            'password': 'Senha123',
        },
    )
    token = register_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    update_response = client.put(
        '/api/settings/profile',
        headers=headers,
        json={
            'name': 'Ana Alterada',
            'username': 'ana',
            'email': 'ana@example.com',
            'phone': None,
            'plan': 'pro',
        },
    )
    # plan field is ignored; profile update should succeed
    assert update_response.status_code == 200
    # Plan should remain free (not changed to pro)
    me_response = client.get('/api/user/me', headers=headers)
    assert me_response.json()['plan'] == 'free'
