def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "The Lenny Growth Assistant"
    assert "active_provider" in data
    assert "providers" in data


def test_api_providers_endpoint(client):
    response = client.get("/api/providers")
    assert response.status_code == 200
    providers = response.json()
    assert isinstance(providers, list)
    provider_ids = [p["id"] for p in providers]
    assert "ollama" in provider_ids
