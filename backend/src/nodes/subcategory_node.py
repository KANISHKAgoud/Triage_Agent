def subcategory_node(state):

    print("Running Subcategory Node")

    return {
        "predicted_subcategory":
            state["llm_result"]["subcategory"]
    }