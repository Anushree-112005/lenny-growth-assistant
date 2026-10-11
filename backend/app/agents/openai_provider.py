from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseProvider, ModelResponse

try:
    import openai
    OPENAI_INSTALLED = True
except ImportError:
    OPENAI_INSTALLED = False


class OpenAIProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self._client = None
        if OPENAI_INSTALLED and self.api_key:
            self._client = openai.AsyncOpenAI(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

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
        if not OPENAI_INSTALLED:
            raise RuntimeError("The 'openai' package is not installed.")
        if not self.api_key or not self._client:
            raise RuntimeError(
                "OpenAI API key is not configured. Please set OPENAI_API_KEY in .env or switch to local Ollama."
            )

        payload_messages = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        for msg in messages:
            payload_messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=payload_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            prompt_tokens = response.usage.prompt_tokens if response.usage else None
            completion_tokens = response.usage.completion_tokens if response.usage else None

            return ModelResponse(
                content=content.strip(),
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                raw={"id": response.id, "finish_reason": response.choices[0].finish_reason},
            )
        except openai.AuthenticationError as e:
            logger.error("OpenAI authentication failed. Invalid API key.")
            raise RuntimeError("OpenAI authentication error: Invalid API key provided.") from e
        except openai.RateLimitError as e:
            logger.error("OpenAI rate limit reached.")
            raise RuntimeError("OpenAI rate limit exceeded. Please wait a moment before trying again.") from e
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise RuntimeError(f"OpenAI error: {str(e)}") from e

    async def health_check(self) -> Dict[str, Any]:
        has_key = bool(self.api_key and self.api_key.strip())
        return {
            "status": "available" if has_key else "not_configured",
            "provider": "openai",
            "model": self.model,
            "installed": OPENAI_INSTALLED,
            "configured": has_key,
            "message": "Ready" if has_key else "Set OPENAI_API_KEY in .env to enable OpenAI.",
        }
