import os
import chromadb

_client = None

def get_db_client():
    global _client

    if _client is None:
        db_path = os.path.abspath("chroma_db")

        print("=" * 60)
        print("CHROMA DB PATH:", db_path)
        print("PATH EXISTS:", os.path.exists(db_path))
        print("=" * 60)

        _client = chromadb.PersistentClient(path=db_path)

    return _client


def get_knowledge_collection(create_if_missing=False):
    client = get_db_client()

    if create_if_missing:
        return client.get_or_create_collection("chidakara_knowledge")

    return client.get_collection("chidakara_knowledge")