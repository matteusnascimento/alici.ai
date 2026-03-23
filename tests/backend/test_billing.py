def test_billing_plan_and_upgrade_flow(client, auth_headers):
    plans_response = client.get('/api/billing/plans', headers=auth_headers)
    assert plans_response.status_code == 200
    plans = plans_response.json()
    assert any(item['id'] == 'free' for item in plans)
    assert any(item['id'] == 'pro' for item in plans)

    current_response = client.get('/api/billing/current', headers=auth_headers)
    assert current_response.status_code == 200
    assert current_response.json()['plan_id'] == 'free'

    upgrade_response = client.post(
        '/api/billing/upgrade',
        headers=auth_headers,
        json={'plan_id': 'pro', 'billing_cycle': 'monthly'},
    )
    assert upgrade_response.status_code == 200
    assert upgrade_response.json()['subscription']['plan_id'] == 'pro'

    usage_response = client.get('/api/billing/usage', headers=auth_headers)
    assert usage_response.status_code == 200
    assert isinstance(usage_response.json()['items'], list)

    history_response = client.get('/api/billing/history', headers=auth_headers)
    assert history_response.status_code == 200
    assert len(history_response.json()['events']) >= 1
