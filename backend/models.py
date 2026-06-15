"""Pydantic models used by the API endpoints."""

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Request body expected by the /agent endpoint."""

    query: str = Field(..., min_length=1, description="User query to process.")
    session_id: str = Field(..., min_length=1, description="Client session identifier.")


class IncidentMatch(BaseModel):
    """A single incident match returned by semantic search."""

    ticket_id: str
    issue_name: str
    category: str
    subcategory: str
    priority: str
    department: str
    status: str
    score: float


class AgentResponse(BaseModel):
    """Structured response returned by the /agent endpoint."""

    status: str
    query: str
    session_id: str
    matches: list[IncidentMatch]
