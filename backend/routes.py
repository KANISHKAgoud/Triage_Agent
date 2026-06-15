"""API route definitions for the Triage Agent service."""

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from rag.search import search_incidents

from .models import AgentRequest, AgentResponse, IncidentMatch


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
        search_results = await run_in_threadpool(search_incidents, payload.query, top_k=5)
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
            detail="Unexpected error while searching incidents.",
        ) from exc

    matches = [
        IncidentMatch(
            ticket_id=str(match["ticket_id"]),
            issue_name=str(match["issue_name"]),
            category=str(match["category"]),
            subcategory=str(match["subcategory"]),
            priority=str(match["priority"]),
            department=str(match["department"]),
            status=str(match["status"]),
            score=float(match["score"]),
        )
        for match in search_results
    ]

    return AgentResponse(
        status="success",
        query=payload.query,
        session_id=payload.session_id,
        matches=matches,
    )
