
from database import create_database
from rag.ingest import ingest_documents


def initialize():
    print("===== ENERGYOPS INITIALIZATION =====")

    print("Initializing SQLite database...")
    create_database()

    print("Initializing ChromaDB...")
    ingest_documents()

    print("Initialization completed successfully!")


if __name__ == "__main__":
    initialize()
