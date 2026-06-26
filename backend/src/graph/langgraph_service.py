
from langgraph.graph import END, StateGraph
from backend.src.graph.state import AgentState
from backend.src.nodes.save_node import save_node
from backend.src.nodes.decision_node import decision_node


from backend.src.nodes.retrieve_node import retrieve_node
from backend.src.nodes.confidence_node import confidence_node

from backend.src.nodes.keyword_boost_node import keyword_boost_node
from backend.src.nodes.response_node import response_node


from backend.src.nodes.reasoning_node import reasoning_node
from backend.src.nodes.category_node import category_node
from backend.src.nodes.subcategory_node import subcategory_node

from backend.src.nodes.resolution_node import resolution_node


builder = StateGraph(AgentState)

builder.add_node(
    "retrieve",
    retrieve_node,
)

builder.add_node(
    "keyword_boost",
    keyword_boost_node,
)

builder.add_node(
    "confidence",
    confidence_node,
)

builder.add_node(
    "reasoning",
    reasoning_node,
)

builder.add_node(
    "category",
    category_node,
)

builder.add_node(
    "subcategory",
    subcategory_node,
)

builder.add_node(
    "resolution",
    resolution_node,
)

builder.add_node(
    "decision",
    decision_node,
)

builder.add_node(
    "save",
    save_node,
)

builder.add_node(
    "response",
    response_node,
)

builder.set_entry_point("retrieve")

builder.add_edge(
    "retrieve",
    "keyword_boost",
)
builder.add_edge(
    "keyword_boost",
    "confidence",
)
builder.add_edge(
    "confidence",
    "reasoning",
)

builder.add_edge(
    "reasoning",
    "category",
)

builder.add_edge(
    "category",
    "subcategory",
)

builder.add_edge(
    "subcategory",
    "resolution",
)

builder.add_edge(
    "resolution",
    "decision",
)

builder.add_edge(
    "decision",
    "save",
)

builder.add_edge(
    "save",
    "response",
)

builder.add_edge(
    "response",
    END,
)

graph = builder.compile()


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
        "predicted_category": result["predicted_category"],
        "predicted_subcategory": result["predicted_subcategory"],
        "confidence_score": round(result["confidence_score"], 4),
        "retrieved_incidents": result["retrieved_incidents"],
        "recommended_resolution": result["recommended_resolution"],
    }
