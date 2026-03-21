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
