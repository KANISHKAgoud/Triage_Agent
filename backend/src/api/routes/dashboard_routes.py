

from fastapi import APIRouter, HTTPException, status
from backend.src.storage.ticket_storage import get_tickets
from backend.src.storage.servicenow_storage import get_incidents
from backend.src.services.vector_service import get_vector_stats
from backend.src.services.storage_service import get_triage_history
from backend.src.storage.postgres_storage import get_triage_history_pg


router = APIRouter()

@router.get(
    "/",
    summary="API health welcome",
)
async def read_root() -> dict[str, str]:
    """Return a simple status message for the API root."""

    return {
        "message": "Welcome to Triage Agent API",
        "status": "running",
    }


@router.get("/dashboard")
async def dashboard():

    tickets = get_tickets()

    incidents = get_incidents()

    vector_stats = get_vector_stats()

    total_tickets = len(tickets)

    triaged_tickets = len(
        [
            ticket
            for ticket in tickets
            if ticket[3] == "TRIAGED"
        ]
    )

    servicenow_incidents = len(incidents)

    vector_documents = vector_stats.get(
        "documents",
        0,
    )

    return {
        "total_tickets": total_tickets,
        "triaged_tickets": triaged_tickets,
        "servicenow_incidents": servicenow_incidents,
        "vector_documents": vector_documents,
        "vector_db": "healthy",
        "mailbox": "connected",
    }


@router.get("/vector-health")
async def vector_health():

    return get_vector_stats()


@router.get("/tickets")
async def tickets():

    rows = get_tickets()

    return {
        "count": len(rows),
        "tickets": rows,
    }

@router.get("/history")
async def history():

    rows = get_triage_history()

    return {
        "count": len(rows),
        "results": rows,
    }

@router.get("/postgres-history")
async def postgres_history():

    rows = get_triage_history_pg()

    return {
        "count": len(rows),
        "results": rows,
    }