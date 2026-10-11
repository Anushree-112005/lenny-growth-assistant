import os
import re
import json
from typing import Dict, Any, Tuple


def parse_document(file_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Parses a document (.txt, .md, .json) and extracts metadata and clean text content.
    Returns:
        (metadata_dict, text_content)
    """
    ext = os.path.splitext(file_path)[1].lower()
    basename = os.path.basename(file_path)
    doc_id = os.path.splitext(basename)[0]

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw_text = f.read()

    metadata: Dict[str, Any] = {
        "id": doc_id,
        "title": doc_id.replace("-", " ").replace("_", " ").title(),
        "source_type": "podcast",
        "url": "",
        "author": "Lenny Rachitsky",
        "filename": basename,
    }

    if ext == ".json":
        try:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                metadata["id"] = data.get("id", doc_id)
                metadata["title"] = data.get("title", metadata["title"])
                metadata["source_type"] = data.get("source_type", "podcast")
                metadata["url"] = data.get("url", "")
                metadata["author"] = data.get("author", "Lenny Rachitsky")
                content = data.get("content") or data.get("transcript") or data.get("text") or ""
                return metadata, content.strip()
        except Exception:
            pass  # Fall back to raw text if json parsing fails

    # Markdown frontmatter parsing (e.g. --- title: ... ---)
    if ext in [".md", ".txt"]:
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
        if frontmatter_match:
            frontmatter_raw, body = frontmatter_match.groups()
            for line in frontmatter_raw.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    k = key.strip().lower()
                    v = val.strip().strip('"').strip("'")
                    if k in ["id", "title", "source_type", "url", "author"]:
                        metadata[k] = v
            return metadata, body.strip()

        # Check for markdown title heading (e.g. # Title)
        h1_match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
        if h1_match:
            metadata["title"] = h1_match.group(1).strip()

        # Check for URL or metadata in header lines
        url_match = re.search(r"(?:URL|Source):\s*(https?://[^\s\)]+)", raw_text, re.IGNORECASE)
        if url_match:
            metadata["url"] = url_match.group(1).strip()

        type_match = re.search(r"(?:Type|Category):\s*(podcast|newsletter|article)", raw_text, re.IGNORECASE)
        if type_match:
            metadata["source_type"] = type_match.group(1).strip().lower()

    return metadata, raw_text.strip()
