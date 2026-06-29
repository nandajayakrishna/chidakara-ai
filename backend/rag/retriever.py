from rag.db import get_knowledge_collection


def search(query_embedding, n_results=8):

    print("=" * 60)
    print("SEARCH FUNCTION CALLED")
    print("=" * 60)

    collection = get_knowledge_collection()

    print("Collection count before query:", collection.count())

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