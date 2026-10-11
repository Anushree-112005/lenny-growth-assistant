from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ModelResponse:
    content: str
    provider: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None


class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name identifier of the provider (e.g. 'ollama', 'anthropic', 'openai', 'pi-agent')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model name."""
        pass

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> ModelResponse:
        """Generates completion for chat messages."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Checks if the provider is reachable and ready."""
        pass
