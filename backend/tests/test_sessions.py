import uuid


def test_session_creation_and_listing(client):
    create_res = client.post("/api/conversations", json={"title": "Session Test 1"})
    assert create_res.status_code == 200
    conv_data = create_res.json()
    assert conv_data["id"] is not None
    assert conv_data["title"] == "Session Test 1"

    list_res = client.get("/api/conversations")
    assert list_res.status_code == 200
    conv_list = list_res.json()
    assert any(c["id"] == conv_data["id"] for c in conv_list)


def test_session_isolation(client):
    # Create two separate sessions
    session_a = str(uuid.uuid4())
    session_b = str(uuid.uuid4())

    # Send message in session A
    res_a = client.post("/api/chat", json={
        "conversation_id": session_a,
        "message": "Question in Session A about PLG",
    })
    assert res_a.status_code == 200

    # Send message in session B
    res_b = client.post("/api/chat", json={
        "conversation_id": session_b,
        "message": "Question in Session B about monetization",
    })
    assert res_b.status_code == 200

    # Fetch Session A
    get_a = client.get(f"/api/conversations/{session_a}")
    assert get_a.status_code == 200
    messages_a = get_a.json()["messages"]
    assert any("Question in Session A" in m["content"] for m in messages_a)
    assert not any("Question in Session B" in m["content"] for m in messages_a)

    # Fetch Session B
    get_b = client.get(f"/api/conversations/{session_b}")
    assert get_b.status_code == 200
    messages_b = get_b.json()["messages"]
    assert any("Question in Session B" in m["content"] for m in messages_b)
    assert not any("Question in Session A" in m["content"] for m in messages_b)


def test_session_deletion(client):
    temp_id = str(uuid.uuid4())
    client.post("/api/chat", json={"conversation_id": temp_id, "message": "Delete me test"})
    del_res = client.delete(f"/api/conversations/{temp_id}")
    assert del_res.status_code == 200

    check_res = client.get(f"/api/conversations/{temp_id}")
    assert check_res.status_code == 404
