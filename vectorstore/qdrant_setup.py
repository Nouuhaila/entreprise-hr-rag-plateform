from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from vectorstore.embedding_generator import embedding_dim

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_chunks"

def main():
    client = QdrantClient(url=QDRANT_URL)
    print("Connected to Qdrant.")

    dim = embedding_dim()
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"✅ Created collection '{COLLECTION_NAME}' with dim={dim}")
        return

    info = client.get_collection(COLLECTION_NAME)
    size = None
    distance = None

    try:
        size = info.config.params.vectors.size
        distance = info.config.params.vectors.distance
    except Exception:
        pass

    if size is not None and size != dim:
        print(f"❌ Dimension mismatch: collection size={size} but embedding_dim={dim}")
        print("   Fix: delete & recreate collection, or use the matching embedding model.")
    else:
        print(f"✅ Collection '{COLLECTION_NAME}' exists and dim looks OK ({dim}).")

    if distance is not None and str(distance).upper() != "COSINE":
        print(f"⚠️ Distance mismatch: collection distance={distance} (expected COSINE)")
    else:
        print("✅ Distance looks OK (COSINE).")

if __name__ == "__main__":
    main()
