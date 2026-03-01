import time
from typing import Optional, Dict, Any, List
from fastapi import FastAPI
from pydantic import BaseModel, Field

from rag_pipeline.rag_orchestrator import rag_query

app = FastAPI(title="HR Compliance RAG API", version="1.0")

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    t0 = time.perf_counter()
    result = rag_query(req.question, top_k=req.top_k, filters=req.filters)
    t1 = time.perf_counter()
    result["latency_ms"] = (t1 - t0) * 1000.0
    return result