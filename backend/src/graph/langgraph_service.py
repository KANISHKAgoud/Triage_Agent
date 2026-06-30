from backend.src.graph.builder import graph

def process_query_langgraph(
    query: str,
    ticket_id: str = "AGENT",
    ):
    result = graph.invoke(
        {
            "query": query,
            "ticket_id": ticket_id,
            "node_metrics": {},
            "execution_path": [],
        }
    )

    return {
        "reasoning": result["reasoning"],

        "predicted_category": result["predicted_category"],

        "predicted_subcategory": result["predicted_subcategory"],

        "priority": result["priority"],

        "confidence_score": round(result["confidence_score"], 4),

        "requires_manual_review": result["requires_manual_review"],

        "retrieved_incidents": result["retrieved_incidents"],

        "recommended_resolution": result["recommended_resolution"],
    }
