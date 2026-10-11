import os
import sys
import argparse
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.session import SessionLocal, init_db
from app.db.models import SourceDocument, TranscriptChunk
from app.retrieval.parser import parse_document
from app.retrieval.chunker import chunk_text


def ingest_file(db: Session, file_path: str) -> Dict[str, Any]:
    """Ingests a single transcript file into the database."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    metadata, raw_text = parse_document(file_path)
    doc_id = metadata["id"]

    # Delete existing doc if re-ingesting
    existing_doc = db.query(SourceDocument).filter(SourceDocument.id == doc_id).first()
    if existing_doc:
        db.delete(existing_doc)
        db.commit()

    # Create SourceDocument
    source_doc = SourceDocument(
        id=doc_id,
        title=metadata.get("title", doc_id),
        source_type=metadata.get("source_type", "podcast"),
        url=metadata.get("url"),
        author=metadata.get("author", "Lenny Rachitsky"),
        summary=raw_text[:300] + "..." if len(raw_text) > 300 else raw_text,
        doc_metadata=metadata,
    )
    db.add(source_doc)
    db.flush()

    # Create chunks
    chunks_data = chunk_text(
        text=raw_text,
        doc_id=doc_id,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
    )

    created_chunks = []
    for cd in chunks_data:
        chunk = TranscriptChunk(
            document_id=doc_id,
            chunk_index=cd["chunk_index"],
            content=cd["content"],
            chunk_metadata=cd["metadata"],
        )
        db.add(chunk)
        created_chunks.append(chunk)

    db.commit()
    logger.info(f"Ingested '{metadata['title']}' ({doc_id}) with {len(created_chunks)} chunks.")

    return {
        "document_id": doc_id,
        "title": metadata["title"],
        "source_type": metadata.get("source_type"),
        "chunks_count": len(created_chunks),
    }


def ingest_directory(db: Session, directory_path: str) -> List[Dict[str, Any]]:
    """Recursively ingests all supported documents (.md, .txt, .json) in a directory."""
    results = []
    if not os.path.isdir(directory_path):
        logger.warning(f"Directory does not exist: {directory_path}")
        return results

    supported_exts = {".md", ".txt", ".json"}
    for root, _, files in os.walk(directory_path):
        for f in sorted(files):
            ext = os.path.splitext(f)[1].lower()
            if ext in supported_exts:
                file_path = os.path.join(root, f)
                try:
                    res = ingest_file(db, file_path)
                    results.append(res)
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Ingest transcript files into Lenny Growth Assistant DB")
    parser.add_argument("--dir", default="transcripts", help="Directory containing transcripts")
    parser.add_argument("--file", default=None, help="Specific file to ingest")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        if args.file:
            print(f"Ingesting file: {args.file}")
            res = ingest_file(db, args.file)
            print(f"Result: {res}")
        else:
            target_dir = args.dir
            if not os.path.isabs(target_dir):
                target_dir = os.path.abspath(target_dir)
            print(f"Ingesting directory: {target_dir}")
            results = ingest_directory(db, target_dir)
            print(f"Completed ingestion of {len(results)} files:")
            for r in results:
                print(f" - {r['title']} ({r['chunks_count']} chunks)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
