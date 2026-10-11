import tempfile
import os
from app.retrieval.parser import parse_document
from app.retrieval.chunker import chunk_text
from app.retrieval.search import search_transcripts, compute_lexical_score, tokenize


def test_parser_with_markdown_frontmatter():
    content = """---
id: test-episode-1
title: Test Episode Title
source_type: podcast
url: https://example.com/test
author: Test Author
---

# Test Heading
Here is the body content of the test transcript.
"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        meta, body = parse_document(temp_path)
        assert meta["id"] == "test-episode-1"
        assert meta["title"] == "Test Episode Title"
        assert meta["source_type"] == "podcast"
        assert "Here is the body content" in body
    finally:
        os.remove(temp_path)


def test_chunking_overlap_and_preservation():
    sample_text = (
        "Paragraph 1 contains some initial thoughts on product growth.\n\n"
        "Paragraph 2 discusses self-sustaining compounding loops in B2B SaaS.\n\n"
        "Paragraph 3 concludes with monetization vectors and feature gating."
    )
    chunks = chunk_text(sample_text, doc_id="test-doc", chunk_size=100, overlap=30)
    assert len(chunks) >= 2
    for c in chunks:
        assert c["document_id"] == "test-doc"
        assert "content" in c
        assert c["chunk_index"] >= 0


def test_retrieval_relevance_and_abstention(db_session):
    # Query with matching terms in test fixture
    results = search_transcripts(db_session, "PLG growth loop monetization", limit=3)
    assert len(results) > 0
    top = results[0]
    assert top.score > 0.05
    assert "Elena Verna" in top.title

    # Query with irrelevant terms not in the database
    irrelevant_results = search_transcripts(db_session, "Quantum mechanics black hole singularity astrophysics", limit=3)
    assert len(irrelevant_results) == 0
