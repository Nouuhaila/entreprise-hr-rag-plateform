import time
import logging
from typing import Dict, Any, Optional

from rag_pipeline.prompt_engineering import SYSTEM_PROMPT, build_user_prompt
from rag_pipeline.llm_integration import generate
from rag_pipeline.configs.settings import TOP_K_DEFAULT, SCORE_THRESHOLD, ENABLE_RERANKING

from vectorstore.retriever import retrieve


# Logging
logger = logging.getLogger("rag_pipeline")


def rag_query(
    question: str,
    top_k: int = TOP_K_DEFAULT,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    logger.info("RAG query started | question=%s | top_k=%s | filters=%s",
                question, top_k, filters)

    t0 = time.perf_counter()

    try:
        # Retrieval
        t_retrieval_start = time.perf_counter()

        # Fetch more candidates when reranking is enabled
        fetch_k = top_k * 3 if ENABLE_RERANKING else top_k

        retrieved = retrieve(
            question,
            top_k=fetch_k,
            filters=filters,
            with_payload=True,
        )

        retrieval_ms = (time.perf_counter() - t_retrieval_start) * 1000

        logger.info("Retrieval completed | chunks=%s | latency=%.2f ms",
                    len(retrieved), retrieval_ms)

        # Score threshold check
        if not retrieved or max(r["score"] for r in retrieved) < SCORE_THRESHOLD:
            total_ms = (time.perf_counter() - t0) * 1000
            logger.info(
                "Score below threshold (%.2f) — skipping LLM | latency=%.2f ms",
                SCORE_THRESHOLD, total_ms,
            )
            return {
                "question": question,
                "answer": "I don't know based on the provided documents.",
                "sources": [],
                "filters": filters or {},
                "top_k": top_k,
                "latency_ms": total_ms,
            }

        # Re-ranking (optional)
        if ENABLE_RERANKING and retrieved:
            from vectorstore.reranker import rerank
            t_rerank_start = time.perf_counter()
            retrieved = rerank(question, retrieved, top_k)
            rerank_ms = (time.perf_counter() - t_rerank_start) * 1000
            logger.info("Re-ranking completed | chunks=%s | latency=%.2f ms",
                        len(retrieved), rerank_ms)

        # Prompt building
        user_prompt = build_user_prompt(question, retrieved)

        # LLM generation
        t_llm_start = time.perf_counter()

        answer = generate(SYSTEM_PROMPT, user_prompt)

        llm_ms = (time.perf_counter() - t_llm_start) * 1000

        logger.info("LLM generation completed | latency=%.2f ms", llm_ms)

        # Sources extraction
        sources = []
        for r in retrieved:
            p = r.get("payload", {}) or {}

            sources.append({
                "chunk_id": p.get("chunk_id"),
                "doc_id": p.get("doc_id"),
                "score": r.get("score"),
                "dataset_name": p.get("dataset_name"),
                "department": p.get("department"),
                "category": p.get("category"),
                "document_type": p.get("document_type"),
                "region": p.get("region"),
            })

        total_ms = (time.perf_counter() - t0) * 1000

        logger.info("RAG query finished | total_latency=%.2f ms", total_ms)

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "filters": filters or {},
            "top_k": top_k,
            "latency_ms": total_ms,
        }

    except Exception as e:

        logger.exception("RAG query failed | error=%s", str(e))
        raise


if __name__ == "__main__":

    out = rag_query(
        "What are compliance obligations?",
        filters={"department": "Compliance"}
    )

    print(out["answer"])
    print("\nSOURCES:", out["sources"])
    print(f"\nLatency: {out['latency_ms']:.2f} ms")
