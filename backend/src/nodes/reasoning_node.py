from backend.src.services.llm.llm_service import generate_triage_response

def reasoning_node(state):

    from backend.src.utils.logger import logger

    logger.info("Running reasoning Node")

    result = generate_triage_response(
        query=state["query"],
        retrieved_incidents=state["retrieved_incidents"],
    )

    return {
        "llm_result": result,

        "reasoning": result["reasoning"],

        "priority": result["priority"],

        "confidence_score": result["confidence"],

        "requires_manual_review": result["requires_manual_review"],
    }