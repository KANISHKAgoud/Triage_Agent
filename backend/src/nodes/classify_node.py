from backend.src.graph.state import AgentState


def classify_node(state: AgentState):

    from backend.src.utils.logger import logger

    logger.info("Running classify Node")

    result = state.get("llm_result", {})

    return {
        "predicted_category": result.get("category", "Unknown"),
        "predicted_subcategory": result.get("subcategory", "Unknown"),
    }