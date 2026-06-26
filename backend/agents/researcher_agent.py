from rag.embedder import create_embeddings
from rag.retriever import search


def _core_gather(question, context=None):
    queries = [question]

    q = question.lower()

    if "summarize" in q:
        queries += [
            "projects",
            "skills",
            "education",
            "experience"
        ]

    elif "compare" in q:
        queries += [
            "first topic",
            "second topic"
        ]

    elif "publication" in q:
        queries += [
            "publications"
        ]

    elif "experience" in q:
        queries += [
            "work experience"
        ]

    documents = []
    metadata = []
    seen = set()

    all_chunks = []
    all_scores = []
    all_pdfs = set()

    print()
    print("===== RESEARCH AGENT =====")

    for q_term in queries:
        print(q_term)

    print("==========================")

    for query in queries:

        print("Searching:", query)

        embedding = create_embeddings([query])[0]

        results = search(
            query_embedding=embedding,
            n_results=3
        )

        print("Returned:", results)

        docs = results.get("documents", [])
        metas = results.get("metadata", [])
        dists = results.get("distances", [])

        # Ensure lists are aligned
        for i in range(len(docs)):
            doc = docs[i]
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else 0.0

            all_chunks.append(doc)
            all_scores.append(dist)
            if isinstance(meta, dict) and meta.get("source"):
                all_pdfs.add(meta.get("source"))

            if doc not in seen:
                seen.add(doc)
                documents.append(doc)
                metadata.append(meta)

    if context is not None:
        context.debug_metadata["research"] = {
            "retrieved_chunks": all_chunks,
            "similarity_scores": all_scores,
            "pdf_names": list(all_pdfs)
        }

    return documents, metadata


def gather(context_or_question):
    """
    Gather relevant documents from ChromaDB based on the query.
    Supports ExecutionContext and backward compatible string questions.
    """
    if hasattr(context_or_question, 'question'):
        ctx = context_or_question
        docs, meta = _core_gather(ctx.question, context=ctx)
        ctx.retrieved_documents = docs
        ctx.metadata = meta
        return docs, meta
    else:
        return _core_gather(context_or_question)