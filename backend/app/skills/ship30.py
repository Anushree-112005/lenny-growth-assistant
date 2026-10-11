import os
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.models import Conversation, Message, Citation, Artifact
from app.retrieval.search import search_transcripts, RetrievalResult
from app.agents.router import router

PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), "ship30_prompt.md")


class Ship30Request(BaseModel):
    topic: str = Field(..., description="The growth topic or question to write the Ship 30 essay about")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to link the essay to")
    provider: Optional[str] = Field(None, description="Optional provider override")


class Ship30Response(BaseModel):
    title: str
    essay: str
    word_count: int
    abstained: bool
    citations: List[Dict[str, Any]]
    artifact_id: Optional[str] = None
    provider: str
    model: str


def load_ship30_prompt_template() -> str:
    if os.path.exists(PROMPT_FILE_PATH):
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "You are an expert digital writer trained in the Ship 30 for 30 methodology."


async def generate_ship30_essay(
    db: Session,
    request: Ship30Request,
) -> Ship30Response:
    """
    Executes the Ship 30 for 30 skill:
    1. Searches transcripts for topic evidence.
    2. Enforces abstention if evidence is insufficient.
    3. Prompts the selected provider using the Ship 30 prompt architecture.
    4. Computes word count and persists the resulting essay and artifact.
    """
    topic = request.topic.strip()
    provider_name = request.provider or settings.LLM_PROVIDER
    conversation_id = request.conversation_id

    # 1. Retrieve chunks (get up to 6 chunks for comprehensive essay evidence)
    chunks: List[RetrievalResult] = search_transcripts(db=db, query=topic, limit=6)

    # 2. Check for sufficient evidence
    if not chunks:
        logger.info(f"Ship 30 skill: Insufficient evidence for topic '{topic}'. Abstaining.")
        abstention_text = (
            f"# Insufficient Evidence: '{topic}'\n\n"
            "The Ship 30 for 30 skill strictly requires verified transcript evidence to build an "
            "authoritative, citation-grounded essay. The ingested archive does not currently contain "
            "sufficient source material covering this specific subject.\n\n"
            "To generate a grounded Ship 30 essay, please choose a topic covered by the ingested sources:\n"
            "- Self-sustaining growth loops vs. linear funnels (Elena Verna)\n"
            "- The Four Fits Framework for scaling past PMF (Brian Balfour)\n"
            "- Cohort retention curves and diagnosing Product-Market Fit (Casey Winters)\n"
            "- Value metric selection and SaaS pricing strategy (Lenny Rachitsky)\n"
            "- Atomic essays and digital writing architecture (Nicolas Cole & Dickie Bush)"
        )
        return Ship30Response(
            title=f"Abstention: {topic}",
            essay=abstention_text,
            word_count=len(abstention_text.split()),
            abstained=True,
            citations=[],
            artifact_id=None,
            provider=provider_name,
            model="abstention-gate",
        )

    # 3. Format source evidence
    evidence_blocks = []
    for i, c in enumerate(chunks, 1):
        evidence_blocks.append(
            f"[Source {i}: \"{c.title}\" | Doc ID: {c.document_id} | Chunk {c.chunk_index} | URL: {c.url or 'N/A'}]\n"
            f"{c.excerpt}\n"
        )
    evidence_text = "\n---\n".join(evidence_blocks)

    system_instructions = load_ship30_prompt_template()

    user_prompt = (
        f"TOPIC: {topic}\n\n"
        f"RETRIEVED TRANSCRIPT EVIDENCE:\n"
        f"{evidence_text}\n\n"
        "Now, write the complete, approximately 1,250-word Ship 30 for 30 essay following all required "
        "sections: Opening Hook (1-3-1), Central Thesis, Evidence-Grounded Core Narrative with descriptive headings, "
        "Distinction between source evidence and original synthesis, Actionable Implementation Plan, "
        "and Citation References. Ground every claim directly in the evidence above."
    )

    provider = router.get_provider(provider_name)
    logger.info(f"Ship 30 skill invoking {provider.provider_name} ({provider.model_name})")

    model_resp = await provider.complete(
        messages=[{"role": "user", "content": user_prompt}],
        system=system_instructions,
        temperature=0.3,
        max_tokens=2500,
    )

    essay_content = model_resp.content.strip()
    words = len(re.findall(r"\b\w+\b", essay_content))

    # Derive essay title from markdown H1 or fallback
    title_match = re.search(r"^#\s+(.+)$", essay_content, re.MULTILINE)
    essay_title = title_match.group(1).strip() if title_match else f"Ship 30 Essay: {topic}"

    # 4. Save to conversation and create an Artifact
    saved_citations = [
        {
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "title": c.title,
            "url": c.url,
            "excerpt": c.excerpt[:300] + "...",
            "relevance_score": c.score,
        }
        for c in chunks
    ]

    # If conversation_id is provided, save message & artifact
    artifact_id = None
    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            conv = Conversation(id=conversation_id, title=f"Ship 30: {topic}")
            db.add(conv)
            db.commit()

        msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=essay_content,
            provider=model_resp.provider,
            model=model_resp.model,
            abstained=False,
        )
        db.add(msg)
        db.flush()

        for sc in saved_citations:
            cit = Citation(
                message_id=msg.id,
                chunk_id=sc["chunk_id"],
                document_id=sc["document_id"],
                title=sc["title"],
                url=sc["url"],
                excerpt=sc["excerpt"],
                relevance_score=sc["relevance_score"],
            )
            db.add(cit)

        # Create Artifact for easy viewing
        artifact = Artifact(
            conversation_id=conversation_id,
            message_id=msg.id,
            title=essay_title,
            artifact_type="markdown",
            content=essay_content,
            is_evidence_grounded=True,
            artifact_metadata={
                "topic": topic,
                "word_count": words,
                "skill": "ship-30-for-30",
            },
        )
        db.add(artifact)
        db.commit()
        artifact_id = artifact.id

    return Ship30Response(
        title=essay_title,
        essay=essay_content,
        word_count=words,
        abstained=False,
        citations=saved_citations,
        artifact_id=artifact_id,
        provider=model_resp.provider,
        model=model_resp.model,
    )
