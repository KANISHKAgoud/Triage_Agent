from backend.src.graph.state import AgentState


def manual_review_node(state: AgentState):

    print("Manual Review Node")

    return {

        "predicted_category": "Unknown",

        "predicted_subcategory": "Unknown",

        "recommended_resolution": "Manual review required.",

    }