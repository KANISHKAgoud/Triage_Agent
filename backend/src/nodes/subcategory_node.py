def subcategory_node(state):

    from backend.src.utils.logger import logger

    logger.info("Running subcategory Node")

    return {
        "predicted_subcategory":
            state["llm_result"]["subcategory"]
    }