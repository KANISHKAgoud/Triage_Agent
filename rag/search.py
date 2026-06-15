"""Semantic search over the historical incident ChromaDB collection."""

from __future__ import annotations

from typing import Any

from .ingest import COLLECTION_NAME, get_collection


def search_incidents(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Return the top matching incidents for a user query.

    The function assumes `rag/ingest.py` has already been run at least once so
    the persistent ChromaDB collection exists on disk.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query must be a non-empty string.")

    if top_k < 1:
        raise ValueError("top_k must be greater than zero.")

    collection = get_collection()

    if collection.count() == 0:
        raise RuntimeError(
            f"ChromaDB collection '{COLLECTION_NAME}' is empty. "
            "Run `python -m rag.ingest` before searching."
        )

    try:
        results = collection.query(
            query_texts=[query.strip()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        raise RuntimeError("Failed to search incidents in ChromaDB.") from exc

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matches: list[dict[str, Any]] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        matches.append(
            {
                "ticket_id": metadata.get("ticket_id"),
                "issue_name": metadata.get("issue_name"),
                "category": metadata.get("category"),
                "subcategory": metadata.get("subcategory"),
                "priority": metadata.get("priority"),
                "department": metadata.get("department"),
                "status": metadata.get("status"),
                "score": 1 / (1 + distance),
                "matched_text": document,
            }
        )

    return matches
