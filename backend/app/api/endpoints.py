import os
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db, check_db_health
from app.db.models import SourceDocument, TranscriptChunk
from app.agents.router import router as model_router
from app.agents.orchestrator import orchestrator
from app.skills.ship30 import generate_ship30_essay, Ship30Request, Ship30Response
from app.services.artifacts import (
    create_or_generate_artifact,
    get_artifact_by_id,
    CreateArtifactRequest,
    ArtifactResponse,
)
from app.services.conversation_service import (
    list_conversations,
    get_conversation_details,
    create_new_conversation,
    delete_conversation,
)
from app.retrieval.ingest import ingest_file, ingest_directory

api_router = APIRouter()


# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    message: str = Field(..., description="User question or prompt")
    conversation_id: Optional[str] = Field(None, description="Session ID. Generated if omitted.")
    provider: Optional[str] = Field(None, description="Optional override for model provider")


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    role: str
    content: str
    provider: str
    model: str
    abstained: bool
    citations: List[Dict[str, Any]]


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None


class IngestionRequest(BaseModel):
    path: Optional[str] = Field(None, description="Path to file or directory to ingest")


# --- Endpoints ---

@api_router.get("/health")
async def health_check():
    db_health = check_db_health()
    providers_info = await model_router.get_all_provider_statuses()
    active_provider = model_router.get_provider()

    return {
        "status": "healthy" if db_health["status"] == "connected" else "degraded",
        "service": "The Lenny Growth Assistant",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": db_health,
        "active_provider": {
            "name": active_provider.provider_name,
            "model": active_provider.model_name,
        },
        "providers": providers_info,
    }


@api_router.get("/providers")
async def get_providers():
    return await model_router.get_all_provider_statuses()


@api_router.get("/conversations")
def get_conversations(db: Session = Depends(get_db)):
    return list_conversations(db)


@api_router.post("/conversations")
def create_conversation(req: CreateConversationRequest, db: Session = Depends(get_db)):
    return create_new_conversation(db, title=req.title)


@api_router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = get_conversation_details(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@api_router.delete("/conversations/{conversation_id}")
def delete_conversation_route(conversation_id: str, db: Session = Depends(get_db)):
    success = delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}


@api_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    conv_id = req.conversation_id or str(uuid.uuid4())
    try:
        result = await orchestrator.process_chat(
            db=db,
            conversation_id=conv_id,
            user_message=req.message,
            provider_name=req.provider,
        )
        return result
    except TimeoutError as te:
        logger.error(f"Chat timeout: {te}")
        raise HTTPException(status_code=504, detail=str(te))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@api_router.post("/skills/ship-30-for-30", response_model=Ship30Response)
async def ship_30_endpoint(req: Ship30Request, db: Session = Depends(get_db)):
    try:
        return await generate_ship30_essay(db, req)
    except Exception as e:
        logger.error(f"Ship 30 skill failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ship 30 skill error: {str(e)}")


@api_router.post("/artifacts", response_model=ArtifactResponse)
async def create_artifact_endpoint(req: CreateArtifactRequest, db: Session = Depends(get_db)):
    try:
        return await create_or_generate_artifact(db, req)
    except Exception as e:
        logger.error(f"Artifact creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Artifact generation error: {str(e)}")


@api_router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
def get_artifact_endpoint(artifact_id: str, db: Session = Depends(get_db)):
    art = get_artifact_by_id(db, artifact_id)
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return art


@api_router.get("/sources")
def get_sources(db: Session = Depends(get_db)):
    docs = db.query(SourceDocument).all()
    results = []
    for d in docs:
        results.append({
            "id": d.id,
            "title": d.title,
            "source_type": d.source_type,
            "url": d.url,
            "author": d.author,
            "chunks_count": len(d.chunks),
            "ingested_at": d.ingested_at.isoformat(),
        })
    return results


@api_router.post("/ingestion")
def ingest_endpoint(req: IngestionRequest, db: Session = Depends(get_db)):
    target_path = req.path or "transcripts"
    if not os.path.isabs(target_path):
        target_path = os.path.abspath(target_path)

    if not os.path.exists(target_path):
        raise HTTPException(status_code=400, detail=f"Path not found: {target_path}")

    if os.path.isdir(target_path):
        results = ingest_directory(db, target_path)
        return {"status": "success", "type": "directory", "count": len(results), "documents": results}
    else:
        result = ingest_file(db, target_path)
        return {"status": "success", "type": "file", "document": result}
