from app.services.ai_service import AIService, AIServiceError


def test_marketing_copy_falls_back_when_rate_limited(client, auth_headers, monkeypatch):
    def _raise_rate_limit(self, **kwargs):
        raise AIServiceError('OpenAI rate limit reached', user_message='rate', status_code=429, code='rate_limit')

    monkeypatch.setattr(AIService, 'generate_text', _raise_rate_limit)

    response = client.post('/api/marketing/generate-copy', headers=auth_headers, json={'prompt': 'Lançamento premium'})

    assert response.status_code == 200
    body = response.json()
    assert body['copy']
    assert 'Lançamento premium' in body['copy']


def test_marketing_campaign_falls_back_when_rate_limited(client, auth_headers, monkeypatch):
    def _raise_rate_limit(self, **kwargs):
        raise AIServiceError('OpenAI rate limit reached', user_message='rate', status_code=429, code='rate_limit')

    monkeypatch.setattr(AIService, 'generate_structured_output', _raise_rate_limit)

    response = client.post(
        '/api/marketing/campaign',
        headers=auth_headers,
        json={
            'company_name': 'Alici',
            'audience': 'Hoteis',
            'objective': 'Gerar reservas',
            'offer': 'Automação comercial',
            'tone': 'premium',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['campaign']
    assert body['cta']


def test_studio_caption_generate_falls_back_when_rate_limited(client, auth_headers, monkeypatch):
    def _raise_rate_limit(self, **kwargs):
        raise AIServiceError('OpenAI rate limit reached', user_message='rate', status_code=429, code='rate_limit')

    monkeypatch.setattr(AIService, 'generate_structured_output', _raise_rate_limit)

    response = client.post(
        '/api/studio/caption/generate',
        headers=auth_headers,
        json={
            'campaign_context': 'Campanha de reativação',
            'channel': 'instagram',
            'tone': 'direto',
            'include_cta': True,
            'include_hashtags': True,
            'variations': 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body['result']['captions']) == 3
