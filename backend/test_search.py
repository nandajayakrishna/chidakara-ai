from sentence_transformers import SentenceTransformer
from rag.retriever import search


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

query = "What machine learning projects has Nanda done?"

query_embedding = model.encode(query)

results = search(query_embedding)

print("\nRESULTS\n")

for i, doc in enumerate(results):
    print(f"\nResult {i+1}")
    print("-" * 40)
    print(doc)