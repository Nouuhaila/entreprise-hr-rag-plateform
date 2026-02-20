import os
import csv
import hashlib
from typing import List, Dict, Any, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from vectorstore.embedding_generator import embed_texts

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_chunks"

CHUNKS_META = os.path.join("data", "chunks_metadata.csv")
CHUNKS_DIR = os.path.join("data", "chunks")

BATCH_SIZE = 64


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

import hashlib

def stable_point_id(payload: dict) -> int:
    """
    Return a stable UNSIGNED INT id for Qdrant.
    hash chunk_id into 64-bit int.
    """
    chunk_id = str(payload.get("chunk_id") or "").strip()
    if not chunk_id:
        # fallback
        doc_id = str(payload.get("doc_id") or "").strip()
        chunk_index = str(payload.get("chunk_index") or "").strip()
        chunk_id = f"{doc_id}::{chunk_index}"

    # 64-bit unsigned int from sha1 digest
    h = hashlib.sha1(chunk_id.encode("utf-8")).digest()
    return int.from_bytes(h[:8], byteorder="big", signed=False)


def main():
    client = QdrantClient(url=QDRANT_URL)

    if not os.path.exists(CHUNKS_META):
        raise FileNotFoundError(f"Missing {CHUNKS_META}. Run ingestion/chunker.py first.")

    with open(CHUNKS_META, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Dict[str, Any]] = list(reader)

    print(f"Found {len(rows)} chunks in metadata.")

    batch_texts: List[str] = []
    batch_payloads: List[Dict[str, Any]] = []

    def flush():
        nonlocal batch_texts, batch_payloads
        if not batch_payloads:
            return

        vectors = embed_texts(batch_texts, batch_size=32, show_progress=False, normalize=True)

        points: List[PointStruct] = []
        for payload, vec in zip(batch_payloads, vectors):
            pid = stable_point_id(payload)
            points.append(PointStruct(id=pid, vector=vec, payload=payload))

        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Upserted {len(points)} points")

        batch_texts, batch_payloads = [], []

    for r in rows:
        chunk_file = r.get("chunk_file", "") or ""
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
            "text": text,  #
        }

        batch_payloads.append(payload)
        batch_texts.append(text)

        if len(batch_payloads) >= BATCH_SIZE:
            flush()

    flush()
    print("Done indexing.")


if __name__ == "__main__":
    main()
