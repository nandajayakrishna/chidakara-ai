import chromadb

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_collection(
    "chidakara_knowledge"
)

print(
    collection.count()
)