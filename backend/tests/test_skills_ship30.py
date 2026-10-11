import uuid


def test_ship_30_skill_grounded_essay(client):
    payload = {
        "topic": "Self-sustaining product-led growth loops and monetization gates",
        "conversation_id": str(uuid.uuid4()),
        "provider": "ollama",
    }
    response = client.post("/api/skills/ship-30-for-30", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["abstained"] is False
    assert data["word_count"] > 20
    assert len(data["essay"]) > 50
    assert len(data["citations"]) > 0
    assert data["artifact_id"] is not None


def test_ship_30_skill_abstention_on_unsupported_topic(client):
    payload = {
        "topic": "Quantum physics and black hole thermodynamics in outer space",
        "conversation_id": str(uuid.uuid4()),
        "provider": "ollama",
    }
    response = client.post("/api/skills/ship-30-for-30", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["abstained"] is True
    assert "insufficient evidence" in data["essay"].lower()
    assert len(data["citations"]) == 0
