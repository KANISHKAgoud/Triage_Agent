from backend.src.graph.state import AgentState

UNKNOWN_CATEGORY_THRESHOLD = 0.30


def confidence_node(state: AgentState):

    print("Running Confidence Node")

    incidents = state["retrieved_incidents"]

    if not incidents:
        return {
            "confidence_score": 0.0,
            "predicted_category": "Unknown",
            "predicted_subcategory": "Unknown",
            "recommended_resolution": "Manual review required.",
        }

    top = incidents[0]

    confidence = float(top.get("score", 0))

    return {
        "confidence_score": confidence
    }