"""Pydantic models used by the API endpoints."""

from pydantic import BaseModel, Field, model_validator


class AgentRequest(BaseModel):
    """Request body expected by the /agent endpoint."""

    query: str | None = Field(
        default=None,
        min_length=1,
        description="Backward-compatible user query to process.",
    )
    ticket_subject: str | None = Field(
        default=None,
        min_length=1,
        description="Ticket subject to include in the search query.",
    )
    ticket_description: str | None = Field(
        default=None,
        min_length=1,
        description="Ticket description to include in the search query.",
    )
    session_id: str = Field(..., min_length=1, description="Client session identifier.")

    @model_validator(mode="after")
    def require_query_or_ticket_fields(self) -> "AgentRequest":
        """Require either the legacy query or at least one ticket field."""

        if not self.search_query:
            raise ValueError(
                "Provide query or at least one of ticket_subject/ticket_description."
            )

        return self

    @property
    def search_query(self) -> str:
        """Build the query text used for retrieval."""

        ticket_parts = [
            value.strip()
            for value in (self.ticket_subject, self.ticket_description)
            if value and value.strip()
        ]

        if ticket_parts:
            return "\n\n".join(ticket_parts)

        return self.query.strip() if self.query else ""


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


class FreeScoutWebhookRequest(BaseModel):
    """Request body expected from the FreeScout webhook."""

    ticket_id: str = Field(..., min_length=1, description="FreeScout ticket ID.")
    subject: str = Field(..., min_length=1, description="FreeScout ticket subject.")
    description: str = Field(
        ..., min_length=1, description="FreeScout ticket description."
    )

    @property
    def search_query(self) -> str:
        """Build the query text used for retrieval."""

        return "\n\n".join([self.subject.strip(), self.description.strip()])


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


class FreeScoutWebhookResponse(BaseModel):
    """Structured response returned by the FreeScout webhook endpoint."""

    ticket_id: str
    predicted_category: str
    predicted_subcategory: str
    recommended_resolution: str
    retrieved_incidents: list[RetrievedIncident]
