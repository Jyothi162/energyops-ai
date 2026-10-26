
from pathlib import Path

import chromadb
import os
from ollama import Client

ollama_client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://127.0.0.1:11434"
    )
)


# Find the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder containing our support documents
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"

# Folder where ChromaDB stores its data

CHROMA_DIR = Path(
    os.getenv(
        "CHROMA_PATH",
        str(BASE_DIR / "chroma_db")
    )
)


COLLECTION_NAME = "energyops_knowledge"
EMBEDDING_MODEL = "nomic-embed-text"


def ingest_documents():

    print("\n===== ENERGYOPS RAG INGESTION =====")

    # Create or open our persistent vector database
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # Find all text files
    files = sorted(KNOWLEDGE_DIR.glob("*.txt"))

    if not files:
        print("No knowledge-base documents found.")
        return

    for file_path in files:

        print(f"\nProcessing: {file_path.name}")

        # Read the document
        content = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            print("Skipping empty document.")
            continue

        # Generate an embedding using local Ollama
        response = ollama_client.embed(
            model=EMBEDDING_MODEL,
            input=content
        )

        embedding = response["embeddings"][0]

        # Store the text and its embedding
        collection.upsert(
            ids=[file_path.stem],
            documents=[content],
            embeddings=[embedding],
            metadatas=[
                {"source": file_path.name}
            ]
        )

        print("Embedding generated and stored.")

    print("\n===== INGESTION COMPLETE =====")
    print(
        "Documents stored:",
        collection.count()
    )


if __name__ == "__main__":
    ingest_documents()
