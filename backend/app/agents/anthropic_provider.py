from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseProvider, ModelResponse

try:
    import anthropic
    ANTHROPIC_INSTALLED = True
except ImportError:
    ANTHROPIC_INSTALLED = False


class AnthropicProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        self._client = None
        if ANTHROPIC_INSTALLED and self.api_key:
            self._client = anthropic.AsyncAnthropic(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return self.model

    async def complete(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> ModelResponse:
        if not ANTHROPIC_INSTALLED:
            raise RuntimeError("The 'anthropic' package is not installed.")
        if not self.api_key or not self._client:
            raise RuntimeError(
                "Anthropic API key is not configured. Please set ANTHROPIC_API_KEY in .env or switch to local Ollama."
            )

        payload_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ["user", "assistant"]
        ]

        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": payload_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if system:
                kwargs["system"] = system

            response = await self._client.messages.create(**kwargs)
            text_blocks = [
                b.text for b in response.content if getattr(b, "type", "") == "text"
            ]
            content = "".join(text_blocks)

            prompt_tokens = getattr(response.usage, "input_tokens", None)
            completion_tokens = getattr(response.usage, "output_tokens", None)

            return ModelResponse(
                content=content.strip(),
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                raw={"id": response.id, "stop_reason": response.stop_reason},
            )
        except anthropic.AuthenticationError as e:
            logger.error("Anthropic authentication failed. Invalid API key.")
            raise RuntimeError("Anthropic authentication error: Invalid API key provided.") from e
        except anthropic.RateLimitError as e:
            logger.error("Anthropic rate limit reached.")
            raise RuntimeError("Anthropic rate limit exceeded. Please wait a moment before trying again.") from e
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise RuntimeError(f"Anthropic error: {str(e)}") from e

    async def health_check(self) -> Dict[str, Any]:
        has_key = bool(self.api_key and self.api_key.strip())
        return {
            "status": "available" if has_key else "not_configured",
            "provider": "anthropic",
            "model": self.model,
            "installed": ANTHROPIC_INSTALLED,
            "configured": has_key,
            "message": "Ready" if has_key else "Set ANTHROPIC_API_KEY in .env to enable Claude.",
        }
