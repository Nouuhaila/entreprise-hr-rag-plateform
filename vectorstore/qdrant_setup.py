# vectorstore/qdrant_setup.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from vectorstore.embeddings import embedding_dim

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_chunks"

def main():
    client = QdrantClient(url=QDRANT_URL)
    print("Connected to Qdrant.")
    print("Existing collections:", [c.name for c in client.get_collections().collections])

    dim = embedding_dim()

    # Create collection if not exists
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"✅ Created collection '{COLLECTION_NAME}' with dim={dim}")
    else:
        print(f"✅ Collection '{COLLECTION_NAME}' already exists (dim should be {dim})")

if __name__ == "__main__":
    main()
