from backend.src.graph.state import AgentState


def response_node(state: AgentState):

    from backend.src.utils.logger import logger

    logger.info("Running response Node")

    return state