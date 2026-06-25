from backend.src.graph.state import AgentState
from rag.search import search_incidents


def retrieve_node(state: AgentState):
    print("Running Retrieve Node")

    incidents = search_incidents(
        state["query"],
        top_k=5,
    )

    return {
        "retrieved_incidents": incidents
    }