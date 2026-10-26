
from pathlib import Path

import chromadb
import ollama
import os

# Main project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Existing ChromaDB database

CHROMA_DIR = Path(
    os.getenv(
        "CHROMA_PATH",
        str(BASE_DIR / "chroma_db")
    )
)


COLLECTION_NAME = "energyops_knowledge"
EMBEDDING_MODEL = "nomic-embed-text"


def retrieve_documents(question, top_k=2):

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # Open our vector database
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    # Generate an embedding for the question
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question
    )

    question_embedding = response["embeddings"][0]

    # Find the most relevant documents
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count()),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_documents = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        retrieved_documents.append({
            "source": metadata["source"],
            "content": document,
            "distance": distance
        })

    return retrieved_documents


# Test the retriever
if __name__ == "__main__":

    print("\n===== ENERGYOPS RAG SEARCH =====")

    question = input(
        "Ask a solar support question: "
    ).strip()

    try:
        documents = retrieve_documents(question)

        if not documents:
            print("No documents found.")

        for index, document in enumerate(
            documents,
            start=1
        ):
            print(f"\n===== RESULT {index} =====")
            print("Source:", document["source"])
            print("Distance:", round(document["distance"], 4))
            print("\nContent:")
            print(document["content"])

    except Exception as error:
        print("Retrieval error:", error)
