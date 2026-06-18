from typing import Any, TypedDict
from backend.storage_service import save_triage_result
from langgraph.graph import END, StateGraph

from backend.postgres_storage import save_triage_result_pg

from backend.llm_service import generate_triage_response
from rag.search import search_incidents

from backend.ticket_status import (
    PROCESSING,
    TRIAGED,
)


class AgentState(TypedDict):
    query: str
    ticket_id: str

    retrieved_incidents: list[dict[str, Any]]

    predicted_category: str
    predicted_subcategory: str

    recommended_resolution: str


def retrieve_node(state: AgentState):
    print("Running Retrieve Node")

    incidents = search_incidents(
        state["query"],
        top_k=5,
    )

    return {
        "retrieved_incidents": incidents
    }


def classify_node(state: AgentState):
    print("Running Classify Node")

    result = generate_triage_response(
        query=state["query"],
        retrieved_incidents=state["retrieved_incidents"],
    )

    return {
        "predicted_category": result["category"],
        "predicted_subcategory": result["subcategory"],
    }


def resolution_node(state: AgentState):
    print("Running Resolution Node")

    result = generate_triage_response(
        query=state["query"],
        retrieved_incidents=state["retrieved_incidents"],
    )

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

    if float(top_incident.get("score", 0.0)) < 0.60:
        return {
            "predicted_category": "Unknown",
            "predicted_subcategory": "Unknown",
            "confidence_score": round(
                float(top_incident.get("score", 0.0)),
                4,
            ),
            "retrieved_incidents": result["retrieved_incidents"],
            "recommended_resolution": "Manual review required.",
        }

    return {
        "predicted_category":
            result["predicted_category"],

        "predicted_subcategory":
            result["predicted_subcategory"],

        "confidence_score":
            round(
                float(
                    top_incident.get(
                        "score",
                        0.0,
                    )
                ),
                4,
            ),

        "retrieved_incidents":
            result["retrieved_incidents"],

        "recommended_resolution":
            result["recommended_resolution"],
    }