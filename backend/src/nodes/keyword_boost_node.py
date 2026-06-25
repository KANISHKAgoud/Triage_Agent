from backend.src.graph.state import AgentState
from backend.src.utils.keyword_boost import apply_hardware_keyword_boost


def keyword_boost_node(state: AgentState):

    print("Running Keyword Boost Node")

    boosted = apply_hardware_keyword_boost(
        state["query"],
        state["retrieved_incidents"],
    )

    return {
        "retrieved_incidents": boosted
    }