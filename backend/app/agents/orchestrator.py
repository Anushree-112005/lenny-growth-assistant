import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.models import Conversation, Message, Citation
from app.retrieval.search import search_transcripts, RetrievalResult
from app.agents.router import router

ABSTENTION_MESSAGE = (
    "I could not find sufficient evidence in the ingested Lenny's Podcast and Newsletter transcripts "
    "to answer this question reliably. The retrieved sources do not cover this topic.\n\n"
    "**Suggested topics covered in the ingested material:**\n"
    "- Common approaches to diagnosing Product-Market Fit and reading retention curves (Casey Winters)\n"
    "- The Four Fits Framework: Market-Product, Product-Channel, Channel-Model, Model-Market (Brian Balfour)\n"
    "- B2B Product-Led Growth (PLG), Sales-assisted motions, and self-sustaining growth loops (Elena Verna)\n"
    "- SaaS pricing models, packaging, and value metric selection (Lenny Rachitsky)\n"
    "- Digital writing frameworks and Ship 30 for 30 Atomic Essays (Nicolas Cole & Dickie Bush)"
)


class GrowthOrchestrator:
    async def process_chat(
        self,
        db: Session,
        conversation_id: str,
        user_message: str,
        provider_name: Optional[str] = None,
        limit_chunks: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrates full grounded conversational flow:
        1. Conversation verification / creation
        2. Persistence of user message
        3. Search and retrieval of evidence chunks
        4. Relevance threshold check & abstention enforcement
        5. Context-grounded LLM inference
        6. Persistence of assistant message & citations
        """
        # 1. Fetch or create conversation
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            conv = Conversation(
                id=conversation_id,
                title=user_message[:50] + ("..." if len(user_message) > 50 else "")
            )
            db.add(conv)
            db.commit()

        # 2. Persist user message
        user_msg_record = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message.strip(),
        )
        db.add(user_msg_record)
        db.commit()

        # 3. Retrieve relevant chunks
        retrieved_chunks: List[RetrievalResult] = search_transcripts(
            db=db,
            query=user_message,
            limit=limit_chunks or settings.MAX_RETRIEVED_CHUNKS,
        )

        # 4. Abstention check
        if not retrieved_chunks:
            logger.info(f"Insufficient evidence for query '{user_message}'. Abstaining.")
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=ABSTENTION_MESSAGE,
                provider=provider_name or settings.LLM_PROVIDER,
                model="abstention-gate",
                abstained=True,
            )
            db.add(assistant_msg)
            db.commit()

            return {
                "conversation_id": conversation_id,
                "message_id": assistant_msg.id,
                "role": "assistant",
                "content": assistant_msg.content,
                "provider": assistant_msg.provider,
                "model": assistant_msg.model,
                "abstained": True,
                "citations": [],
            }

        # 5. Build grounded context
        context_blocks = []
        for i, c in enumerate(retrieved_chunks, 1):
            context_blocks.append(
                f"[Source {i}: \"{c.title}\" | Doc ID: {c.document_id} | Chunk {c.chunk_index} | URL: {c.url or 'N/A'}]\n"
                f"{c.excerpt}\n"
            )
        evidence_text = "\n---\n".join(context_blocks)

        system_prompt = (
            "You are The Lenny Growth Assistant, an AI expert partner grounded strictly in Lenny Rachitsky's "
            "podcast and newsletter materials.\n\n"
            "RETRIEVED SOURCE EXCERPTS:\n"
            f"{evidence_text}\n\n"
            "STRICT GROUNDING INSTRUCTIONS:\n"
            "1. Base your answer strictly on the provided transcript excerpts above.\n"
            "2. Cite your sources directly using the Source title or Doc ID (e.g., [Source: Elena Verna on B2B PLG]).\n"
            "3. Keep your response direct, structured, and focused with 2-3 key takeaways and bullet points (around 120-180 words total).\n"
            "4. Never invent podcast episode titles, guest quotes, metrics, or source URLs not in the excerpts.\n"
            "5. If the excerpts only partially address the question, be transparent about what is covered."
        )

        # Build message history for conversational context (up to last 6 messages)
        past_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(6)
            .all()
        )
        past_messages.reverse()

        llm_messages = []
        for m in past_messages:
            if m.role in ["user", "assistant"]:
                llm_messages.append({"role": m.role, "content": m.content})

        # 6. Call model provider
        provider = router.get_provider(provider_name)
        logger.info(f"Invoking provider '{provider.provider_name}' with model '{provider.model_name}'")

        try:
            model_response = await provider.complete(
                messages=llm_messages,
                system=system_prompt,
                temperature=0.2,
                max_tokens=250,
            )
        except Exception as e:
            logger.error(f"Provider call failed: {e}")
            raise

        # 7. Persist assistant response and citations
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=model_response.content,
            provider=model_response.provider,
            model=model_response.model,
            abstained=False,
        )
        db.add(assistant_msg)
        db.flush()

        saved_citations = []
        for chunk in retrieved_chunks:
            citation = Citation(
                message_id=assistant_msg.id,
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                title=chunk.title,
                url=chunk.url,
                excerpt=chunk.excerpt[:400] + ("..." if len(chunk.excerpt) > 400 else ""),
                relevance_score=chunk.score,
            )
            db.add(citation)
            saved_citations.append({
                "id": citation.id,
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "url": chunk.url,
                "excerpt": citation.excerpt,
                "relevance_score": chunk.score,
            })

        db.commit()

        return {
            "conversation_id": conversation_id,
            "message_id": assistant_msg.id,
            "role": "assistant",
            "content": assistant_msg.content,
            "provider": model_response.provider,
            "model": model_response.model,
            "abstained": False,
            "citations": saved_citations,
        }


orchestrator = GrowthOrchestrator()
