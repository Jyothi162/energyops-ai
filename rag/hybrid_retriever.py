
import re

import chromadb
import ollama
from rank_bm25 import BM25Okapi

from rag.retriever import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


def tokenize(text):
    """Convert text into lowercase words."""
    return re.findall(r"[a-z0-9]+", text.lower())


def hybrid_retrieve(question, top_k=2):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)

    records = collection.get(include=["documents", "metadatas"])
    documents = records["documents"]
    metadatas = records["metadatas"]
    ids = records["ids"]

    if not documents:
        return []

    # 1. Semantic retrieval
    embedding_response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question,
    )
    question_embedding = embedding_response["embeddings"][0]

    semantic_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=len(documents),
        include=["distances"],
    )

    semantic_ids = semantic_results["ids"][0]

    # 2. BM25 keyword retrieval
    tokenized_documents = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_documents)

    keyword_scores = bm25.get_scores(tokenize(question))

    keyword_order = sorted(
        range(len(documents)),
        key=lambda index: keyword_scores[index],
        reverse=True,
    )
    keyword_ids = [ids[index] for index in keyword_order]

    # 3. Reciprocal Rank Fusion
    # Larger RRF scores indicate better combined rankings.
    rrf_scores = {doc_id: 0.0 for doc_id in ids}
    rrf_k = 60

    for ranking in [semantic_ids, keyword_ids]:
        for rank, doc_id in enumerate(ranking, start=1):
            rrf_scores[doc_id] += 1.0 / (rrf_k + rank)

    # 4. Return the highest-ranked documents
    ranked_ids = sorted(
        ids,
        key=lambda doc_id: rrf_scores[doc_id],
        reverse=True,
    )

    record_lookup = {
        doc_id: {
            "source": metadata.get("source", "unknown"),
            "content": document,
        }
        for doc_id, document, metadata in zip(
            ids, documents, metadatas
        )
    }

    return [
        {
            **record_lookup[doc_id],
            "rrf_score": rrf_scores[doc_id],
        }
        for doc_id in ranked_ids[:top_k]
    ]


if __name__ == "__main__":
    questions = [
        "Why is the amount on my solar power statement higher than expected?",
        "How do I get help with a payment discrepancy?",
        "What should I do if my inverter keeps shutting down?",
        "How can I check whether my solar panel installation is delayed?",
        "Who should I contact if my solar equipment shows an error code?",
    ]

    for question in questions:
        print("\nQUESTION:", question)

        for rank, result in enumerate(
            hybrid_retrieve(question, top_k=2),
            start=1,
        ):
            print(
                f"{rank}. {result['source']} "
                f"(RRF score: {result['rrf_score']:.6f})"
            )
