from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseProvider
from app.agents.ollama_provider import OllamaProvider
from app.agents.pi_agent_provider import PiCodingAgentProvider
from app.agents.anthropic_provider import AnthropicProvider
from app.agents.openai_provider import OpenAIProvider


class ModelRouter:
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._init_providers()

    def _init_providers(self):
        # 1. Ollama (default local provider)
        try:
            self._providers["ollama"] = OllamaProvider()
        except Exception as e:
            logger.warning(f"Could not initialize OllamaProvider: {e}")

        # 2. Pi Coding Agent
        try:
            self._providers["pi-agent"] = PiCodingAgentProvider(provider_backend="ollama")
        except Exception as e:
            logger.warning(f"Could not initialize PiCodingAgentProvider: {e}")

        # 3. Anthropic Claude
        try:
            self._providers["anthropic"] = AnthropicProvider()
        except Exception as e:
            logger.warning(f"Could not initialize AnthropicProvider: {e}")

        # 4. OpenAI
        try:
            self._providers["openai"] = OpenAIProvider()
        except Exception as e:
            logger.warning(f"Could not initialize OpenAIProvider: {e}")

    def get_provider(self, provider_name: Optional[str] = None) -> BaseProvider:
        """
        Returns the requested provider, or the environment default configured provider.
        """
        name = (provider_name or settings.LLM_PROVIDER).lower()
        if name in self._providers:
            return self._providers[name]

        # If not directly matched, check if ollama is available as fallback
        if "ollama" in self._providers:
            logger.warning(f"Provider '{name}' not found. Falling back to 'ollama'.")
            return self._providers["ollama"]

        raise ValueError(f"Requested provider '{name}' is not registered or available.")

    async def get_all_provider_statuses(self) -> List[Dict[str, Any]]:
        """Returns the status and capabilities of all configured providers."""
        results = []
        active_provider_name = settings.LLM_PROVIDER.lower()

        for name, provider in self._providers.items():
            try:
                health = await provider.health_check()
            except Exception as e:
                health = {"status": "error", "error": str(e)}

            results.append({
                "id": name,
                "name": name.upper(),
                "model": provider.model_name,
                "is_default": (name == active_provider_name),
                "health": health,
            })
        return results


router = ModelRouter()
