"""Pydantic models used by the API endpoints."""

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Request body expected by the /agent endpoint."""

    query: str = Field(..., min_length=1, description="User query to process.")
    session_id: str = Field(..., min_length=1, description="Client session identifier.")


class AgentResponse(BaseModel):
    """Structured response returned by the /agent endpoint."""

    status: str
    query: str
    session_id: str
    response: str
