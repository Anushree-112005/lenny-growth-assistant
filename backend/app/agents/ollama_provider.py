from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseProvider, ModelResponse


class OllamaProvider(BaseProvider):
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    @property
    def provider_name(self) -> str:
        return "ollama"

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
        payload_messages = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        for msg in messages:
            payload_messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {
            "model": self.model,
            "messages": payload_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        url = f"{self.base_url}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                message_obj = data.get("message", {})
                content = message_obj.get("content", "")

                prompt_tokens = data.get("prompt_eval_count")
                completion_tokens = data.get("eval_count")

                return ModelResponse(
                    content=content.strip(),
                    provider=self.provider_name,
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    raw=data,
                )
        except httpx.ConnectError as e:
            logger.error(f"Ollama connection error at {self.base_url}: {e}")
            raise RuntimeError(
                f"Cannot connect to local Ollama service at {self.base_url}. Please ensure Ollama is running (`ollama serve`)."
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out after {self.timeout}s: {e}")
            raise TimeoutError(
                f"Ollama generation timed out after {self.timeout} seconds for model '{self.model}'."
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error {e.response.status_code}: {e.response.text}")
            raise RuntimeError(f"Ollama returned error {e.response.status_code}: {e.response.text}") from e
        except Exception as e:
            logger.error(f"Unexpected Ollama provider error: {e}")
            raise RuntimeError(f"Ollama error: {str(e)}") from e

    async def health_check(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    models_data = res.json().get("models", [])
                    available_model_names = [m.get("name", "") for m in models_data]
                    is_model_present = any(self.model in name for name in available_model_names)
                    return {
                        "status": "available",
                        "base_url": self.base_url,
                        "model": self.model,
                        "model_available": is_model_present,
                        "installed_models": available_model_names,
                    }
                return {
                    "status": "error",
                    "code": res.status_code,
                    "error": res.text,
                }
        except Exception as e:
            return {
                "status": "unavailable",
                "base_url": self.base_url,
                "error": str(e),
                "model": self.model,
            }
