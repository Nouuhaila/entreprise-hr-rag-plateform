"""
Cross-encoder re-ranking for retrieved chunks.

Uses sentence-transformers CrossEncoder (cross-encoder/ms-marco-MiniLM-L-6-v2)
to re-score query-document pairs and return the top_k most relevant chunks.

Usage:
    from vectorstore.reranker import rerank
    reranked = rerank(query, retrieved_chunks, top_k=5)

Enable via: ENABLE_RERANKING=true in .env
"""
from typing import List, Dict, Any

_cross_encoder = None
_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        from sentence_transformers import CrossEncoder
        _cross_encoder = CrossEncoder(_MODEL_NAME)
    return _cross_encoder


def rerank(query: str, results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    """Re-rank retrieved chunks using a cross-encoder.

    Args:
        query: The user's question.
        results: List of retrieval results (each with 'payload' containing 'text').
        top_k: Number of top results to return after re-ranking.

    Returns:
        Re-ranked and truncated list of results.
    """
    if not results:
        return results

    encoder = _get_cross_encoder()

    texts = [r.get("payload", {}).get("text", "") for r in results]
    pairs = [[query, t] for t in texts]

    scores = encoder.predict(pairs)

    ranked = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
    return [r for _, r in ranked[:top_k]]
