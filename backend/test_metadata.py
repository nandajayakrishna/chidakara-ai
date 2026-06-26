# test_metadata.py

import chromadb

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_collection(
    "chidakara_knowledge"
)

results = collection.get()

print(results["metadatas"][:5])