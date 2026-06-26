from backend.src.graph.state import AgentState
from rag.search import search_incidents


def retrieve_node(state: AgentState):
    from backend.src.utils.logger import logger

    from backend.src.utils.timer import NodeTimer
    from backend.src.utils.logger import logger

    def retrieve_node(state):

        with NodeTimer() as timer:

            logger.info("Running Retrieve Node")

            incidents = ...

        logger.info(f"Retrieve Node completed in {timer.elapsed:.3f}s")

    incidents = search_incidents(
        state["query"],
        top_k=5,
    )

    return {
        "retrieved_incidents": incidents
    }