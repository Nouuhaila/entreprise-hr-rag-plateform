# vectorstore/search_test.py
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from vectorstore.embeddings import embed_texts

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_chunks"


def main():
    client = QdrantClient(url=QDRANT_URL)

    query = "employee termination policy notice period"
    qvec = embed_texts([query])[0]  

    # Filtre 
    flt = Filter(
        must=[
            FieldCondition(key="department", match=MatchValue(value="HR"))
        ]
    )

    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=qvec,
        query_filter=flt,   
        limit=5,
        with_payload=True,
    )

    print("\n=== TOP RESULTS ===")
    for i, p in enumerate(hits.points, 1):
        payload = p.payload or {}
        print(f"\n#{i} score={p.score:.4f}")
        print("chunk_id:", payload.get("chunk_id"))
        print("doc_id:", payload.get("doc_id"))
        print("dataset:", payload.get("dataset_name"))
        print("department:", payload.get("department"))

        text = payload.get("text", "")
        if isinstance(text, str):
            print("text preview:", text[:400].replace("\n", " "))
        else:
            print("text preview: (no text field in payload)")


if __name__ == "__main__":
    main()
