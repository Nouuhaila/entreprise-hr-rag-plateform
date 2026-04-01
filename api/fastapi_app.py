import hashlib
import json
import logging
import os
import threading
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from rag_pipeline.rag_orchestrator import rag_query

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("fastapi_app")

# ── In-memory cache ───────────────────────────────────────────────────────────
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))


@dataclass
class _CacheEntry:
    result: dict
    created_at: float = field(default_factory=time.time)


_cache: Dict[str, _CacheEntry] = {}
_cache_lock = threading.Lock()

# ── Metrics counters ──────────────────────────────────────────────────────────
_metrics: Dict[str, int] = {"total": 0, "cache_hits": 0, "errors": 0}


def _make_cache_key(question: str, top_k: int, filters: Optional[Dict]) -> str:
    payload = {
        "q": question.strip().lower(),
        "top_k": top_k,
        "filters": sorted((filters or {}).items()),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


# ── Request ID middleware ─────────────────────────────────────────────────────
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ── App lifecycle ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("HR Compliance RAG API starting up")
    logger.info("Cache settings: TTL=%ds MAX_SIZE=%d", CACHE_TTL_SECONDS, CACHE_MAX_SIZE)
    yield
    logger.info("HR Compliance RAG API shutting down")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="HR Compliance RAG API", version="1.0", lifespan=lifespan)
app.add_middleware(RequestIDMiddleware)


# ── Pydantic models ───────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(5, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = None


class Source(BaseModel):
    chunk_id: Optional[str] = None
    doc_id: Optional[str] = None
    score: Optional[float] = None
    dataset_name: Optional[str] = None
    department: Optional[str] = None
    category: Optional[str] = None
    document_type: Optional[str] = None
    region: Optional[str] = None


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    filters: Dict[str, Any]
    top_k: int
    latency_ms: float


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    _metrics["total"] += 1
    cache_key = _make_cache_key(req.question, req.top_k, req.filters)

    # Check cache first
    with _cache_lock:
        entry = _cache.get(cache_key)
        if entry and (time.time() - entry.created_at) < CACHE_TTL_SECONDS:
            _metrics["cache_hits"] += 1
            logger.info("Cache HIT | key=%s | question=%s", cache_key[:12], req.question[:60])
            cached = dict(entry.result)
            cached["latency_ms"] = 0.0
            return cached

    logger.info(
        "Cache MISS | question=%s | top_k=%s | filters=%s",
        req.question,
        req.top_k,
        req.filters,
    )

    t0 = time.perf_counter()
    try:
        result = rag_query(req.question, top_k=req.top_k, filters=req.filters)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        result["latency_ms"] = latency_ms

        logger.info(
            "Query OK | latency_ms=%.2f | sources=%d",
            latency_ms,
            len(result.get("sources", [])),
        )

        # Store in cache (evict oldest if at capacity)
        with _cache_lock:
            if len(_cache) >= CACHE_MAX_SIZE:
                oldest = sorted(_cache.items(), key=lambda x: x[1].created_at)
                for k, _ in oldest[: len(_cache) - CACHE_MAX_SIZE + 1]:
                    del _cache[k]
            _cache[cache_key] = _CacheEntry(result=result)

        return result

    except Exception as e:
        _metrics["errors"] += 1
        latency_ms = (time.perf_counter() - t0) * 1000.0
        logger.exception("Query FAILED | latency_ms=%.2f | error=%s", latency_ms, str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing the query.",
        )


@app.get("/cache/stats")
def cache_stats():
    with _cache_lock:
        now = time.time()
        live = sum(1 for e in _cache.values() if now - e.created_at < CACHE_TTL_SECONDS)
    return {
        "total_entries": len(_cache),
        "live_entries": live,
        "ttl_seconds": CACHE_TTL_SECONDS,
        "max_size": CACHE_MAX_SIZE,
    }


@app.delete("/cache")
def cache_clear():
    with _cache_lock:
        _cache.clear()
    logger.info("Cache cleared via API")
    return {"status": "cleared"}


@app.get("/metrics")
def metrics_endpoint():
    return {
        **_metrics,
        "cache_entries": len(_cache),
    }
