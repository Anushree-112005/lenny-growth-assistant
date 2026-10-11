from typing import List, Dict, Any, Optional
import os

from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseProvider, ModelResponse

try:
    from pi_agent.llm import build_provider, NeutralMessage, ollama_running
    PI_AGENT_AVAILABLE = True
except ImportError:
    PI_AGENT_AVAILABLE = False


class PiCodingAgentProvider(BaseProvider):
    """
    Genuine integration of the Pi Coding Agent SDK (pi_agent).
    Wraps pi_agent's multi-provider LLM abstraction and tool execution layer.
    """
    def __init__(self, model: Optional[str] = None, provider_backend: str = "ollama"):
        if not PI_AGENT_AVAILABLE:
            raise ImportError("pi-coding-agent is not installed in the Python environment.")
        self.model = model or settings.OLLAMA_MODEL
        self.provider_backend = provider_backend
        self._provider = build_provider(
            model=self.model,
            provider=self.provider_backend,
            max_tokens=2048,
        )

    @property
    def provider_name(self) -> str:
        return "pi-agent"

    @property
    def model_name(self) -> str:
        return f"{self.provider_backend}/{self.model}"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> ModelResponse:
        system_prompt = system or "You are a helpful assistant."
        pi_messages = [
            NeutralMessage(role=m["role"], content=m["content"])
            for m in messages
        ]

        try:
            # pi_agent complete runs synchronously; wrap in completion
            resp = self._provider.complete(
                system=system_prompt,
                messages=pi_messages,
                tools=[],
            )
            input_tokens = getattr(resp.usage, "input_tokens", None) if resp.usage else None
            output_tokens = getattr(resp.usage, "output_tokens", None) if resp.usage else None

            return ModelResponse(
                content=resp.text.strip(),
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                raw={"stop_reason": getattr(resp, "stop_reason", "stop")},
            )
        except Exception as e:
            logger.error(f"Pi Coding Agent error: {e}")
            raise RuntimeError(f"Pi Coding Agent execution error: {str(e)}") from e

    async def health_check(self) -> Dict[str, Any]:
        running = ollama_running() if self.provider_backend == "ollama" else True
        return {
            "status": "available" if running else "unavailable",
            "sdk": "pi-coding-agent",
            "backend": self.provider_backend,
            "model": self.model,
            "ollama_running": running,
        }
