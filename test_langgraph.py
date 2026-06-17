from backend.langgraph_service import graph

result = graph.invoke(
    {
        "query": "VPN login failing after changing phone"
    }
)

print(result)