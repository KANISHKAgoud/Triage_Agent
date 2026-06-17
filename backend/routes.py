"""API route definitions for the Triage Agent service."""

from backend.storage_service import get_triage_history
from backend.langgraph_service import process_query_langgraph
from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool
from backend.postgres_storage import get_triage_history_pg
from backend.outlook_graph_service import get_emails
from backend.outlook_service import fetch_new_emails
from backend.email_processor import process_email

from backend.agent_service import process_query
from backend.freescout_service import (
    add_ticket_note,
    update_ticket_fields,
)

from .models import (
    AgentRequest,
    AgentResponse,
    FreeScoutWebhookRequest,
    FreeScoutWebhookResponse,
    RetrievedIncident,
)


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


@router.post(
    "/agent",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a user query",
)
async def run_agent(payload: AgentRequest) -> AgentResponse:
    """Search historical incidents and return the closest matches."""

    search_query = payload.search_query

    try:
        result = await run_in_threadpool(
    process_query_langgraph,
    search_query,
)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    retrieved_incidents = [
        RetrievedIncident(
            ticket_id=str(incident["ticket_id"]),
            issue_name=str(incident["issue_name"]),
            category=str(incident["category"]),
            subcategory=str(incident["subcategory"]),
            priority=str(incident["priority"]),
            department=str(incident["department"]),
            status=str(incident["status"]),
            score=float(incident["score"]),
            symptoms=str(incident["symptoms"]),
            root_cause=str(incident["root_cause"]),
            resolution=str(incident["resolution"]),
        )
        for incident in result["retrieved_incidents"]
    ]

    return AgentResponse(
        status="success",
        query=search_query,
        session_id=payload.session_id,
        predicted_category=str(result["predicted_category"]),
        predicted_subcategory=str(result["predicted_subcategory"]),
        confidence_score=float(result["confidence_score"]),
        recommended_resolution=str(result["recommended_resolution"]),
        retrieved_incidents=retrieved_incidents,
    )


@router.post(
    "/freescout/webhook",
    response_model=FreeScoutWebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a FreeScout ticket webhook",
)

async def run_freescout_webhook(
    payload: FreeScoutWebhookRequest,
) -> FreeScoutWebhookResponse:
    """Search historical incidents for a FreeScout ticket webhook."""

    search_query = payload.search_query

    try:
        result = await run_in_threadpool(
        process_query_langgraph,
        search_query,
        payload.ticket_id,
)
        update_ticket_fields(
            ticket_id=payload.ticket_id,
            category=result["predicted_category"],
            subcategory=result["predicted_subcategory"],
        )
        add_ticket_note(
            ticket_id=payload.ticket_id,
            note=result["recommended_resolution"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing FreeScout webhook.",
        ) from exc

    retrieved_incidents = [
        RetrievedIncident(
            ticket_id=str(incident["ticket_id"]),
            issue_name=str(incident["issue_name"]),
            category=str(incident["category"]),
            subcategory=str(incident["subcategory"]),
            priority=str(incident["priority"]),
            department=str(incident["department"]),
            status=str(incident["status"]),
            score=float(incident["score"]),
            symptoms=str(incident["symptoms"]),
            root_cause=str(incident["root_cause"]),
            resolution=str(incident["resolution"]),
        )
        for incident in result["retrieved_incidents"]
    ]

    return FreeScoutWebhookResponse(
        ticket_id=payload.ticket_id,
        predicted_category=str(result["predicted_category"]),
        predicted_subcategory=str(result["predicted_subcategory"]),
        recommended_resolution=str(result["recommended_resolution"]),
        retrieved_incidents=retrieved_incidents,
    )

@router.get("/outlook/test")
async def outlook_test():

    emails = fetch_new_emails()

    return {
        "count": len(emails),
        "emails": emails,
    }

@router.get("/outlook/process")
async def outlook_process():

    emails = fetch_new_emails()

    results = []

    for email in emails:
        results.append(
            process_email(email)
        )

    return {
        "processed": len(results),
        "results": results,
    }

@router.get("/outlook/live")
async def outlook_live():

    emails = get_emails()

    return {
        "count": len(emails),
        "emails": emails,
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