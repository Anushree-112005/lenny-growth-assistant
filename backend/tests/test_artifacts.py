from app.services.artifacts import sanitize_html


def test_artifact_sanitization():
    malicious_html = """
    <div>
        <h1>Welcome</h1>
        <script>window.localStorage.setItem('secret', 'stolen');</script>
        <script>document.cookie = 'user=hacked';</script>
        <a href="javascript:alert(1)">Click here</a>
        <iframe src="https://attacker.com/steal"></iframe>
        <img src="x" onerror="alert('xss')" />
    </div>
    """
    clean_html = sanitize_html(malicious_html)

    assert "window.localStorage" not in clean_html
    assert "document.cookie" not in clean_html
    assert "javascript:" not in clean_html
    assert "<iframe" not in clean_html
    assert "onerror=" not in clean_html
    assert "<h1>Welcome</h1>" in clean_html


def test_create_and_fetch_artifact(client):
    payload = {
        "title": "PLG Pricing Page",
        "artifact_type": "html",
        "content": "<div class='pricing-table'><h2>Pro Plan</h2><p>$49/month</p></div>",
        "is_evidence_grounded": True,
    }
    create_res = client.post("/api/artifacts", json=payload)
    assert create_res.status_code == 200
    art = create_res.json()
    assert art["id"] is not None
    assert art["title"] == "PLG Pricing Page"
    assert "pricing-table" in art["content"]

    fetch_res = client.get(f"/api/artifacts/{art['id']}")
    assert fetch_res.status_code == 200
    fetched_art = fetch_res.json()
    assert fetched_art["id"] == art["id"]
    assert fetched_art["artifact_type"] == "html"
