import os
import json
import time
import logging
from glob import glob
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain.schema import Document

# ---- Load environment ----
load_dotenv()

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---- Configs ----
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_CLOUD_API_KEY = os.getenv("QDRANT_CLOUD_API_KEY")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 1536))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
BATCH_SLEEP_TIME = int(os.getenv("BATCH_SLEEP_TIME", 2))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
TICKETS_FILES = Path(os.getenv("TICKETS_FILES", "./tickets/*.json"))
INGESTION_TRACKER_FILE = Path(os.getenv("INGESTION_TRACKER_FILE", "./ingest-tracker/ingested_tickets.json"))
TICKET_COLLECTION = os.getenv("TICKET_COLLECTION", "tickets")

# ---- Qdrant client and embeddings ----
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_CLOUD_API_KEY)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

# ---- Track ingested files ----
def load_ingested_files():
    if INGESTION_TRACKER_FILE.exists():
        with open(INGESTION_TRACKER_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_ingested_file(file_path):
    ingested = load_ingested_files()
    ingested.add(str(file_path))
    INGESTION_TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INGESTION_TRACKER_FILE, "w") as f:
        json.dump(list(ingested), f)

# ---- Create collection if not exists ----
def create_collection_if_not_exists(collection_name: str):
    existing = [c.name for c in qdrant_client.get_collections().collections]
    if collection_name not in existing:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        logger.info(f"Collection '{collection_name}' created.")
    else:
        logger.info(f"Collection '{collection_name}' already exists.")

# ---- Ingest tickets ----
def ingest_tickets(collection_name: str = TICKET_COLLECTION):
    create_collection_if_not_exists(collection_name)
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=collection_name, embedding=embeddings)

    ingested_files = load_ingested_files()
    files = glob(str(TICKETS_FILES))
    if not files:
        logger.warning(f"No ticket files found at {TICKETS_FILES}")
        return

    for file_path in files:
        if file_path in ingested_files:
            logger.info(f"Skipping already ingested file: {file_path}")
            continue

        logger.info(f"Ingesting ticket file: {file_path}")

        try:
            with open(file_path, "r") as f:
                ticket_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            continue

        docs = []
        for ticket in ticket_data:
            text_content = (
                f"Ticket ID: {ticket.get('ticketId')}\n"
                f"Ticket Type: {ticket.get('ticketType')}\n"
                f"Message: {ticket.get('message')}\n"
                f"Suggested Action: {ticket.get('suggestedAction')}"
            )
            metadata = ticket.copy()  # use ticketId from JSON
            docs.append(Document(page_content=text_content, metadata=metadata))

        # Ingest in batches
        for i in range(0, len(docs), BATCH_SIZE):
            batch = docs[i:i + BATCH_SIZE]
            vector_store.add_documents(batch)
            logger.info(f"Ingested batch {i // BATCH_SIZE + 1} ({len(batch)} tickets)")
            time.sleep(BATCH_SLEEP_TIME)

        save_ingested_file(file_path)
        logger.info(f"Finished ingestion of tickets into '{collection_name}'.")

# ---- CLI support ----
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest tickets into Qdrant")
    parser.add_argument("--collection", type=str, default=TICKET_COLLECTION, help="Qdrant collection name")
    args = parser.parse_args()
    ingest_tickets(args.collection)
