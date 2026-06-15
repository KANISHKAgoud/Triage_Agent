"""Pydantic models used by the API endpoints."""

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Request body expected by the /agent endpoint."""

    query: str = Field(..., min_length=1, description="User query to process.")
    session_id: str = Field(..., min_length=1, description="Client session identifier.")


class RetrievedIncident(BaseModel):
    """A historical incident retrieved for the triage response."""

    ticket_id: str
    issue_name: str
    category: str
    subcategory: str
    priority: str
    department: str
    status: str
    score: float
    symptoms: str
    root_cause: str
    resolution: str


class AgentResponse(BaseModel):
    """Structured response returned by the /agent endpoint."""

    status: str
    query: str
    session_id: str
    predicted_category: str
    predicted_subcategory: str
    confidence_score: float
    recommended_resolution: str
    retrieved_incidents: list[RetrievedIncident]
