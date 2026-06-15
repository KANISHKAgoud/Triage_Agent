"""Service layer for triaging user queries with retrieved incident context."""

from __future__ import annotations

from typing import Any

from backend.llm_service import LLMServiceError, generate_triage_response
from rag.search import search_incidents


TOP_K_INCIDENTS = 5
FALLBACK_RECOMMENDATION = "Unable to generate recommendation"


def _build_context(retrieved_incidents: list[dict[str, Any]]) -> str:
    """Create a concise text context from retrieved incidents for future LLM use."""

    context_parts = []
    for incident in retrieved_incidents:
        context_parts.append(
            "\n".join(
                [
                    f"Ticket ID: {incident.get('ticket_id', '')}",
                    f"Issue Name: {incident.get('issue_name', '')}",
                    f"Category: {incident.get('category', '')}",
                    f"Subcategory: {incident.get('subcategory', '')}",
                    f"Priority: {incident.get('priority', '')}",
                    f"Department: {incident.get('department', '')}",
                    f"Status: {incident.get('status', '')}",
                    f"Score: {incident.get('score', 0.0):.4f}",
                    f"Symptoms: {incident.get('symptoms', '')}",
                    f"Root Cause: {incident.get('root_cause', '')}",
                    f"Resolution: {incident.get('resolution', '')}",
                ]
            )
        )

    return "\n\n".join(context_parts)


def _format_retrieved_incident(incident: dict[str, Any]) -> dict[str, Any]:
    """Return only API-safe fields from a retrieved incident."""

    return {
        "ticket_id": incident.get("ticket_id"),
        "issue_name": incident.get("issue_name"),
        "category": incident.get("category"),
        "subcategory": incident.get("subcategory"),
        "priority": incident.get("priority"),
        "department": incident.get("department"),
        "status": incident.get("status"),
        "score": incident.get("score"),
        "symptoms": incident.get("symptoms"),
        "root_cause": incident.get("root_cause"),
        "resolution": incident.get("resolution"),
    }


def process_query(query: str) -> dict[str, Any]:
    """Search historical incidents and prepare a triage response.

    The top retrieved incident is used as a fallback if Azure OpenAI cannot
    generate a triage recommendation.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    retrieved_incidents = search_incidents(query.strip(), top_k=TOP_K_INCIDENTS)

    if not retrieved_incidents:
        raise RuntimeError("No matching incidents were retrieved.")

    context = _build_context(retrieved_incidents)
    if not context:
        raise RuntimeError("Unable to build incident context from search results.")

    top_incident = retrieved_incidents[0]
    confidence_score = round(float(top_incident.get("score", 0.0)), 4)

    try:
        llm_result = generate_triage_response(
            query=query,
            retrieved_incidents=retrieved_incidents,
        )
        predicted_category = llm_result["category"]
        predicted_subcategory = llm_result["subcategory"]
        recommended_resolution = llm_result["recommended_resolution"]
    except (LLMServiceError, ValueError, KeyError):
        predicted_category = top_incident.get("category")
        predicted_subcategory = top_incident.get("subcategory")
        recommended_resolution = FALLBACK_RECOMMENDATION

    return {
        "predicted_category": predicted_category,
        "predicted_subcategory": predicted_subcategory,
        "confidence_score": confidence_score,
        "retrieved_incidents": [
            _format_retrieved_incident(incident) for incident in retrieved_incidents
        ],
        "recommended_resolution": recommended_resolution,
    }
