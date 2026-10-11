import os
import sys
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.models import Base, SourceDocument, TranscriptChunk, Conversation, Message
from app.db.session import get_db
from app.main import app
from app.agents.base import BaseProvider, ModelResponse
from app.agents.router import router

# Test in-memory SQLite database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class MockLLMProvider(BaseProvider):
    def __init__(self, name: str = "mock-ollama", model: str = "qwen2.5:3b"):
        self._name = name
        self._model = model

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(self, messages, system=None, temperature=0.2, max_tokens=1500) -> ModelResponse:
        return ModelResponse(
            content=(
                "# Product-Led Growth Insights\n\n"
                "According to Elena Verna [Source: Elena Verna on B2B PLG], PLG is an end-user driven model "
                "where the product itself drives acquisition, retention, and monetization. "
                "Traditional linear funnels fail because each customer requires continuous ad spend, whereas "
                "self-sustaining growth loops compound organically as users invite colleagues."
            ),
            provider=self.provider_name,
            model=self.model_name,
            prompt_tokens=120,
            completion_tokens=65,
        )

    async def health_check(self):
        return {"status": "available", "mock": True}


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Populate sample transcript for retrieval testing
    doc = SourceDocument(
        id="elena-verna-plg-growth-loops",
        title="Elena Verna on B2B Product-Led Growth (PLG) and Growth Loops",
        source_type="podcast",
        url="https://www.lennyspodcast.com/elena-verna",
        author="Lenny Rachitsky",
        summary="Elena Verna breaks down PLG, sales-assisted motions, and compounding loops.",
    )
    session.add(doc)
    session.flush()

    chunk1 = TranscriptChunk(
        document_id=doc.id,
        chunk_index=0,
        content=(
            "Elena Verna: PLG is not just a free trial button. PLG is a go-to-market model "
            "where the product itself drives acquisition, retention, and monetization. "
            "In a growth loop, an input generates an action, which produces an output reinvested into new inputs."
        ),
        chunk_metadata={"chunk_index": 0},
    )
    chunk2 = TranscriptChunk(
        document_id=doc.id,
        chunk_index=1,
        content=(
            "The Three Pillars of PLG Monetization: Feature Gates, Usage Limits, and Seat-Based Collaboration Gates. "
            "Never gate the Aha moment. Let users experience value first before prompting a paywall."
        ),
        chunk_metadata={"chunk_index": 1},
    )
    session.add_all([chunk1, chunk2])
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    # Register mock provider in router for deterministic testing
    mock_p = MockLLMProvider()
    router._providers["ollama"] = mock_p
    router._providers["mock"] = mock_p

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
