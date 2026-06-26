from rag.db import get_knowledge_collection


def search(query_embedding, n_results=8):

    print("SEARCH FUNCTION CALLED")

    collection = get_knowledge_collection()

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    print(results)

    return {
        "documents": results["documents"][0],
        "metadata": results["metadatas"][0],
        "distances": results["distances"][0]
    }