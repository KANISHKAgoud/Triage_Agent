def category_node(state):

    from backend.src.utils.logger import logger

    logger.info("Running category Node")

    return {
        "predicted_category":
            state["llm_result"]["category"]
    }