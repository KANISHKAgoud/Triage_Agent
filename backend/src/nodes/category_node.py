def category_node(state):

    print("Running Category Node")

    return {
        "predicted_category":
            state["llm_result"]["category"]
    }