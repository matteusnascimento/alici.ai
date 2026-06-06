from app.services.ai_service import AIService


def test_studio_overview_empty_state(client, auth_headers):
    response = client.get('/api/studio/overview', headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body['recent_projects'] == []
    assert body['recent_exports'] == []
    assert body['brand_summary']['assets_count'] == 0
    assert len(body['suggested_actions']) >= 1
    routes = {item['route'] for item in body['suggested_actions']}
    assert '/app/studio/tools/ad' in routes
    assert '/app/studio/tools/caption' in routes


def test_studio_recent_projects_and_exports(client, auth_headers):
    project_response = client.post(
        '/api/studio/projects',
        headers=auth_headers,
        json={
            'project_type': 'poster',
            'title': 'Projeto Primavera',
            'metadata': {},
            'canvas_data': {},
            'layers': [],
            'timeline_data': {},
            'export_settings': {},
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()['id']

    export_response = client.post(
        f'/api/studio/projects/{project_id}/export',
        headers=auth_headers,
        json={'export_type': 'png', 'options': {'quality': 'high'}},
    )
    assert export_response.status_code == 501
    assert 'real' in export_response.json()['detail']

    recent_projects = client.get('/api/studio/projects/recent?limit=5', headers=auth_headers)
    assert recent_projects.status_code == 200
    assert recent_projects.json()[0]['title'] == 'Projeto Primavera'

    recent_exports = client.get('/api/studio/exports/recent?limit=5', headers=auth_headers)
    assert recent_exports.status_code == 200
    assert recent_exports.json() == []


def test_studio_caption_generate_uses_backend_ai(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        AIService,
        'generate_structured_output',
        lambda self, **kwargs: {'result': ['Legenda 1', 'Legenda 2', 'Legenda 3']},
    )

    response = client.post(
        '/api/studio/caption/generate',
        headers=auth_headers,
        json={
            'campaign_context': 'Campanha para lead magnet',
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
    assert 'OPENAI_API_KEY' not in response.text


def test_studio_background_remove_endpoint(client, auth_headers):
    response = client.post(
        '/api/studio/background-remove',
        headers=auth_headers,
        json={
            'asset_url': 'https://images.example.com/product.png',
            'options': {'softness': 0.5},
        },
    )

    assert response.status_code == 503
    assert 'Provider Remove.bg não configurado' in response.json()['detail']


def test_studio_ad_create_endpoint(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        AIService,
        'generate_structured_output',
        lambda self, **kwargs: {'variations': [{'id': 'A', 'headline': 'Oferta A', 'cta': 'Compre', 'style': 'premium'}]},
    )

    response = client.post(
        '/api/studio/ad/create',
        headers=auth_headers,
        json={
            'product': 'Curso de IA',
            'offer': '50% OFF',
            'audience': 'Empreendedores',
            'channel': 'Meta Ads',
            'prompt': 'Gerar anuncio para curso de IA',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['project']['project_type'] == 'ad'
    assert body['generation'] is not None
