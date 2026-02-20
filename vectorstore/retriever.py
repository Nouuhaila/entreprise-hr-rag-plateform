from typing import Optional, Dict, Any, List
from qdrant_client import QdrantClient
from qdrant_client.models import Filter

from vectorstore.embedding_generator import embed_text
from vectorstore.metadata_filter import build_filter

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_chunks"

def retrieve(
    query: str,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    with_payload: bool = True,
) -> List[Dict[str, Any]]:
    client = QdrantClient(url=QDRANT_URL)
    qvec = embed_text(query)

    flt: Optional[Filter] = build_filter(**filters) if filters else None

    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=qvec,
        query_filter=flt,
        limit=top_k,
        with_payload=with_payload,
    )

    results: List[Dict[str, Any]] = []
    for p in hits.points:
        results.append({"id": p.id, "score": float(p.score), "payload": p.payload or {}})
    return results

if __name__ == "__main__":
    q = "compliance regulation obligations"
    res = retrieve(q, top_k=5, filters={"department": "Compliance"})
    for i, r in enumerate(res, 1):
        print(i, r["score"], r["payload"].get("doc_id"), r["payload"].get("chunk_id"))