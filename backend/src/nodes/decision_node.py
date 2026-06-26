from backend.src.graph.state import AgentState
from backend.src.utils.keyword_boost import has_hardware_keyword

UNKNOWN_CATEGORY_THRESHOLD = 0.30


def decision_node(state: AgentState):

    incidents = state["retrieved_incidents"]

    if not incidents:
        return {
            "predicted_category": "Unknown",
            "predicted_subcategory": "Unknown",
            "recommended_resolution": "Manual review required.",
            "confidence_score": 0.0,
        }

    top = max(
        incidents,
        key=lambda x: float(x.get("score", 0.0))
    )

    confidence = float(top.get("score", 0.0))

    category = state["predicted_category"]
    subcategory = state["predicted_subcategory"]
    resolution = state["recommended_resolution"]

    if confidence < UNKNOWN_CATEGORY_THRESHOLD:

        category = "Unknown"
        subcategory = "Unknown"
        resolution = "Manual review required."

    elif (
        has_hardware_keyword(state["query"])
        and top["category"] == "Hardware"
    ):

        category = top["category"]
        subcategory = top["subcategory"]

    if not category or category == "Unknown":
        category = top["category"]

    if not subcategory or subcategory == "Unknown":
        subcategory = top["subcategory"]

    return {
        "predicted_category": category,
        "predicted_subcategory": subcategory,
        "recommended_resolution": resolution,
        "confidence_score": confidence,
    }