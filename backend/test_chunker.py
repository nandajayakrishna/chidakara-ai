from rag.loader import load_pdf
from rag.chunker import split_text


content = load_pdf("uploads/sample.pdf")

chunks = split_text(content)

print("\n")
print(f"Total Chunks: {len(chunks)}")

for i, chunk in enumerate(chunks[:5]):
    print("\n")
    print("=" * 50)
    print(f"CHUNK {i+1}")
    print("=" * 50)
    print(chunk)