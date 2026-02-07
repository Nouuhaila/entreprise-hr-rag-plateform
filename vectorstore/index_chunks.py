import os
import csv
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from vectorstore.embeddings import embed_texts

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_chunks"

CHUNKS_META = os.path.join("data", "chunks_metadata.csv")
CHUNKS_DIR = os.path.join("data", "chunks")

BATCH_SIZE = 64


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    client = QdrantClient(url=QDRANT_URL)

    if not os.path.exists(CHUNKS_META):
        raise FileNotFoundError(f"Missing {CHUNKS_META}. Run ingestion/chunker.py first.")

    with open(CHUNKS_META, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Dict[str, Any]] = list(reader)

    print(f"Found {len(rows)} chunks in metadata.")

    points: List[PointStruct] = []
    texts: List[str] = []

    def flush():
        nonlocal points, texts
        if not points:
            return

        vectors = embed_texts(texts)  

        upsert_points: List[PointStruct] = []
        for p, vec in zip(points, vectors):
            upsert_points.append(PointStruct(id=p.id, vector=vec, payload=p.payload))

        client.upsert(collection_name=COLLECTION_NAME, points=upsert_points)
        print(f"Upserted {len(upsert_points)} points")

        points, texts = [], []

    for idx, r in enumerate(rows):
        chunk_file = r.get("chunk_file", "")  
        chunk_basename = os.path.basename(chunk_file)  
        chunk_path = os.path.join(CHUNKS_DIR, chunk_basename)  

        if not os.path.exists(chunk_path):
            print(f"[SKIP] missing: {chunk_path}")
            continue

        text = read_text(chunk_path)
        if not text.strip():
            print(f"[SKIP] empty: {chunk_path}")
            continue

        payload = {
            "chunk_id": r.get("chunk_id", ""),
            "doc_id": r.get("doc_id", ""),
            "chunk_index": int(r.get("chunk_index", 0) or 0),
            "chunk_file": r.get("chunk_file", ""),
            "dataset_name": r.get("dataset_name", ""),
            "subset": r.get("subset", ""),
            "split": r.get("split", ""),
            "department": r.get("department", ""),
            "document_type": r.get("document_type", ""),
            "category": r.get("category", ""),
            "region": r.get("region", ""),
            "created_at": r.get("created_at", ""),
            "text": text,  
        }

        point_id = idx + 1  
        points.append(PointStruct(id=point_id, vector=[], payload=payload))
        texts.append(text)

        if len(points) >= BATCH_SIZE:
            flush()

    flush()
    print("Done indexing")


if __name__ == "__main__":
    main()
