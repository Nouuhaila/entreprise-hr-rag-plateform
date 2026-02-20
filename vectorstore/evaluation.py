import os, json, time, statistics
from typing import Dict, Any, List
import numpy as np

from vectorstore.retriever import retrieve
from vectorstore.embedding_generator import embed_texts

QUERIES_PATH = os.path.join("evaluation", "queries.jsonl")
REPORT_PATH = os.path.join("evaluation", "report.md")
TOP_K = 5

def load_queries(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out

def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(np.array(values), p))

def main():
    queries = load_queries(QUERIES_PATH)
    lat_ms: List[float] = []
    recalls: List[float] = []
    mrrs: List[float] = []
    precisions: List[float] = []
    dup_rates: List[float] = []

    for q in queries:
        query = q["query"]
        expected = str(q.get("expected_doc_id", "")).strip()
        filters = q.get("filters", {})

        t0 = time.perf_counter()
        results = retrieve(query, top_k=TOP_K, filters=filters, with_payload=True)
        t1 = time.perf_counter()
        lat_ms.append((t1 - t0) * 1000.0)

        doc_ids = []
        for r in results:
            did = (r.get("payload") or {}).get("doc_id", "")
            if did:
                doc_ids.append(str(did))

        if doc_ids:
            dup_rates.append(1.0 - (len(set(doc_ids)) / len(doc_ids)))

        if expected:
            topk = doc_ids[:TOP_K]
            # Recall
            recalls.append(1.0 if expected in topk else 0.0)
            # Precision
            precisions.append((1.0 / TOP_K) if expected in topk else 0.0)
            # MRR@K
            rr = 0.0
            for i, did in enumerate(topk, start=1):
                if did == expected:
                    rr = 1.0 / i
                    break
            mrrs.append(rr)

    # Embedding throughput
    sample = [q["query"] for q in queries] * 50
    t0 = time.perf_counter()
    _ = embed_texts(sample, batch_size=64, show_progress=False, normalize=True)
    t1 = time.perf_counter()
    throughput = len(sample) / max(t1 - t0, 1e-9)

    avg_lat = statistics.mean(lat_ms) if lat_ms else 0.0
    p95_lat = percentile(lat_ms, 95)

    avg_rec = statistics.mean(recalls) if recalls else 0.0
    avg_prec = statistics.mean(precisions) if precisions else 0.0
    avg_mrr = statistics.mean(mrrs) if mrrs else 0.0
    avg_dup = statistics.mean(dup_rates) if dup_rates else 0.0

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Week 2 Retrieval Evaluation Report\n\n")
        f.write(f"- Queries: **{len(queries)}**\n")
        f.write(f"- Top-K: **{TOP_K}**\n\n")
        f.write("## Metrics\n")
        f.write(f"- Precision@{TOP_K}: **{avg_prec:.4f}**\n")
        f.write(f"- Recall@{TOP_K}: **{avg_rec:.4f}**\n")
        f.write(f"- MRR@{TOP_K}: **{avg_mrr:.4f}**\n\n")
        f.write("## Performance\n")
        f.write(f"- Latency avg: **{avg_lat:.2f} ms**\n")
        f.write(f"- Latency p95: **{p95_lat:.2f} ms**\n")
        f.write(f"- Embedding throughput: **{throughput:.2f} texts/sec**\n\n")
        f.write("## Qualitative checks (proxy)\n")
        f.write(f"- Duplicate doc rate in top-{TOP_K} (avg): **{avg_dup:.4f}**\n")

    print("✅ Done.")
    print(f"Precision@{TOP_K}: {avg_prec:.4f}")
    print(f"Recall@{TOP_K}:    {avg_rec:.4f}")
    print(f"MRR@{TOP_K}:       {avg_mrr:.4f}")
    print(f"Latency avg:       {avg_lat:.2f} ms")
    print(f"Latency p95:       {p95_lat:.2f} ms")
    print(f"Emb throughput:    {throughput:.2f} texts/sec")
    print(f"Report:            {REPORT_PATH}")

if __name__ == "__main__":
    main()