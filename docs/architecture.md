# HR Compliance RAG — System Architecture

## Overview

An end-to-end Retrieval-Augmented Generation (RAG) system for HR and compliance document intelligence. The system enables users to query a corpus of legal, policy, and compliance documents and receive grounded, cited answers from an LLM.

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                  Streamlit (ui/streamlit_app.py)                 │
└─────────────────────────────┬────────────────────────────────────┘
                              │ HTTP POST /query
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        REST API LAYER                            │
│               FastAPI (api/fastapi_app.py :8000)                 │
│           In-memory cache (TTL=300s, max 100 entries)            │
│           Metrics: /metrics  Cache: /cache/stats                 │
└─────────────────────────────┬────────────────────────────────────┘
                              │ rag_query()
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       RAG ORCHESTRATOR                           │
│            rag_pipeline/rag_orchestrator.py                      │
│                                                                  │
│  1. Retrieve top-K chunks from Qdrant                            │
│  2. Score threshold check (< 0.25 → skip LLM)                   │
│  3. [Optional] Cross-encoder re-ranking                          │
│  4. Build prompt (system + user with context)                    │
│  5. Call LLM → get answer                                        │
│  6. Return answer + sources + latency_ms                         │
└──────┬───────────────────────────────────────────────────────────┘
       │                                │
       ▼                                ▼
┌─────────────────┐           ┌──────────────────────┐
│   VECTOR STORE  │           │    LLM PROVIDER       │
│  Qdrant :6333   │           │  Groq API             │
│  hr_chunks      │           │  llama-3.1-8b-instant │
│  384-dim cosine │           │  temperature=0.2      │
└─────────────────┘           └──────────────────────┘
       ▲
       │ (build-time)
┌──────┴──────────────────────────────────────────────────────────┐
│                      INGESTION PIPELINE                          │
│                                                                  │
│  HuggingFace Datasets → chunker → embeddings → Qdrant index     │
│  Sources: pile-of-law, lex_glue, policy_qa, Multi_Legal_Pile    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Reference

### 1. Ingestion Pipeline
| File | Purpose |
|------|---------|
| `ingestion/loaders.py` | Load datasets from HuggingFace, write raw text + metadata CSV |
| `ingestion/chunker.py` | Sliding window chunking (3500 chars, 400 overlap) |
| `ingestion/validator.py` | Validate chunk metadata completeness, detect duplicates |

**Chunk strategy:** 3500 characters (~800-1200 tokens) with 400-char overlap to preserve cross-boundary context.

**Datasets:**
- `pile-of-law/cfr` → Compliance / Law / Global
- `lex_glue/eurlex` → Compliance / Law / EU
- `alzoubi36/policy_qa` → HR / Policy / 
- `joelniklaus/Multi_Legal_Pile/en_legislation` → Compliance / Law /

---

### 2. Vector Store
| File | Purpose |
|------|---------|
| `vectorstore/embedding_generator.py` | SentenceTransformers embeddings (all-MiniLM-L6-v2, 384-dim) |
| `vectorstore/qdrant_setup.py` | Create Qdrant collection with cosine distance |
| `vectorstore/index_builder.py` | Batch embed + upsert chunks to Qdrant |
| `vectorstore/retriever.py` | Semantic search with optional metadata filters |
| `vectorstore/metadata_filter.py` | Build Qdrant filters from metadata parameters |
| `vectorstore/reranker.py` | Cross-encoder re-ranking (cross-encoder/ms-marco-MiniLM-L-6-v2) |

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Similarity: Cosine
- Normalization: enabled

**Metadata filters supported:** `department`, `category`, `document_type`, `region`, `dataset_name`, `created_from/to`

---

### 3. RAG Pipeline
| File | Purpose |
|------|---------|
| `rag_pipeline/rag_orchestrator.py` | Main `rag_query()` function — orchestrates full pipeline |
| `rag_pipeline/prompt_engineering.py` | System prompt + user prompt builder with context formatting |
| `rag_pipeline/llm_integration.py` | LLM abstraction (Groq primary, OpenAI/Ollama optional) |
| `rag_pipeline/configs/settings.py` | All configuration via environment variables |

**Query flow:**
```
question + filters
    → retrieve(top_k * 3 if reranking else top_k)
    → score threshold check (< 0.25 → early return)
    → [optional] cross-encoder rerank → top_k
    → build_user_prompt(question, chunks)
    → generate(system_prompt, user_prompt)
    → return {answer, sources, latency_ms}
```

---

### 4. API Layer
| File | Purpose |
|------|---------|
| `api/fastapi_app.py` | FastAPI app with caching, metrics, request ID middleware |

**Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/query` | Submit RAG query |
| GET | `/cache/stats` | Cache statistics |
| DELETE | `/cache` | Clear cache |
| GET | `/metrics` | Request counters |

**Cache:** In-memory dict with TTL (default 300s) and max size (default 100). Cache key = SHA256 of (question, top_k, filters).

---

### 5. User Interface
| File | Purpose |
|------|---------|
| `ui/streamlit_app.py` | Streamlit web app connecting to FastAPI backend |

**Features:** Filter sidebar (department, category, document_type, region), top_k slider, answer display with inline sources table, query history, cache stats/clear controls.

---

## Configuration Reference

All settings loaded from `.env` via `rag_pipeline/configs/settings.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `groq` | LLM provider (groq only active) |
| `GROQ_API_KEY` | — | Required Groq API key |
| `GROQ_MODEL` | `llama-3.1-70b-versatile` | Groq model name |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `QDRANT_COLLECTION` | `hr_chunks` | Qdrant collection name |
| `TOP_K_DEFAULT` | `5` | Default retrieval count |
| `MAX_CONTEXT_CHARS` | `12000` | Max context characters sent to LLM |
| `TEMPERATURE` | `0.2` | LLM temperature |
| `SCORE_THRESHOLD` | `0.25` | Min similarity score to trigger LLM |
| `ENABLE_RERANKING` | `false` | Enable cross-encoder re-ranking |
| `CACHE_TTL_SECONDS` | `300` | API cache TTL |
| `CACHE_MAX_SIZE` | `100` | API cache max entries |

---

## Deployment

### Local Development
```bash
# Start Qdrant
docker run -p 6333:6333 -v ./qdrant_storage:/qdrant/storage qdrant/qdrant

# Start API
uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000

# Start UI
streamlit run ui/streamlit_app.py
```

### Docker Compose (all services)
```bash
docker compose -f deployment/docker-compose.yml up --build
```
Services: `qdrant` (:6333), `api` (:8000), `ui` (:8501)

---

## Evaluation Baselines

| Week | Queries | Citation Rate | Avg Latency | Notes |
|------|---------|--------------|-------------|-------|
| Week 2 | 10 | — | 101 ms | Retrieval only |
| Week 3 | 3 | 0.67 | 1430 ms | RAG pipeline, basic prompt |
| Week 4 | 7 | 0.43 | 3674 ms | Extended queries, latency_ms was broken (0.00) |
| Week 5 | 15 | TBD | TBD | Fixed latency, score threshold, re-ranking, improved prompt |

---

## Repository Structure

```
hr-compliance-rag/
├── data/                        # Raw docs, chunks, metadata
│   ├── raw/                     # HuggingFace downloaded text
│   ├── chunks/                  # Sliding-window chunks
│   ├── metadata.csv             # Document metadata
│   └── chunks_metadata.csv      # Chunk metadata
├── ingestion/                   # Data pipeline
│   ├── loaders.py
│   ├── chunker.py
│   └── validator.py
├── vectorstore/                 # Embedding & retrieval
│   ├── embedding_generator.py
│   ├── qdrant_setup.py
│   ├── index_builder.py
│   ├── retriever.py
│   ├── metadata_filter.py
│   └── reranker.py              
├── rag_pipeline/                # RAG orchestration
│   ├── rag_orchestrator.py
│   ├── prompt_engineering.py
│   ├── llm_integration.py
│   ├── configs/settings.py
│   └── evaluation/              # Test queries + reports
│       ├── queries_week3.jsonl
│       ├── queries_week4.jsonl
│       ├── queries_week5.jsonl
│       ├── run_eval.py
│       ├── run_eval_week4.py
│       └── run_eval_week5.py
├── api/
│   └── fastapi_app.py           # REST API + cache
├── ui/
│   └── streamlit_app.py         # Web interface
├── deployment/
│   ├── Dockerfile
│   └── docker-compose.yml
├── evaluation/                  # Week 2 retrieval eval
│   ├── queries.jsonl
│   └── report.md
├── docs/
│   └── architecture.md          # This file
├── qdrant_storage/              # Persistent vector index
├── .env                         # Secrets (gitignored)
└── requirements.txt
```
