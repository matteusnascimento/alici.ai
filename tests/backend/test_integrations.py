def test_integrations_endpoints(client, auth_headers):
    list_response = client.get('/api/integrations', headers=auth_headers)
    assert list_response.status_code == 200
    providers = {item['provider'] for item in list_response.json()}
    assert {'openai', 'whatsapp', 'instagram'}.issubset(providers)

    openai_test_response = client.post('/api/integrations/openai/test', headers=auth_headers, json={})
    assert openai_test_response.status_code == 200
    assert openai_test_response.json()['provider'] == 'openai'

    whatsapp_response = client.post('/api/integrations/whatsapp/test', headers=auth_headers, json={})
    assert whatsapp_response.status_code == 200
    assert whatsapp_response.json()['status'] == 'placeholder'

    instagram_response = client.post('/api/integrations/instagram/test', headers=auth_headers, json={})
    assert instagram_response.status_code == 200
    assert instagram_response.json()['status'] == 'placeholder'
