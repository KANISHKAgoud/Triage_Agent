from backend.src.graph.state import AgentState


def resolution_node(state: AgentState):

    print("Running Resolution Node")

    result = state.get("llm_result", {})

    return {
        "recommended_resolution": result.get(
            "recommended_resolution",
            "Manual review required.",
        )
    }