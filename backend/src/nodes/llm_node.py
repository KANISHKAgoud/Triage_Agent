from backend.src.graph.state import AgentState
from backend.src.services.llm_service import (
    generate_triage_response,
    LLMServiceError,
)


def llm_node(state: AgentState):

    print("Running LLM Node")

    try:

        result = generate_triage_response(
            query=state["query"],
            retrieved_incidents=state["retrieved_incidents"],
        )

    except LLMServiceError:

        result = {}

    return {
        "llm_result": result
    }