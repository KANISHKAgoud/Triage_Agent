"""Ingest historical incident tickets into a persistent ChromaDB collection."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "incidents_v2.json"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "banking_it_incidents"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

REQUIRED_FIELDS = {
    "ticket_id",
    "issue_name",
    "category",
    "subcategory",
    "priority",
    "department",
    "symptoms",
    "root_cause",
    "resolution",
    "status",
}


def get_embedding_function(
    *, local_files_only: bool = False
) -> embedding_functions.SentenceTransformerEmbeddingFunction:
    """Create the sentence-transformers embedding function used by ChromaDB."""

    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME,
        local_files_only=local_files_only,
    )


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a persistent ChromaDB client backed by local disk storage."""

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_collection(*, local_files_only: bool = True) -> Collection:
    """Create or load the incidents collection with the configured embedder."""

    client = get_chroma_client()
    try:
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=get_embedding_function(local_files_only=local_files_only),
            metadata={"description": "Historical internal banking IT support incidents"},
        )
    except Exception as exc:
        if local_files_only:
            raise RuntimeError(
                "Could not load the local sentence-transformers model. "
                "Run `python -m rag.ingest` once with network access to download it."
            ) from exc
        raise


def load_incidents(data_path: Path = DATA_PATH) -> list[dict[str, Any]]:
    """Load and validate incident records from the JSON dataset."""

    if not data_path.exists():
        raise FileNotFoundError(f"Incident dataset not found: {data_path}")

    try:
        incidents = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in incident dataset: {exc}") from exc

    if not isinstance(incidents, list):
        raise ValueError("Incident dataset must be a JSON array.")

    for index, incident in enumerate(incidents, start=1):
        if not isinstance(incident, dict):
            raise ValueError(f"Incident at position {index} must be a JSON object.")

        missing_fields = REQUIRED_FIELDS.difference(incident)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Incident at position {index} is missing: {missing}")

    return incidents


def incident_to_text(incident: dict[str, Any]) -> str:
    """Convert one structured incident into searchable natural-language text."""

    return "\n".join(
        [
            f"Ticket ID: {incident['ticket_id']}",
            f"Issue: {incident['issue_name']}",
            f"Category: {incident['category']}",
            f"Subcategory: {incident['subcategory']}",
            f"Priority: {incident['priority']}",
            f"Department: {incident['department']}",
            f"Status: {incident['status']}",
            f"Symptoms: {incident['symptoms']}",
            f"Root Cause: {incident['root_cause']}",
            f"Resolution: {incident['resolution']}",
        ]
    )


def build_metadata(incident: dict[str, Any]) -> dict[str, str]:
    """Prepare Chroma-compatible metadata for filtering and response display."""

    return {
        "ticket_id": str(incident["ticket_id"]),
        "issue_name": str(incident["issue_name"]),
        "category": str(incident["category"]),
        "subcategory": str(incident["subcategory"]),
        "priority": str(incident["priority"]),
        "department": str(incident["department"]),
        "status": str(incident["status"]),
    }


def ingest_incidents(data_path: Path = DATA_PATH) -> int:
    """Load incidents from JSON and store them in persistent ChromaDB."""

    incidents = load_incidents(data_path)
    client = get_chroma_client()

    # Rebuild the collection so repeated ingestion reflects the current JSON file.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        logger.info("Collection %s did not exist before ingestion.", COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(local_files_only=False),
        metadata={"description": "Historical internal banking IT support incidents"},
    )

    documents = [incident_to_text(incident) for incident in incidents]
    metadatas = [build_metadata(incident) for incident in incidents]
    ids = [str(incident["ticket_id"]) for incident in incidents]

    try:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    except Exception as exc:
        raise RuntimeError("Failed to ingest incidents into ChromaDB.") from exc

    return len(incidents)


def main() -> None:
    """Command-line entry point for local ingestion."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    count = ingest_incidents()
    logger.info("Ingested %s incidents into ChromaDB collection '%s'.", count, COLLECTION_NAME)


if __name__ == "__main__":
    main()
