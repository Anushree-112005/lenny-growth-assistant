import re
from typing import List, Dict, Any


def chunk_text(
    text: str,
    doc_id: str,
    chunk_size: int = 700,
    overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Splits text into semantically coherent overlapping chunks.
    Prefers splitting on paragraph boundaries and sentence ends.
    """
    if not text.strip():
        return []

    # First, split into paragraphs
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks: List[Dict[str, Any]] = []
    current_chunk = ""
    chunk_index = 0

    for para in paragraphs:
        # If adding this paragraph exceeds target size, save current chunk and start next with overlap
        if len(current_chunk) + len(para) > chunk_size and len(current_chunk) > 0:
            chunks.append({
                "document_id": doc_id,
                "chunk_index": chunk_index,
                "content": current_chunk.strip(),
                "metadata": {
                    "char_count": len(current_chunk.strip()),
                    "chunk_index": chunk_index,
                }
            })
            chunk_index += 1

            # Retain overlap from end of current chunk
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            # Find closest sentence or space boundary in overlap
            last_space = overlap_text.find(" ")
            if last_space != -1 and last_space < len(overlap_text) // 2:
                overlap_text = overlap_text[last_space + 1:]
            current_chunk = overlap_text + "\n\n" + para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    # Append remaining chunk
    if current_chunk.strip():
        chunks.append({
            "document_id": doc_id,
            "chunk_index": chunk_index,
            "content": current_chunk.strip(),
            "metadata": {
                "char_count": len(current_chunk.strip()),
                "chunk_index": chunk_index,
            }
        })

    return chunks
