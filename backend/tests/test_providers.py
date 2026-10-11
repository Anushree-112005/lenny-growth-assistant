import pytest
from app.agents.router import router
from app.agents.ollama_provider import OllamaProvider


def test_provider_router_selection():
    # Router should return registered ollama provider
    p = router.get_provider("ollama")
    assert p is not None
    assert p.provider_name in ["ollama", "mock-ollama"]

    # Requesting non-existent provider falls back gracefully to default
    fallback = router.get_provider("non_existent_provider_xyz")
    assert fallback is not None


def test_ollama_unavailable_handling():
    import anyio

    async def _run():
        dead_provider = OllamaProvider(base_url="http://localhost:59999", timeout=1.0)
        health = await dead_provider.health_check()
        assert health["status"] == "unavailable"

        with pytest.raises((RuntimeError, TimeoutError)) as exc_info:
            await dead_provider.complete([{"role": "user", "content": "hello"}])
        assert ("Cannot connect to local Ollama service" in str(exc_info.value) or 
                "timed out" in str(exc_info.value))

    anyio.run(_run)
