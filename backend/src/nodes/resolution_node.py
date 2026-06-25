def resolution_node(state):

    print("Running Resolution Node")

    return {
        "recommended_resolution":
            state["llm_result"]["recommended_resolution"]
    }