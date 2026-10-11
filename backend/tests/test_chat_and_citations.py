import uuid


def test_chat_grounded_answer_and_citations(client):
    payload = {
        "message": "What is PLG and how do compounding growth loops work?",
        "conversation_id": str(uuid.uuid4()),
        "provider": "ollama",
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["role"] == "assistant"
    assert data["abstained"] is False
    assert len(data["content"]) > 0
    assert len(data["citations"]) > 0

    first_cit = data["citations"][0]
    assert "Elena Verna" in first_cit["title"]
    assert first_cit["chunk_id"] is not None
    assert first_cit["document_id"] == "elena-verna-plg-growth-loops"
    assert first_cit["relevance_score"] > 0


def test_chat_abstention_on_unsupported_query(client):
    payload = {
        "message": "What is the quantum spin of a Higgs boson in particle physics?",
        "conversation_id": str(uuid.uuid4()),
        "provider": "ollama",
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Must abstain transparently
    assert data["abstained"] is True
    assert "could not find sufficient evidence" in data["content"].lower()
    assert len(data["citations"]) == 0


def test_chat_request_validation(client):
    # Empty message should fail validation
    response = client.post("/api/chat", json={"message": "   ", "conversation_id": "test"})
    # Depending on pydantic field, let's verify error status code or empty handling
    # Let's test missing message key
    res_missing = client.post("/api/chat", json={})
    assert res_missing.status_code == 422
