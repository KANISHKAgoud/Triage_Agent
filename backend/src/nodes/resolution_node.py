def resolution_node(state):

    from backend.src.utils.logger import logger

    logger.info("Running Resolution Node")

    return {
        "recommended_resolution":
            state["llm_result"]["recommended_resolution"]
    }