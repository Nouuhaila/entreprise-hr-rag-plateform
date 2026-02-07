import os
import csv
import re
import json
import time
import argparse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

from datasets import load_dataset
from tqdm import tqdm
from loguru import logger


RAW_DIR = os.path.join("data", "raw")
METADATA_PATH = os.path.join("data", "metadata.csv")
REPORT_PATH = os.path.join("data", "ingestion_report.json")


def safe_name(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s).strip("_")
    return s[:120] if s else "doc"


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def sizeof_dir_bytes(path: str) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

METADATA_FIELDS = [
 "doc_id","file_name","dataset_name","subset","split","subset_percent",
 "department","document_type","category","region","year","source","created_at"
]

def ensure_metadata_header() -> None:
    ensure_dir(os.path.dirname(METADATA_PATH))
    if not os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,METADATA_FIELDS
            )
            writer.writeheader()
            


def append_metadata(row: Dict[str, Any]) -> None:
    ensure_metadata_header()
    row = {k: row.get(k, "") for k in METADATA_FIELDS}
    with open(METADATA_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METADATA_FIELDS)
        writer.writerow(row)





def extract_text_generic(ex: Dict[str, Any]) -> Optional[str]:
    for k in ["text", "content", "document", "body", "article"]:
        v = ex.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
            joined = "\n".join([x.strip() for x in v if x and x.strip()])
            return joined.strip() if joined else None
    return None


def build_policyqa_text(ex: Dict[str, Any]) -> Optional[str]:
    """
     On convertit en un "document policy" unique.
    """
    q = ex.get("question")
    ctx = ex.get("context") or ex.get("passage") or ex.get("policy")
    ans = ex.get("answer") or ex.get("answers")

    parts: List[str] = []
    if isinstance(q, str) and q.strip():
        parts.append(f"Question:\n{q.strip()}")
    if isinstance(ctx, str) and ctx.strip():
        parts.append(f"Context:\n{ctx.strip()}")

    if isinstance(ans, str) and ans.strip():
        parts.append(f"Answer:\n{ans.strip()}")
    elif isinstance(ans, list):
        clean = [str(a).strip() for a in ans if str(a).strip()]
        if clean:
            parts.append("Answer:\n" + "\n".join(clean[:3]))
    elif isinstance(ans, dict):
        txt = ans.get("text")
        if isinstance(txt, list):
            clean = [str(a).strip() for a in txt if str(a).strip()]
            if clean:
                parts.append("Answer:\n" + "\n".join(clean[:3]))

    doc = "\n\n".join(parts).strip()
    return doc if doc else None


def infer_metadata(dataset_key: str) -> Dict[str, str]:
    dk = dataset_key.lower()
    if "eurlex" in dk:
        return dict(department="Compliance", document_type="law", category="Regulation", region="EU")
    if "policyqa" in dk:
        return dict(department="HR", document_type="policy", category="Policy", region="Unknown")
    # pile-of-law & multi legal pile -> compliance/law
    return dict(department="Compliance", document_type="law", category="Regulation", region="Unknown")


def load_subset(dataset_name: str, subset: Optional[str], split: str, percent: float, trust_remote_code: bool = False, force_select: bool = False):

    if force_select:
        ds_full = load_dataset(dataset_name, subset, split=split, trust_remote_code=trust_remote_code)
        n = max(1, int(len(ds_full) * percent))
        return ds_full.shuffle(seed=42).select(range(n))

    pct_str = f"{percent*100:g}%"
    split_expr = f"{split}[:{pct_str}]"
    try:
        return load_dataset(dataset_name, subset, split=split_expr, trust_remote_code=trust_remote_code)
    except Exception:
        ds_full = load_dataset(dataset_name, subset, split=split, trust_remote_code=trust_remote_code)
        n = max(1, int(len(ds_full) * percent))
        return ds_full.shuffle(seed=42).select(range(n))






def ingest_one_dataset(
    dataset_key: str,
    dataset_name: str,
    subset: Optional[str],
    split: str,
    percent: float,
    out_folder: str,
    limit: Optional[int] = None,
) -> Tuple[int, int, str]:
    """
    Retourne (written, skipped, out_dir)
    """
    ensure_dir(RAW_DIR)
    out_dir = os.path.join(RAW_DIR, out_folder)
    ensure_dir(out_dir)

    logger.info(f"[{dataset_key}] Loading {dataset_name} subset={subset} split={split} percent={percent}")
    trust = dataset_key.lower() in ["pile_of_law", "multi_legal_pile"]
    force_select = dataset_key.lower() in ["multi_legal_pile"]  
    ds = load_subset(dataset_name, subset, split, percent, trust_remote_code=trust, force_select=force_select)



    if limit is not None:
        ds = ds.select(range(min(limit, len(ds))))
    else:
        if dataset_key.lower() == "multi_legal_pile":
            ds = ds.select(range(min(200, len(ds))))


    base_md = infer_metadata(dataset_key)
    now = datetime.utcnow().isoformat()

    written, skipped = 0, 0
    rows = []


    for i, ex in enumerate(tqdm(ds, desc=f"Ingest {dataset_key} -> {out_folder}")):
        try:
            if dataset_key.lower() == "policyqa":
                text = build_policyqa_text(ex)
            else:
                text = extract_text_generic(ex)
            if not text:
                skipped += 1
                continue

            doc_id = f"{safe_name(out_folder)}_{i:07d}"
            file_name = f"{doc_id}.txt"
            rel_path = os.path.join(out_folder, file_name).replace("\\", "/")
            abs_path = os.path.join(out_dir, file_name)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(text)

            md_row = {
                "doc_id": doc_id,
                "file_name": rel_path,
                "dataset_name": dataset_name,
                "subset": subset or "",
                "split": split,
                "subset_percent": percent,
                "department": base_md["department"],
                "document_type": base_md["document_type"],
                "category": base_md["category"],
                "region": base_md["region"],
                "year": "unknown",
                "source": f"huggingface:{dataset_name}",
                "created_at": now,
            }
            rows.append(md_row)

            written += 1

        except Exception as e:
            skipped += 1
            logger.exception(f"Row {i} failed: {e}")
    ensure_metadata_header()
    with open(METADATA_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METADATA_FIELDS)
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in METADATA_FIELDS})

    logger.info(f"[{dataset_key}] Done. written={written}, skipped={skipped}, out_dir={out_dir}")
    return written, skipped, out_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent", type=float, default=0.01, help="Subset percent (0.005=0.5%, 0.01=1%)")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for quick testing")
    args = parser.parse_args()

    start = time.time()
    percent_map = {
    "pile_of_law": args.percent,      
    "eurlex": args.percent,           
    "policyqa": args.percent,        
    "multi_legal_pile": min(args.percent, 0.0005),  
}


    datasets_plan = [
    ("pile_of_law", "pile-of-law/pile-of-law", "cfr", "train", "pile_of_law"),
    ("multi_legal_pile", "joelniklaus/Multi_Legal_Pile", "en_legislation", "train", "multi_legal_pile"),
    ("eurlex", "lex_glue", "eurlex", "train", "eurlex"),
    ("policyqa", "alzoubi36/policy_qa", None, "train", "policyqa"),
]


    totals = []
    for dataset_key, dataset_name, subset, split, out_folder in datasets_plan:
        try:
            p = percent_map[dataset_key]
            written, skipped, out_dir = ingest_one_dataset(
                dataset_key=dataset_key,
                dataset_name=dataset_name,
                subset=subset,
                split=split,
                out_folder=out_folder,
                limit=args.limit,
                percent=p
            )
            totals.append(
                {
                    "dataset_key": dataset_key,
                    "dataset_name": dataset_name,
                    "subset": subset,
                    "split": split,
                    "percent": p,
                    "written": written,
                    "skipped": skipped,
                    "out_dir": out_dir.replace("\\", "/"),
                }
            )
        except Exception as e:
            logger.exception(f"Dataset {dataset_key} failed: {e}")

    elapsed = time.time() - start
    raw_size = sizeof_dir_bytes(RAW_DIR)

    report = {
        "percent": args.percent,
        "limit": args.limit,
        "elapsed_seconds": round(elapsed, 2),
        "raw_dir_size_bytes": raw_size,
        "raw_dir_size_mb": round(raw_size / (1024 * 1024), 2),
        "datasets": totals,
    }

    ensure_dir(os.path.dirname(REPORT_PATH))
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Saved report -> {REPORT_PATH} | raw_size_mb={report['raw_dir_size_mb']} elapsed={report['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
