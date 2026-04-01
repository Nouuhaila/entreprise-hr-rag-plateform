import json
import time
from pathlib import Path
from rag_pipeline.rag_orchestrator import rag_query

def has_citation(answer: str) -> bool:
    return "[" in answer and "]" in answer

def main():
    qpath = Path("rag_pipeline/evaluation/queries_week4.jsonl")
    outpath = Path("rag_pipeline/evaluation/report_week4.md")

    if not qpath.exists():
        raise FileNotFoundError(f"Missing {qpath}. Create it with one JSON per line.")

    queries = [
        json.loads(l)
        for l in qpath.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]

    rows = []
    total_latencies = []
    pipeline_latencies = []
    citation_hits = 0

    for q in queries:
        question = q["question"]
        filters = q.get("filters")
        top_k = int(q.get("top_k", 5))

        try:
            t0 = time.perf_counter()
            res = rag_query(question, top_k=top_k, filters=filters)
            total_ms = (time.perf_counter() - t0) * 1000.0

            pipeline_ms = float(res.get("latency_ms", 0.0))
            answer = res.get("answer", "") or ""
            sources = res.get("sources", []) or []

            answer_preview = " ".join(answer.split())[:400]

            top_sources = [
                {
                    "chunk_id": s.get("chunk_id"),
                    "doc_id": s.get("doc_id"),
                    "score": round(float(s.get("score", 0.0)), 4),
                }
                for s in sources[:3]
            ]

            cit = has_citation(answer)
            if cit:
                citation_hits += 1

            rows.append({
                "question": question,
                "filters": filters or {},
                "top_k": top_k,
                "total_ms": total_ms,
                "pipeline_ms": pipeline_ms,
                "citations": cit,
                "n_sources": len(sources),
                "answer_preview": answer_preview,
                "top_sources": top_sources,
            })

            total_latencies.append(total_ms)
            pipeline_latencies.append(pipeline_ms)

        except Exception as e:
            rows.append({
                "question": question,
                "filters": filters or {},
                "top_k": top_k,
                "error": str(e),
            })

    def avg(xs):
        return sum(xs) / len(xs) if xs else 0.0

    def p95(xs):
        if not xs:
            return 0.0
        xs_sorted = sorted(xs)
        idx = max(0, int(0.95 * (len(xs_sorted) - 1)))
        return xs_sorted[idx]

    md = []
    md.append("# Week 4 RAG Evaluation Report\n\n")
    md.append(f"- Queries: **{len(queries)}**\n")
    md.append(f"- Citation rate: **{(citation_hits / len(queries)) if queries else 0:.2f}**\n\n")

    md.append("## Latency\n")
    md.append(f"- End-to-end avg: **{avg(total_latencies):.2f} ms**\n")
    md.append(f"- End-to-end p95: **{p95(total_latencies):.2f} ms**\n")
    md.append(f"- Pipeline avg (reported): **{avg(pipeline_latencies):.2f} ms**\n")
    md.append(f"- Pipeline p95 (reported): **{p95(pipeline_latencies):.2f} ms**\n\n")

    md.append("## Checks\n")
    md.append("- Citation presence is checked heuristically (answer contains `[chunk_id]`).\n\n")

    md.append("## Results\n")
    md.append("| Question | Filters | Top-K | Total (ms) | Pipeline (ms) | Citations? | #Sources | Status |\n")
    md.append("|---|---|---:|---:|---:|:---:|---:|---|\n")

    for r in rows:
        if "error" in r:
            md.append(f"| {r['question']} | {r['filters']} | {r['top_k']} | - | - |  | - | ERROR: {r['error']} |\n")
        else:
            md.append(
                f"| {r['question']} | {r['filters']} | {r['top_k']} "
                f"| {r['total_ms']:.2f} | {r['pipeline_ms']:.2f} | "
                f"{'✅' if r['citations'] else '❌'} | {r['n_sources']} | OK |\n"
            )

    md.append("\n## Answers (preview)\n")
    for r in rows:
        if "error" in r:
            continue
        md.append(f"\n### {r['question']}\n")
        md.append(f"- Filters: `{r['filters']}` | Top-K: `{r['top_k']}`\n")
        md.append(f"- Answer: {r.get('answer_preview', '')}\n")
        md.append(f"- Top sources: `{r.get('top_sources', [])}`\n")

    outpath.write_text("".join(md), encoding="utf-8")
    print(f"Wrote {outpath}")

if __name__ == "__main__":
    main()
