from typing import Any, TypedDict
from backend.storage_service import save_triage_result
from langgraph.graph import END, StateGraph

from backend.postgres_storage import save_triage_result_pg

from backend.llm_service import LLMServiceError, generate_triage_response
from rag.search import search_incidents

from backend.ticket_status import (
    PROCESSING,
    TRIAGED,
)


UNKNOWN_CATEGORY_THRESHOLD = 0.30
HARDWARE_KEYWORDS = {
    "laptop",
    "battery",
    "overheating",
    "keyboard",
    "monitor",
    "display",
    "printer",
    "scanner",
}
HARDWARE_KEYWORD_BOOST = 0.20


class AgentState(TypedDict):
    query: str
    ticket_id: str

    retrieved_incidents: list[dict[str, Any]]

    predicted_category: str
    predicted_subcategory: str

    recommended_resolution: str


def _has_hardware_keyword(query: str) -> bool:
    normalized_query = query.lower()

    return any(
        keyword in normalized_query
        for keyword in HARDWARE_KEYWORDS
    )


def _apply_hardware_keyword_boost(
    query: str,
    incidents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not _has_hardware_keyword(query):
        return incidents

    boosted_incidents = []

    for incident in incidents:
        boosted_incident = dict(incident)

        if boosted_incident.get("category") == "Hardware":
            original_score = float(boosted_incident.get("score", 0.0))
            boosted_incident["score"] = min(
                1.0,
                original_score + HARDWARE_KEYWORD_BOOST,
            )
            boosted_incident["keyword_boost"] = "Hardware"

        boosted_incidents.append(boosted_incident)

    return sorted(
        boosted_incidents,
        key=lambda incident: float(incident.get("score", 0.0)),
        reverse=True,
    )


def _get_top_category_prediction(
    incidents: list[dict[str, Any]],
) -> tuple[str, str, float]:
    if not incidents:
        return "Unknown", "Unknown", 0.0

    top_incident = max(
        incidents,
        key=lambda incident: float(incident.get("score", 0.0)),
    )

    return (
        str(top_incident.get("category") or "Unknown"),
        str(top_incident.get("subcategory") or "Unknown"),
        float(top_incident.get("score", 0.0)),
    )


def retrieve_node(state: AgentState):
    print("Running Retrieve Node")

    incidents = search_incidents(
        state["query"],
        top_k=5,
    )

    incidents = _apply_hardware_keyword_boost(
        state["query"],
        incidents,
    )

    return {
        "retrieved_incidents": incidents
    }


def classify_node(state: AgentState):
    print("Running Classify Node")

    try:
        result = generate_triage_response(
            query=state["query"],
            retrieved_incidents=state["retrieved_incidents"],
        )
    except (LLMServiceError, ValueError, KeyError):
        category, subcategory, _confidence = _get_top_category_prediction(
            state["retrieved_incidents"]
        )

        result = {
            "category": category,
            "subcategory": subcategory,
        }

    return {
        "predicted_category": result["category"],
        "predicted_subcategory": result["subcategory"],
    }


def resolution_node(state: AgentState):
    print("Running Resolution Node")

    try:
        result = generate_triage_response(
            query=state["query"],
            retrieved_incidents=state["retrieved_incidents"],
        )
    except (LLMServiceError, ValueError, KeyError):
        top_incident = state["retrieved_incidents"][0]
        result = {
            "recommended_resolution": top_incident.get(
                "resolution",
                "Manual review required.",
            )
        }

    return {
        "recommended_resolution":
            result["recommended_resolution"]
    }


def response_node(state: AgentState):

    save_triage_result(
        ticket_id=state["ticket_id"],
        query=state["query"],
        category=state["predicted_category"],
        subcategory=state["predicted_subcategory"],
        resolution=state["recommended_resolution"],
        ticket_status=TRIAGED,
    ),

    save_triage_result_pg(
        ticket_id=state["ticket_id"],
        query=state["query"],
        category=state["predicted_category"],
        subcategory=state["predicted_subcategory"],
        resolution=state["recommended_resolution"],
        ticket_status=TRIAGED,
    )

    print("Saved triage result to database")

    return state


builder = StateGraph(AgentState)

builder.add_node(
    "retrieve",
    retrieve_node,
)

builder.add_node(
    "classify",
    classify_node,
)

builder.add_node(
    "resolution",
    resolution_node,
)

builder.add_node(
    "response",
    response_node,
)

builder.set_entry_point("retrieve")

builder.add_edge(
    "retrieve",
    "classify",
)

builder.add_edge(
    "classify",
    "resolution",
)

builder.add_edge(
    "resolution",
    "response",
)

builder.add_edge(
    "response",
    END,
)

graph = builder.compile()


def process_query_langgraph(
    query: str,
    ticket_id: str = "AGENT",
    ):
    result = graph.invoke(
        {
            "query": query,
            "ticket_id": ticket_id,
        }
    )

    top_incident = result["retrieved_incidents"][0]
    (
        top_predicted_category,
        top_predicted_subcategory,
        top_category_confidence,
    ) = _get_top_category_prediction(
        result["retrieved_incidents"]
    )

    final_category = result["predicted_category"]
    final_subcategory = result["predicted_subcategory"]

    if top_category_confidence < UNKNOWN_CATEGORY_THRESHOLD:
        final_category = "Unknown"
        final_subcategory = "Unknown"
        final_resolution = "Manual review required."
    else:
        if (
            _has_hardware_keyword(result["query"])
            and top_predicted_category == "Hardware"
        ):
            final_category = top_predicted_category
            final_subcategory = top_predicted_subcategory
        if not final_category or final_category == "Unknown":
            final_category = top_predicted_category
        if not final_subcategory or final_subcategory == "Unknown":
            final_subcategory = top_predicted_subcategory
        final_resolution = result["recommended_resolution"]

    print(
        "Classification decision | "
        f"top_predicted_category={top_predicted_category} | "
        f"confidence_score={top_category_confidence:.4f} | "
        f"final_assigned_category={final_category}"
    )

    if top_category_confidence < UNKNOWN_CATEGORY_THRESHOLD:
        return {
            "predicted_category": final_category,
            "predicted_subcategory": final_subcategory,
            "confidence_score": round(
                top_category_confidence,
                4,
            ),
            "retrieved_incidents": result["retrieved_incidents"],
            "recommended_resolution": final_resolution,
        }

    return {
        "predicted_category":
            final_category,

        "predicted_subcategory":
            final_subcategory,

        "confidence_score":
            round(
                top_category_confidence,
                4,
            ),

        "retrieved_incidents":
            result["retrieved_incidents"],

        "recommended_resolution":
            final_resolution,
    }
