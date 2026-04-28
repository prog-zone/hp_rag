from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from ingestion.processors import load_hp_docs
from ingestion.chunking import split_documents

load_dotenv()

COLLECTION_NAME = "harry_potter_collection"
DATA_PATH = "./data"

def run_pipeline():
    # 1. Setup Qdrant Client and Embeddings
    client = QdrantClient(host="localhost", port=6333)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small") # 1536 dimensions

    # 2. Create Collection if it doesn't exist
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION_NAME}")

    # 3. Process Data
    raw_docs = load_hp_docs(DATA_PATH)
    chunks = split_documents(raw_docs)

    # 4. Load into Qdrant
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    print("Uploading vectors to Qdrant (this may take a minute)...")
    vector_store.add_documents(chunks)
    print("Ingestion Complete!")

if __name__ == "__main__":
    run_pipeline()