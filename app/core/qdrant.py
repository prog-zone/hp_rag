from qdrant_client import QdrantClient
from app.core.config import settings

# Initialize a singleton client
qdrant_client = QdrantClient(
    host=settings.QDRANT_HOST, 
    port=6333,
    prefer_grpc=False
)