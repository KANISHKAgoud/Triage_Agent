from typing import Any, TypedDict
from langgraph.graph import END, StateGraph
from backend.src.graph.state import AgentState
from backend.src.nodes.save_node import save_node

from backend.src.services.llm_service import LLMServiceError, generate_triage_response
from backend.src.nodes.retrieve_node import retrieve_node
from backend.src.nodes.confidence_node import confidence_node

from backend.src.nodes.keyword_boost_node import keyword_boost_node
from backend.src.utils.keyword_boost import has_hardware_keyword
from backend.src.nodes.response_node import response_node

from backend.src.nodes.llm_node import llm_node
from backend.src.nodes.classify_node import classify_node
from backend.src.nodes.resolution_node import resolution_node

from backend.ticket_status import (
    PROCESSING,
    TRIAGED,
)


UNKNOWN_CATEGORY_THRESHOLD = 0.30


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


    # incidents = _apply_hardware_keyword_boost(
    #     state["query"],
    #     incidents,
    # )


builder = StateGraph(AgentState)

builder.add_node(
    "retrieve",
    retrieve_node,
)

builder.add_node(
    "keyword_boost",
    keyword_boost_node,
)

builder.add_node(
    "llm",
    llm_node,
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
    "confidence",
    confidence_node,
)

builder.add_node(
    "response",
    response_node,
)

builder.add_node(
    "save",
    save_node,
)

builder.set_entry_point("retrieve")

builder.add_edge(
    "retrieve",
    "keyword_boost",
)

builder.add_edge(
    "keyword_boost",
    "confidence",
)

builder.add_edge(
    "confidence",
    "llm",
)

builder.add_edge(
    "llm",
    "classify",
)

builder.add_edge(
    "classify",
    "resolution",
)

builder.add_edge(
    "resolution",
    "save",
)

builder.add_edge(
    "save",
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
            has_hardware_keyword(result["query"])
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
