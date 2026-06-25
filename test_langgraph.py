from backend.src.graph.langgraph_service import graph

result = graph.invoke(
    {
        "query": "VPN login failing after changing phone"
    }
)

print(result)