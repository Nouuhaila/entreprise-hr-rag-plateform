import os
import csv
import re
from datetime import datetime

RAW_DIR = os.path.join("data", "raw")
CHUNKS_DIR = os.path.join("data", "chunks")
METADATA_PATH = os.path.join("data", "metadata.csv")
CHUNKS_METADATA_PATH = os.path.join("data", "chunks_metadata.csv")
METADATA_FIELDS = [
    "doc_id","file_name","dataset_name","subset","split","subset_percent",
    "department","document_type","category","region","year","source","created_at"
]


CHUNK_SIZE_CHARS = 3500      # 800-1200 tokens selon le texte
CHUNK_OVERLAP_CHARS = 400

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def safe_name(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s).strip("_")
    return s[:120] if s else "chunk"

def chunk_text(text: str, chunk_size: int, overlap: int):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks

def read_metadata_rows():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=METADATA_FIELDS)
        return list(reader)


def write_chunks_metadata_header():
    ensure_dir(os.path.dirname(CHUNKS_METADATA_PATH))
    if not os.path.exists(CHUNKS_METADATA_PATH):
        with open(CHUNKS_METADATA_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "chunk_id",
                    "doc_id",
                    "chunk_index",
                    "chunk_file",
                    "dataset_name",
                    "subset",
                    "split",
                    "department",
                    "document_type",
                    "category",
                    "region",
                    "created_at",
                ],
            )
            writer.writeheader()

def append_chunk_row(row: dict):
    write_chunks_metadata_header()
    with open(CHUNKS_METADATA_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)

def main():
    ensure_dir(CHUNKS_DIR)
    rows = read_metadata_rows()
    now = datetime.utcnow().isoformat()

    total_chunks = 0

    for r in rows:
        doc_id = r["doc_id"]
        file_name = r["file_name"]  
        abs_path = os.path.join(RAW_DIR, file_name)

        if not os.path.exists(abs_path):
            print(f"[SKIP] missing file: {abs_path}")
            continue

        with open(abs_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS)

        for idx, ch in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{idx:04d}"
            chunk_file = f"{safe_name(doc_id)}_chunk_{idx:04d}.txt"
            chunk_abs = os.path.join(CHUNKS_DIR, chunk_file)

            with open(chunk_abs, "w", encoding="utf-8") as out:
                out.write(ch)

            append_chunk_row(
                {
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "chunk_file": f"chunks/{chunk_file}",
                    "dataset_name": r["dataset_name"],
                    "subset": r["subset"],
                    "split": r["split"],
                    "department": r["department"],
                    "document_type": r["document_type"],
                    "category": r["category"],
                    "region": r["region"],
                    "created_at": now,
                }
            )

            total_chunks += 1

    print(f"Done. total_chunks={total_chunks} -> {CHUNKS_DIR}")
    print(f"Wrote chunks metadata -> {CHUNKS_METADATA_PATH}")

if __name__ == "__main__":
    main()
