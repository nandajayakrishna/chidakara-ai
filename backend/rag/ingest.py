from rag.loader import load_pdf
from rag.chunker import split_text
from rag.embedder import create_embeddings
from rag.db import get_knowledge_collection


def ingest_document(file_path):

    text = load_pdf(file_path)

    chunks = split_text(text)

    embeddings = create_embeddings(chunks)

    ids = [
        f"{file_path}_{i}"
        for i in range(len(chunks))
    ]

    metadata = [
        {
            "source": file_path,
            "chunk": i
        }
        for i in range(len(chunks))
    ]

    collection = get_knowledge_collection(create_if_missing=True)

    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        ids=ids,
        metadatas=metadata
    )

    return len(chunks)