from fastapi import APIRouter, HTTPException, status
router = APIRouter()

from ....models import (
    AgentRequest,
    AgentResponse,
    FreeScoutWebhookRequest,
    FreeScoutWebhookResponse,
    RetrievedIncident,
)
from starlette.concurrency import run_in_threadpool
from backend.src.graph.langgraph_service import process_query_langgraph

@router.post(
    "/agent",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a user query",
)


@router.post(
    "/agent/query",
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