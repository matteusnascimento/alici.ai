def test_chat_send_and_messages(client, auth_headers):
    send_response = client.post('/api/chat/send', headers=auth_headers, json={'text': 'Quero ajuda com marketing'})

    assert send_response.status_code == 200
    body = send_response.json()
    conversation_id = body['conversation']['id']
    assert body['assistant_message']['text']

    list_response = client.get('/api/chat/conversations', headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    messages_response = client.get(f'/api/chat/conversations/{conversation_id}/messages', headers=auth_headers)
    assert messages_response.status_code == 200
    assert len(messages_response.json()) == 2

    send_v2_response = client.post('/api/chat', headers=auth_headers, json={'text': 'Segunda mensagem'})
    assert send_v2_response.status_code == 200

    history_response = client.get('/api/chat/history', headers=auth_headers)
    assert history_response.status_code == 200
    assert len(history_response.json()) >= 1

    upload_response = client.post(
        '/api/chat/upload',
        headers=auth_headers,
        files={'file': ('brief.txt', b'briefing de campanha', 'text/plain')},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()['filename'] == 'brief.txt'
