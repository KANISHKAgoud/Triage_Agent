from fastapi import APIRouter, HTTPException, status
router = APIRouter()

from backend.src.services.email_service import send_triage_email
from ....models import (
    AgentRequest,
    AgentResponse,
    FreeScoutWebhookRequest,
    FreeScoutWebhookResponse,
    RetrievedIncident,
)
from starlette.concurrency import run_in_threadpool
from backend.src.graph.langgraph_service import process_query_langgraph
from backend.src.services.freescout_service import (
    add_ticket_note,
    update_ticket_fields,
)

@router.get("/email/test")
async def email_test():

    send_triage_email(
        recipient="user@example.com",
        category="VPN",
        subcategory="Remote Access",
        resolution="Reset MFA registration",
    )

    return {
        "status": "email simulated"
    }

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