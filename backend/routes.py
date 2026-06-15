"""API route definitions for the Triage Agent service."""

from fastapi import APIRouter, status

from .models import AgentRequest, AgentResponse


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
    """Accept a user query and return a placeholder agent response."""

    # This placeholder keeps the endpoint contract stable until real agent
    # orchestration is connected behind the API.
    return AgentResponse(
        status="success",
        query=payload.query,
        session_id=payload.session_id,
        response="placeholder response",
    )
