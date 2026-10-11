from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:Anu1116@localhost:5432/lenny_growth"

    # Model Provider Selection ("ollama", "pi-agent", "anthropic", "openai")
    LLM_PROVIDER: str = "ollama"

    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_TIMEOUT: float = 180.0

    # Cloud Providers
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Retrieval settings
    RELEVANCE_THRESHOLD: float = 0.05
    MAX_RETRIEVED_CHUNKS: int = 5
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 150

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def sanitized_dict(self) -> dict:
        """Returns safe config metadata with secrets masked."""
        return {
            "ENVIRONMENT": self.ENVIRONMENT,
            "DATABASE_URL": self.DATABASE_URL.split("@")[-1] if "@" in self.DATABASE_URL else "configured",
            "LLM_PROVIDER": self.LLM_PROVIDER,
            "OLLAMA_BASE_URL": self.OLLAMA_BASE_URL,
            "OLLAMA_MODEL": self.OLLAMA_MODEL,
            "ANTHROPIC_CONFIGURED": bool(self.ANTHROPIC_API_KEY),
            "ANTHROPIC_MODEL": self.ANTHROPIC_MODEL,
            "OPENAI_CONFIGURED": bool(self.OPENAI_API_KEY),
            "OPENAI_MODEL": self.OPENAI_MODEL,
            "RELEVANCE_THRESHOLD": self.RELEVANCE_THRESHOLD,
            "MAX_RETRIEVED_CHUNKS": self.MAX_RETRIEVED_CHUNKS,
        }


settings = Settings()
