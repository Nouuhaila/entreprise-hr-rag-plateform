from qdrant_client import QdrantClient
from vectorstore.embedding_generator import embedding_dim
from qdrant_client.models import Distance, VectorParams

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_chunks"

def main():
    client = QdrantClient(url=QDRANT_URL)
    dim = embedding_dim()

    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"🗑️ Deleted collection {COLLECTION_NAME}")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    print(f"✅ Recreated collection {COLLECTION_NAME} dim={dim}")

if __name__ == "__main__":
    main()