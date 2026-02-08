import os
import csv
import json
import hashlib
from collections import Counter
from statistics import mean

CHUNKS_META = os.path.join("data", "chunks_metadata.csv")
CHUNKS_DIR = os.path.join("data", "chunks")
OUT_DIR = os.path.join("data", "processed")
REPORT_JSON = os.path.join(OUT_DIR, "validation_report.json")
SUMMARY_CSV = os.path.join(OUT_DIR, "validation_summary.csv")

REQUIRED_FIELDS = [
    "chunk_id",
    "doc_id",
    "chunk_index",
    "chunk_file",
    "dataset_name",
    "split",
    "department",
    "document_type",
    "category",
    "region",
]

def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def main():
    if not os.path.exists(CHUNKS_META):
        raise FileNotFoundError(f"Missing {CHUNKS_META}. Run ingestion/chunker.py first.")

    os.makedirs(OUT_DIR, exist_ok=True)

    with open(CHUNKS_META, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    missing_files = 0
    empty_chunks = 0
    missing_meta_rows = 0
    lengths = []
    sha_counts = Counter()

    missing_fields_counts = Counter()
    per_dataset = Counter()
    per_department = Counter()

    for r in rows:
        missing_fields = [k for k in REQUIRED_FIELDS if not (r.get(k) or "").strip()]
        if missing_fields:
            missing_meta_rows += 1
            for k in missing_fields:
                missing_fields_counts[k] += 1

        per_dataset[r.get("dataset_name", "unknown")] += 1
        per_department[r.get("department", "unknown")] += 1

        chunk_file = r.get("chunk_file", "")
        chunk_path = os.path.join(CHUNKS_DIR, os.path.basename(chunk_file))

        if not os.path.exists(chunk_path):
            missing_files += 1
            continue

        text = _read_text(chunk_path).strip()
        if not text:
            empty_chunks += 1
            continue

        lengths.append(len(text))
        sha = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
        sha_counts[sha] += 1

    duplicates = sum(c - 1 for c in sha_counts.values() if c > 1)

    report = {
        "total_chunks": total,
        "missing_chunk_files": missing_files,
        "empty_chunks": empty_chunks,
        "duplicate_chunks": duplicates,
        "missing_metadata_rows": missing_meta_rows,
        "missing_fields_counts": dict(missing_fields_counts),
        "length_chars": {
            "count": len(lengths),
            "min": min(lengths) if lengths else 0,
            "max": max(lengths) if lengths else 0,
            "avg": mean(lengths) if lengths else 0,
        },
        "distribution": {
            "by_dataset": dict(per_dataset),
            "by_department": dict(per_department),
        },
    }

    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["total_chunks", total])
        w.writerow(["missing_chunk_files", missing_files])
        w.writerow(["empty_chunks", empty_chunks])
        w.writerow(["duplicate_chunks", duplicates])
        w.writerow(["missing_metadata_rows", missing_meta_rows])

    print("Validation complete")
    print(f"- report:  {REPORT_JSON}")
    print(f"- summary: {SUMMARY_CSV}")

if __name__ == "__main__":
    main()
