def test_account_profile_and_preferences_flow(client, auth_headers):
    profile_response = client.get('/api/account/profile', headers=auth_headers)
    assert profile_response.status_code == 200
    assert profile_response.json()['email'] == 'ana@example.com'

    updated_profile = {
        'name': 'Ana Souza',
        'username': 'ana.souza',
        'email': 'ana.souza@example.com',
        'phone': '11988887777',
        'avatar_url': 'https://cdn.axi.app/avatar.png',
        'bio': 'Especialista em atendimento.',
    }
    update_response = client.put('/api/account/profile', headers=auth_headers, json=updated_profile)
    assert update_response.status_code == 200
    assert update_response.json()['username'] == 'ana.souza'

    preferences_payload = {
        'language': 'pt-BR',
        'voice': 'feminina',
        'theme_mode': 'light',
        'accent_color': '#0ea5e9',
        'haptic_feedback': True,
        'background_conversation': True,
        'autocomplete': True,
        'trending': False,
        'sequence': True,
        'split_mode': False,
    }
    preferences_response = client.put('/api/account/preferences', headers=auth_headers, json=preferences_payload)
    assert preferences_response.status_code == 200
    assert preferences_response.json()['accent_color'] == '#0ea5e9'

    notifications_payload = {
        'notifications_enabled': True,
        'email_notifications': True,
        'push_notifications': False,
        'product_updates': True,
        'marketing_notifications': False,
        'security_alerts': True,
    }
    notifications_response = client.put('/api/account/notifications', headers=auth_headers, json=notifications_payload)
    assert notifications_response.status_code == 200
    assert notifications_response.json()['marketing_notifications'] is False


def test_account_profile_conflict_and_phone_validation(client, auth_headers):
    client.post(
        '/api/auth/register',
        json={
            'name': 'Joao',
            'username': 'joao',
            'email': 'joao@example.com',
            'phone': '11977776666',
            'password': 'Senha123',
        },
    )

    conflict_response = client.put(
        '/api/account/profile',
        headers=auth_headers,
        json={
            'name': 'Ana Silva',
            'username': 'joao',
            'email': 'ana@example.com',
            'phone': '11999999999',
            'avatar_url': None,
            'bio': None,
        },
    )
    assert conflict_response.status_code == 409
    assert 'ja esta em uso' in conflict_response.json().get('detail', '').lower()

    phone_response = client.put(
        '/api/account/profile',
        headers=auth_headers,
        json={
            'name': 'Ana Silva',
            'username': 'ana',
            'email': 'ana@example.com',
            'phone': '1234567',
            'avatar_url': None,
            'bio': None,
        },
    )
    assert phone_response.status_code == 422
    assert 'telefone deve ter pelo menos 8 digitos' in phone_response.json().get('detail', '').lower()


def test_account_security_integrations_and_privacy_actions(client, auth_headers):
    integrations_response = client.get('/api/account/integrations', headers=auth_headers)
    assert integrations_response.status_code == 200
    providers = {item['provider'] for item in integrations_response.json()}
    assert {'openai', 'whatsapp', 'instagram', 'website'}.issubset(providers)

    disable_response = client.put('/api/account/integrations/openai', headers=auth_headers, json={'enabled': False})
    assert disable_response.status_code == 200
    assert disable_response.json()['status'] == 'disconnected'

    change_password_response = client.post(
        '/api/account/security/change-password',
        headers=auth_headers,
        json={
            'current_password': 'Senha123',
            'new_password': 'SenhaNova123',
            'confirm_password': 'SenhaNova123',
        },
    )
    assert change_password_response.status_code == 200

    login_response = client.post('/api/auth/login', json={'email': 'ana@example.com', 'password': 'SenhaNova123'})
    assert login_response.status_code == 200

    invalid_current_response = client.post(
        '/api/account/security/change-password',
        headers={'Authorization': f"Bearer {login_response.json()['access_token']}"},
        json={
            'current_password': 'senha-invalida',
            'new_password': 'OutraSenha123',
            'confirm_password': 'OutraSenha123',
        },
    )
    assert invalid_current_response.status_code == 401
    assert 'senha atual invalida' in invalid_current_response.json().get('detail', '').lower()

    export_response = client.post('/api/account/privacy/export', headers=auth_headers)
    assert export_response.status_code == 200
    assert 'solicitacao de exportacao registrada' in export_response.json().get('message', '').lower()

    delete_response = client.post('/api/account/privacy/delete-request', headers=auth_headers)
    assert delete_response.status_code == 200
    assert 'solicitacao de exclusao recebida' in delete_response.json().get('message', '').lower()

    logout_response = client.post('/api/account/logout', headers=auth_headers)
    assert logout_response.status_code == 200
    assert 'sessao encerrada com sucesso' in logout_response.json().get('message', '').lower()


def test_account_avatar_upload(client, auth_headers):
    """Test avatar upload endpoint"""
    from io import BytesIO

    # Criar dados PNG simples (1x1 pixel válido)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x05\x18\r\n\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    # Upload com tipo MIME correto
    response = client.post(
        '/api/account/upload-avatar',
        headers=auth_headers,
        files={'file': ('avatar.png', BytesIO(png_data), 'image/png')},
    )
    assert response.status_code == 200
    data = response.json()
    assert 'avatar_url' in data
    assert data['avatar_url'].startswith('/uploads/avatars/')

    # Tentar upload com tipo de arquivo inválido
    invalid_response = client.post(
        '/api/account/upload-avatar',
        headers=auth_headers,
        files={'file': ('document.pdf', BytesIO(b'PDF content'), 'application/pdf')},
    )
    assert invalid_response.status_code == 400
    assert 'permitido' in invalid_response.json().get('detail', '').lower()

    # Tentar upload sem arquivo
    empty_response = client.post(
        '/api/account/upload-avatar',
        headers=auth_headers,
    )
    assert empty_response.status_code == 422  # Unprocessable Entity
