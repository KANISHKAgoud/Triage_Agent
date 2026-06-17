from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from backend.llm_service import generate_triage_response
from rag.search import search_incidents


class AgentState(TypedDict):
    query: str
    retrieved_incidents: list[dict[str, Any]]
    llm_result: dict[str, str]


def retrieve_node(state: AgentState):
    incidents = search_incidents(
        state["query"],
        top_k=5,
    )

    return {
        "retrieved_incidents": incidents
    }


def llm_node(state: AgentState):
    result = generate_triage_response(
        query=state["query"],
        retrieved_incidents=state["retrieved_incidents"],
    )

    return {
        "llm_result": result
    }


def response_node(state: AgentState):
    return state


builder = StateGraph(AgentState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("llm", llm_node)
builder.add_node("response", response_node)

builder.set_entry_point("retrieve")

builder.add_edge("retrieve", "llm")
builder.add_edge("llm", "response")
builder.add_edge("response", END)

graph = builder.compile()

def process_query_langgraph(query: str):
    result = graph.invoke(
        {
            "query": query
        }
    )

    top_incident = result["retrieved_incidents"][0]

    return {
        "predicted_category": result["llm_result"]["category"],
        "predicted_subcategory": result["llm_result"]["subcategory"],
        "confidence_score": round(
            float(top_incident.get("score", 0.0)),
            4,
        ),
        "retrieved_incidents": result["retrieved_incidents"],
        "recommended_resolution": result["llm_result"][
            "recommended_resolution"
        ],
    }