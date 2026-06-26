from rag.loader import load_pdf
from rag.chunker import split_text
from rag.embedder import create_embeddings
from rag.retriever import store_chunks


content = load_pdf("uploads/sample.pdf")

chunks = split_text(content)

embeddings = create_embeddings(chunks)

store_chunks(chunks, embeddings)