from rag.loader import load_pdf
from rag.chunker import split_text
from rag.embedder import create_embeddings


content = load_pdf("uploads/sample.pdf")

chunks = split_text(content)

embeddings = create_embeddings(chunks)

print("\n")
print("Total Chunks:", len(chunks))
print("Embedding Shape:", embeddings.shape)

print("\nFirst Vector Preview:\n")

print(embeddings[0][:10])