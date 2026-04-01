"""
Week 5 Enhanced RAG Evaluation
================================
Improvements over Week 4:
  - Proper latency tracking (latency_ms now in rag_query() response)
  - Token counting per query (tiktoken, cl100k_base encoding)
  - Category-level breakdown of citation rates
  - Score threshold trigger detection (latency_ms near 0 → threshold hit)
  - Structured markdown report with baselines comparison
"""
import json
import time
from collections import defaultdict
from pathlib import Path

import tiktoken

from rag_pipeline.rag_orchestrator import rag_query

ENCODING = tiktoken.get_encoding("cl100k_base")

QPATH = Path("rag_pipeline/evaluation/queries_week5.jsonl")
OUTPATH = Path("rag_pipeline/evaluation/report_week5.md")


def has_citation(answer: str) -> bool:
    return "[" in answer and "]" in answer


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def avg(xs):
    return sum(xs) / len(xs) if xs else 0.0


def p95(xs):
    if not xs:
        return 0.0
    xs_sorted = sorted(xs)
    idx = max(0, int(0.95 * (len(xs_sorted) - 1)))
    return xs_sorted[idx]


def main():
    if not QPATH.exists():
        raise FileNotFoundError(f"Missing {QPATH}")

    queries = [
        json.loads(l)
        for l in QPATH.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]

    rows = []
    total_latencies = []
    citation_hits = 0
    threshold_hits = 0
    total_tokens = 0

    # Per-category tracking
    cat_results = defaultdict(lambda: {"total": 0, "citations": 0, "latencies": []})

    for q in queries:
        question = q["question"]
        filters = q.get("filters")
        top_k = int(q.get("top_k", 5))
        category = q.get("category", "unknown")
        q_tokens = count_tokens(question)
        total_tokens += q_tokens

        try:
            t0 = time.perf_counter()
            res = rag_query(question, top_k=top_k, filters=filters)
            wall_ms = (time.perf_counter() - t0) * 1000.0

            # latency_ms is now properly set in rag_orchestrator
            pipeline_ms = float(res.get("latency_ms", 0.0))
            answer = res.get("answer", "") or ""
            sources = res.get("sources", []) or []

            answer_preview = " ".join(answer.split())[:400]
            top_sources = [
                {
                    "chunk_id": s.get("chunk_id"),
                    "doc_id": s.get("doc_id"),
                    "score": round(float(s.get("score") or 0.0), 4),
                }
                for s in sources[:3]
            ]

            cit = has_citation(answer)
            if cit:
                citation_hits += 1

            # Detect score threshold triggers (no sources returned)
            threshold_triggered = len(sources) == 0
            if threshold_triggered:
                threshold_hits += 1

            row = {
                "question": question,
                "category": category,
                "filters": filters or {},
                "top_k": top_k,
                "wall_ms": wall_ms,
                "pipeline_ms": pipeline_ms,
                "citations": cit,
                "n_sources": len(sources),
                "threshold_triggered": threshold_triggered,
                "q_tokens": q_tokens,
                "answer_preview": answer_preview,
                "top_sources": top_sources,
            }
            rows.append(row)

            total_latencies.append(pipeline_ms)
            cat_results[category]["total"] += 1
            cat_results[category]["latencies"].append(pipeline_ms)
            if cit:
                cat_results[category]["citations"] += 1

        except Exception as e:
            rows.append({
                "question": question,
                "category": category,
                "filters": filters or {},
                "top_k": top_k,
                "error": str(e),
            })
            cat_results[category]["total"] += 1

    # ── Build markdown report ────────────────────────────────────────────────
    n = len(queries)
    citation_rate = citation_hits / n if n else 0.0

    md = []
    md.append("# Week 5 RAG Evaluation Report\n\n")
    md.append(f"- Total queries: **{n}**\n")
    md.append(f"- Citation rate: **{citation_rate:.2f}** ({citation_hits}/{n})\n")
    md.append(f"- Score threshold triggers: **{threshold_hits}** (queries answered without LLM)\n")
    md.append(f"- Total question tokens: **{total_tokens}** (~{total_tokens / n:.1f} avg/query)\n\n")

    md.append("## Latency (pipeline)\n")
    md.append(f"- Avg: **{avg(total_latencies):.2f} ms**\n")
    md.append(f"- P95: **{p95(total_latencies):.2f} ms**\n\n")

    md.append("## Baseline Comparison\n")
    md.append("| Week | Queries | Citation Rate | Avg Latency |\n")
    md.append("|------|---------|--------------|-------------|\n")
    md.append("| Week 3 | 3 | 0.67 | 1430 ms |\n")
    md.append("| Week 4 | 7 | 0.43 | 3674 ms |\n")
    md.append(f"| Week 5 | {n} | {citation_rate:.2f} | {avg(total_latencies):.0f} ms |\n\n")

    md.append("## Results by Category\n")
    md.append("| Category | Queries | Citation Rate | Avg Latency (ms) |\n")
    md.append("|----------|---------|--------------|------------------|\n")
    for cat, data in sorted(cat_results.items()):
        crate = data["citations"] / data["total"] if data["total"] else 0.0
        clat = avg(data["latencies"])
        md.append(f"| {cat} | {data['total']} | {crate:.2f} | {clat:.0f} |\n")
    md.append("\n")

    md.append("## Detailed Results\n")
    md.append("| Question | Category | Filters | Top-K | Pipeline (ms) | Citations? | #Sources | Threshold? |\n")
    md.append("|---|---|---|---:|---:|:---:|---:|:---:|\n")

    for r in rows:
        if "error" in r:
            md.append(
                f"| {r['question'][:50]} | {r['category']} | {r['filters']} | {r['top_k']} "
                f"| - | | - | - | ERROR: {r['error'][:60]} |\n"
            )
        else:
            md.append(
                f"| {r['question'][:50]} | {r['category']} | {r['filters']} | {r['top_k']} "
                f"| {r['pipeline_ms']:.0f} | {'✅' if r['citations'] else '❌'} "
                f"| {r['n_sources']} | {'⚡' if r['threshold_triggered'] else ''} |\n"
            )

    md.append("\n## Answers (preview)\n")
    for r in rows:
        if "error" in r:
            continue
        md.append(f"\n### [{r['category']}] {r['question']}\n")
        md.append(f"- Filters: `{r['filters']}` | Top-K: `{r['top_k']}` | Tokens: `{r.get('q_tokens', '?')}`\n")
        if r.get("threshold_triggered"):
            md.append("- **Score threshold triggered** — answered without LLM call\n")
        md.append(f"- Answer: {r.get('answer_preview', '')}\n")
        md.append(f"- Top sources: `{r.get('top_sources', [])}`\n")

    OUTPATH.write_text("".join(md), encoding="utf-8")
    print(f"Wrote {OUTPATH}")
    print(f"Citation rate: {citation_rate:.2f} | Avg latency: {avg(total_latencies):.0f} ms | Threshold hits: {threshold_hits}/{n}")


if __name__ == "__main__":
    main()
