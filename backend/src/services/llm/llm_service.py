import json
from typing import Any

from backend.src.prompts.system_prompt import SYSTEM_PROMPT
from backend.src.prompts.category_prompt import CATEGORY_PROMPT
from backend.src.prompts.subcategory_prompt import SUBCATEGORY_PROMPT
from backend.src.prompts.resolution_prompt import RESOLUTION_PROMPT
from backend.src.prompts.output_format import OUTPUT_FORMAT

from backend.src.services.llm.gemini_service import (
    ask_gemini,
    GeminiServiceError,
)


class LLMServiceError(RuntimeError):
    pass


TRIAGE_SYSTEM_PROMPT = "\n\n".join(
    [
        SYSTEM_PROMPT,
        CATEGORY_PROMPT,
        SUBCATEGORY_PROMPT,
        RESOLUTION_PROMPT,
        OUTPUT_FORMAT,
    ]
)


def _format_incident(incident: dict[str, Any]) -> str:

    return "\n".join(
        [
            f"Ticket ID: {incident.get('ticket_id', '')}",
            f"Issue Name: {incident.get('issue_name', '')}",
            f"Category: {incident.get('category', '')}",
            f"Subcategory: {incident.get('subcategory', '')}",
            f"Priority: {incident.get('priority', '')}",
            f"Department: {incident.get('department', '')}",
            f"Status: {incident.get('status', '')}",
            f"Similarity Score: {incident.get('score', '')}",
            f"Symptoms: {incident.get('symptoms', '')}",
            f"Root Cause: {incident.get('root_cause', '')}",
            f"Resolution: {incident.get('resolution', '')}",
        ]
    )


def _build_prompt(
    query: str,
    retrieved_incidents: list[dict],
) -> str:

    incidents = "\n\n----------------------\n\n".join(
        _format_incident(i)
        for i in retrieved_incidents
    )

    return f"""
Current User Issue

{query}


Retrieved Incidents

{incidents}
"""


def generate_triage_response(
    query: str,
    retrieved_incidents: list[dict],
) -> dict:

    if not query.strip():
        raise LLMServiceError("Empty query")

    if not retrieved_incidents:
        raise LLMServiceError("No retrieved incidents")

    prompt = _build_prompt(
        query,
        retrieved_incidents,
    )

    try:

        response = ask_gemini(
            TRIAGE_SYSTEM_PROMPT,
            prompt,
        )

    except GeminiServiceError as exc:
        raise LLMServiceError(str(exc))

    required = [
        "reasoning",
        "category",
        "subcategory",
        "priority",
        "confidence",
        "recommended_resolution",
        "requires_manual_review",
    ]

    for key in required:

        if key not in response:

            raise LLMServiceError(
                f"Gemini response missing '{key}'"
            )

    return response