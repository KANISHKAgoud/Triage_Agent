"""Azure OpenAI service for generating triage recommendations."""


from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from backend.src.prompts.system_prompt import SYSTEM_PROMPT
from backend.src.prompts.category_prompt import CATEGORY_PROMPT
from backend.src.prompts.subcategory_prompt import SUBCATEGORY_PROMPT
from backend.src.prompts.resolution_prompt import RESOLUTION_PROMPT
from backend.src.prompts.output_format import OUTPUT_FORMAT


DEFAULT_AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
TRIAGE_SYSTEM_PROMPT = "\n\n".join(
    [
        SYSTEM_PROMPT,
        CATEGORY_PROMPT,
        SUBCATEGORY_PROMPT,
        RESOLUTION_PROMPT,
        OUTPUT_FORMAT,
    ]
)


class LLMServiceError(RuntimeError):
    """Raised when Azure OpenAI triage generation fails."""


@lru_cache(maxsize=1)
def _get_azure_openai_client() -> Any:
    """Create a cached Azure OpenAI client from environment configuration."""

    load_dotenv()

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint:
        raise LLMServiceError("Missing AZURE_OPENAI_ENDPOINT environment variable.")
    if not api_key:
        raise LLMServiceError("Missing AZURE_OPENAI_API_KEY environment variable.")

    try:
        from openai import AzureOpenAI
    except ImportError as exc:
        raise LLMServiceError(
            "The openai package is required for Azure OpenAI integration."
        ) from exc

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=os.getenv(
            "AZURE_OPENAI_API_VERSION", DEFAULT_AZURE_OPENAI_API_VERSION
        ),
    )


def _get_model_name() -> str:
    """Read the Azure OpenAI deployment/model name from configuration."""

    load_dotenv()
    model = os.getenv("AZURE_OPENAI_MODEL")
    if not model:
        raise LLMServiceError("Missing AZURE_OPENAI_MODEL environment variable.")
    return model


def _format_incident_for_prompt(incident: dict[str, Any]) -> str:
    """Format one retrieved incident into compact prompt context."""

    return "\n".join(
        [
            f"Ticket ID: {incident.get('ticket_id', '')}",
            f"Issue Name: {incident.get('issue_name', '')}",
            f"Category: {incident.get('category', '')}",
            f"Subcategory: {incident.get('subcategory', '')}",
            f"Priority: {incident.get('priority', '')}",
            f"Department: {incident.get('department', '')}",
            f"Status: {incident.get('status', '')}",
            f"Score: {incident.get('score', '')}",
            f"Symptoms: {incident.get('symptoms', '')}",
            f"Root Cause: {incident.get('root_cause', '')}",
            f"Resolution: {incident.get('resolution', '')}",
        ]
    )


def _build_prompt(
    query: str,
    retrieved_incidents: list[dict[str, Any]],
) -> str:
    incidents_context = "\n\n---\n\n".join(
        _format_incident_for_prompt(incident)
        for incident in retrieved_incidents
    )

    return f"""
Current User Issue:

{query}

Retrieved Historical Incidents:

{incidents_context}
""".strip()


def _parse_triage_response(raw_response: str) -> dict[str, str]:
    """Parse and validate the model's JSON triage response."""

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise LLMServiceError("Azure OpenAI returned invalid JSON.") from exc

    required_fields = {"category", "subcategory", "recommended_resolution"}
    missing_fields = required_fields.difference(parsed)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise LLMServiceError(f"Azure OpenAI response is missing: {missing}")

    return {
        "category": str(parsed["category"]),
        "subcategory": str(parsed["subcategory"]),
        "recommended_resolution": str(parsed["recommended_resolution"]),
    }


def generate_triage_response(
    query: str,
    retrieved_incidents: list[dict[str, Any]],
) -> dict[str, str]:
    """Generate category, subcategory, and resolution using Azure OpenAI."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string.")
    if not isinstance(retrieved_incidents, list) or not retrieved_incidents:
        raise ValueError("retrieved_incidents must be a non-empty list.")

    client = _get_azure_openai_client()
    model = _get_model_name()
    prompt = _build_prompt(query.strip(), retrieved_incidents)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        print("========== AZURE ERROR ==========")
        print(type(exc))
        print(exc)
        print("=================================")
        raise

    message = completion.choices[0].message.content
    if not message:
        raise LLMServiceError("Azure OpenAI returned an empty response.")

    return _parse_triage_response(message)
