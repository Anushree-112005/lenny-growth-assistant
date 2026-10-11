import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    Boolean,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    artifacts = relationship("Artifact", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    provider = Column(String(50), nullable=True)  # "ollama", "anthropic", "openai", "pi-agent"
    model = Column(String(100), nullable=True)
    abstained = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    citations = relationship("Citation", back_populates="message", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="message", cascade="all, delete-orphan")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String(36), nullable=False)
    document_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=True)
    excerpt = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=True)

    message = relationship("Message", back_populates="citations")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(String(100), primary_key=True)  # slug or identifier
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), default="podcast")  # "podcast", "newsletter", "article"
    url = Column(String(500), nullable=True)
    author = Column(String(100), default="Lenny Rachitsky")
    summary = Column(Text, nullable=True)
    ingested_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    doc_metadata = Column("metadata", JSON, default=dict)

    chunks = relationship("TranscriptChunk", back_populates="document", cascade="all, delete-orphan")


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(100), ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    document = relationship("SourceDocument", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunk_doc_index", "document_id", "chunk_index"),
    )


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # "html", "markdown", "experiment", "brief"
    content = Column(Text, nullable=False)
    is_evidence_grounded = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    artifact_metadata = Column("metadata", JSON, default=dict)

    conversation = relationship("Conversation", back_populates="artifacts")
    message = relationship("Message", back_populates="artifacts")
