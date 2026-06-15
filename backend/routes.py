"""API route definitions for the Triage Agent service."""

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from backend.agent_service import process_query

from .models import AgentRequest, AgentResponse, RetrievedIncident


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

    try:
        result = await run_in_threadpool(process_query, payload.query)
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
            detail="Unexpected error while processing triage request.",
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
        query=payload.query,
        session_id=payload.session_id,
        predicted_category=str(result["predicted_category"]),
        predicted_subcategory=str(result["predicted_subcategory"]),
        confidence_score=float(result["confidence_score"]),
        recommended_resolution=str(result["recommended_resolution"]),
        retrieved_incidents=retrieved_incidents,
    )
