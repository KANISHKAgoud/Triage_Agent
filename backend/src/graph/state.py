from typing import Any, TypedDict


class AgentState(TypedDict):
    # Input
    query: str
    ticket_id: str

    # Retrieval
    retrieved_incidents: list[dict[str, Any]]
    
    llm_result: dict

    # LLM output (raw)
    llm_result: dict[str, Any]

    # Final prediction
    predicted_category: str
    predicted_subcategory: str
    recommended_resolution: str
    confidence_score: float