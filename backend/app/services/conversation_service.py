from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models import Conversation, Message, Citation, Artifact


def list_conversations(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    conversations = (
        db.query(Conversation)
        .order_by(desc(Conversation.updated_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
            "message_count": len(c.messages),
        }
        for c in conversations
    ]


def get_conversation_details(db: Session, conversation_id: str) -> Optional[Dict[str, Any]]:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        return None

    messages_data = []
    for m in conv.messages:
        citations_data = [
            {
                "id": cit.id,
                "chunk_id": cit.chunk_id,
                "document_id": cit.document_id,
                "title": cit.title,
                "url": cit.url,
                "excerpt": cit.excerpt,
                "relevance_score": cit.relevance_score,
            }
            for cit in m.citations
        ]
        messages_data.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "provider": m.provider,
            "model": m.model,
            "abstained": m.abstained,
            "created_at": m.created_at.isoformat(),
            "citations": citations_data,
        })

    artifacts_data = [
        {
            "id": a.id,
            "title": a.title,
            "artifact_type": a.artifact_type,
            "created_at": a.created_at.isoformat(),
            "is_evidence_grounded": a.is_evidence_grounded,
        }
        for a in conv.artifacts
    ]

    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
        "messages": messages_data,
        "artifacts": artifacts_data,
    }


def create_new_conversation(db: Session, title: Optional[str] = None) -> Dict[str, Any]:
    conv = Conversation(title=title or "New Conversation")
    db.add(conv)
    db.commit()
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
    }


def delete_conversation(db: Session, conversation_id: str) -> bool:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True
