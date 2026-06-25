from rag.ingest import get_collection


def get_vector_stats():

    collection = get_collection()

    return {
        "documents": collection.count(),
        "vector_db": "ChromaDB",
        "status": "healthy",
    }