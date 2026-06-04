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
        "page_url": "https://example.com/reservas",
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
