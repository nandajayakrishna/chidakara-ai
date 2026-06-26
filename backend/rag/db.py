import chromadb

_client = None

def get_db_client():
    """
    Returns a singleton instance of the ChromaDB PersistentClient.
    """
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path="chroma_db")
    return _client

def get_knowledge_collection(create_if_missing=False):
    """
    Retrieves or creates the 'chidakara_knowledge' collection from ChromaDB.
    """
    client = get_db_client()
    if create_if_missing:
        return client.get_or_create_collection("chidakara_knowledge")
    return client.get_collection("chidakara_knowledge")
