import re
import math
from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import logger
from app.db.models import TranscriptChunk, SourceDocument

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", 
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", 
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", 
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", 
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours"
}


@dataclass
class RetrievalResult:
    chunk_id: str
    document_id: str
    title: str
    url: Optional[str]
    source_type: str
    excerpt: str
    score: float
    chunk_index: int


def tokenize(text_input: str) -> List[str]:
    words = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text_input.lower())
    return [w for w in words if w not in STOPWORDS]


def compute_lexical_score(query_tokens: List[str], chunk_text: str) -> float:
    """Computes a normalized term match score between query and chunk using exact word matches."""
    if not query_tokens or not chunk_text:
        return 0.0

    chunk_lower = chunk_text.lower()
    matches = 0
    total_term_freq = 0

    for token in query_tokens:
        token_pattern = r"\b" + re.escape(token) + r"\b"
        found = re.findall(token_pattern, chunk_lower)
        count = len(found)
        if count > 0:
            matches += 1
            total_term_freq += count

    if matches == 0:
        return 0.0

    # Ratio of unique query terms matched (weight 0.75) + frequency density (weight 0.25)
    term_coverage = matches / len(query_tokens)
    density = min(total_term_freq / (len(chunk_text.split()) + 1) * 20.0, 1.0)
    score = (term_coverage * 0.75) + (density * 0.25)
    return round(score, 4)


def search_transcripts(
    db: Session,
    query: str,
    limit: Optional[int] = None,
    threshold: Optional[float] = None
) -> List[RetrievalResult]:
    """
    Searches transcript chunks using PostgreSQL full-text search with fallback
    and lexical relevance scoring. Enforces relevance threshold.
    """
    limit = limit or settings.MAX_RETRIEVED_CHUNKS
    threshold = threshold if threshold is not None else settings.RELEVANCE_THRESHOLD
    query_tokens = tokenize(query)

    if not query.strip() or not query_tokens:
        logger.info("Search query contains no significant keywords.")
        return []

    results: List[RetrievalResult] = []

    # Attempt PostgreSQL Full-Text Search
    if "postgresql" in settings.DATABASE_URL:
        try:
            sql = text(
                """
                SELECT 
                    c.id, c.document_id, c.chunk_index, c.content,
                    d.title, d.source_type, d.url,
                    ts_rank_cd(to_tsvector('english', c.content), plainto_tsquery('english', :query)) AS rank
                FROM transcript_chunks c
                JOIN source_documents d ON c.document_id = d.id
                WHERE to_tsvector('english', c.content) @@ plainto_tsquery('english', :query)
                ORDER BY rank DESC
                LIMIT :limit
                """
            )
            rows = db.execute(sql, {"query": query, "limit": limit * 2}).fetchall()
            for row in rows:
                chunk_id, doc_id, chunk_index, content, title, source_type, url, rank = row
                # Normalize Postgres ts_rank (typically 0.01 - 0.5) with lexical token coverage
                lex_score = compute_lexical_score(query_tokens, content)
                combined_score = round(min(rank * 3.0 + lex_score * 0.7, 1.0), 4)

                if combined_score >= threshold:
                    results.append(
                        RetrievalResult(
                            chunk_id=str(chunk_id),
                            document_id=str(doc_id),
                            title=str(title),
                            url=str(url) if url else None,
                            source_type=str(source_type),
                            excerpt=content.strip(),
                            score=combined_score,
                            chunk_index=int(chunk_index),
                        )
                    )
        except Exception as e:
            logger.warning(f"PostgreSQL FTS search query error, using lexical fallback: {e}")

    # Fallback / supplement: lexical matching across all chunks if FTS returned too few results
    if len(results) < limit:
        all_chunks = (
            db.query(TranscriptChunk, SourceDocument)
            .join(SourceDocument, TranscriptChunk.document_id == SourceDocument.id)
            .all()
        )
        existing_chunk_ids = {r.chunk_id for r in results}

        lexical_matches: List[RetrievalResult] = []
        for chunk, doc in all_chunks:
            if chunk.id in existing_chunk_ids:
                continue
            lex_score = compute_lexical_score(query_tokens, chunk.content)
            if lex_score >= threshold:
                lexical_matches.append(
                    RetrievalResult(
                        chunk_id=chunk.id,
                        document_id=doc.id,
                        title=doc.title,
                        url=doc.url,
                        source_type=doc.source_type,
                        excerpt=chunk.content.strip(),
                        score=lex_score,
                        chunk_index=chunk.chunk_index,
                    )
                )

        lexical_matches.sort(key=lambda x: x.score, reverse=True)
        results.extend(lexical_matches)

    # Sort all by score descending and truncate to limit
    results.sort(key=lambda x: x.score, reverse=True)
    final_results = results[:limit]

    logger.info(
        f"Search query: '{query}' returned {len(final_results)} chunks (top score: {final_results[0].score if final_results else 0.0}, threshold: {threshold})"
    )
    return final_results
