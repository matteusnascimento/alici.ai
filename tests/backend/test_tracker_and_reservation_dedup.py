def test_reservation_dedup_merges_same_external_reservation(client, auth_headers):
    payload = {
        "reservation_id": "EXT-RES-001",
        "external_reservation_id": "EXT-RES-001",
        "reservation_number": "1001",
        "guest_name": "Ana Silva",
        "guest_document": "12345678900",
        "guest_email": "ana@example.com",
        "check_in": "2026-07-10",
        "check_out": "2026-07-12",
        "room_type": "standard",
        "guests": 2,
        "total_amount": 980,
        "channel": "whatsapp",
        "source_provider": "omnibees",
        "source": "WhatsApp",
        "city": "Salvador",
        "state": "BA",
        "country": "Brasil",
    }

    created = client.post("/api/revenue/reservations", headers=auth_headers, json=payload)
    assert created.status_code == 200

    updated_payload = {**payload, "city": "Aracaju", "source": "PMS"}
    duplicated = client.post("/api/revenue/reservations", headers=auth_headers, json=updated_payload)
    assert duplicated.status_code == 200
    assert duplicated.json()["id"] == created.json()["id"]
    assert duplicated.json()["city"] == "Aracaju"
    assert duplicated.json()["reservation_identity_hash"]

    reservations = client.get("/api/revenue/reservations", headers=auth_headers)
    assert reservations.status_code == 200
    assert len([item for item in reservations.json() if item["external_reservation_id"] == "EXT-RES-001"]) == 1


def test_tracker_events_feed_origin_demand_map(client, auth_headers):
    event = {
        "site_id": "pousada-mar-sol",
        "visitor_id": "visitor-001",
        "session_id": "sess-001",
        "event_type": "reservation",
        "city": "Salvador",
        "state": "BA",
        "country": "Brasil",
        "traffic_source": "google_ads",
        "device": "mobile",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "ferias",
        "utm_term": "pousada bahia",
        "utm_content": "banner-a",
        "page_url": "https://example.com/reservas",
        "search_query": "suite com vista",
        "reservation_value": 1500,
    }

    response = client.post("/api/tracker/events", json=event)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

    demand = client.get("/api/revenue/origin-demand", headers=auth_headers)
    assert demand.status_code == 200
    payload = demand.json()
    assert payload["status"] == "ok"
    first = payload["items"][0]
    assert first["cidade"] == "Salvador"
    assert first["reservas"] == 1
    assert first["receita"] == 1500


def test_website_chat_widget_script_uses_tracker_endpoint(client, auth_headers):
    response = client.get("/api/integrations/website-chat/widget-script", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["company_id"].startswith("axi-")
    assert "/api/tracker/script.js" in payload["script"]
    assert 'data-axi-endpoint="' in payload["script"]


def test_lead_identity_deduplicates_and_customer_360(client, auth_headers):
    lead_payload = {
        "name": "Carlos Lima",
        "email": "carlos@example.com",
        "phone": "71999990000",
        "company": "Pousada",
        "lead_source": "instagram",
        "stage": "lead",
        "value": 500,
    }
    created = client.post("/api/revenue/leads", headers=auth_headers, json=lead_payload)
    assert created.status_code == 200
    assert created.json()["lead_identity_hash"]

    updated = client.post("/api/revenue/leads", headers=auth_headers, json={**lead_payload, "value": 850})
    assert updated.status_code == 200
    assert updated.json()["id"] == created.json()["id"]
    assert updated.json()["value"] == 850

    customer_360 = client.get("/api/revenue/customer-360", headers=auth_headers)
    assert customer_360.status_code == 200
    body = customer_360.json()
    assert body["status"] == "ok"
    assert body["items"][0]["email"] == "carlos@example.com"
