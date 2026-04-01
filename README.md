# HR Compliance RAG Platform

Production-ready Retrieval-Augmented Generation (RAG) system for HR and Compliance document intelligence. Built over 5 weeks, it covers the full lifecycle of an AI system: data engineering, retrieval infrastructure, LLM integration, application layer, and system evaluation.

---

## Why RAG?

Fine-tuning permanently modifies model weights and is expensive to retrain when documents change. HR & Compliance systems require frequently updated policies, regulatory changes reflected instantly, and transparent filterable retrieval.

RAG keeps the model frozen and retrieves relevant documents dynamically at query time:
- No retraining required
- Real-time knowledge updates
- Metadata-based filtered retrieval
- Lower cost than fine-tuning

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit UI (:8501)                       │
│               ui/streamlit_app.py                            │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP POST /query
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              FastAPI REST API (:8000)                         │
│              api/fastapi_app.py                              │
│         In-memory cache (TTL=300s, max 100 entries)          │
└──────────────────────────┬───────────────────────────────────┘
                           │ rag_query()
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              RAG Orchestrator                                 │
│         rag_pipeline/rag_orchestrator.py                     │
│  1. Retrieve top-K chunks from Qdrant                        │
│  2. Score threshold check (< 0.25 → skip LLM)               │
│  3. [Optional] Cross-encoder re-ranking                      │
│  4. Build prompt with context chunks                         │
│  5. Call LLM → grounded answer with citations                │
└──────────┬────────────────────────────────┬──────────────────┘
           │                                │
           ▼                                ▼
┌──────────────────┐              ┌─────────────────────┐
│   Qdrant (:6333) │              │    Groq API          │
│   hr_chunks      │              │  llama-3.1-8b-instant│
│   384-dim cosine │              │  temperature=0.2     │
└──────────────────┘              └─────────────────────┘
           ▲
           │ (build-time)
┌──────────┴───────────────────────────────────────────────────┐
│              Ingestion Pipeline                               │
│  HuggingFace Datasets → chunk → embed → index into Qdrant    │
└──────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
hr-compliance-rag/
│
├── data/
│   ├── raw/                     # HuggingFace downloaded text files
│   ├── chunks/                  # Sliding-window text chunks
│   ├── processed/               # Validation reports
│   ├── metadata.csv             # Document-level metadata
│   └── chunks_metadata.csv      # Chunk-level metadata
│
├── ingestion/
│   ├── loaders.py               # Load & save HuggingFace datasets
│   ├── chunker.py               # Sliding-window chunking
│   └── validator.py             # Data quality checks
│
├── vectorstore/
│   ├── embedding_generator.py   # SentenceTransformers (all-MiniLM-L6-v2)
│   ├── qdrant_setup.py          # Create Qdrant collection
│   ├── index_builder.py         # Batch embed + upsert to Qdrant
│   ├── metadata_filter.py       # Build Qdrant filter objects
│   ├── retriever.py             # Semantic search with filters
│   ├── reranker.py              # Cross-encoder re-ranking (Week 5)
│   ├── evaluation.py            # Precision@K, Recall@K, MRR@K
│   └── reset_collection.py      # Clean rebuild utility
│
├── rag_pipeline/
│   ├── rag_orchestrator.py      # Main RAG pipeline function
│   ├── prompt_engineering.py    # System & user prompt builders
│   ├── llm_integration.py       # LLM provider abstraction
│   ├── configs/
│   │   └── settings.py          # All config via env vars
│   └── evaluation/
│       ├── queries_week3.jsonl
│       ├── queries_week4.jsonl
│       ├── queries_week5.jsonl  
│       ├── run_eval.py
│       ├── run_eval_week4.py
│       └── run_eval_week5.py    # Enhanced: token count, categories
│
├── api/
│   └── fastapi_app.py           # REST API with cache & metrics
│
├── ui/
│   └── streamlit_app.py         # Web interface
│
├── deployment/
│   ├── Dockerfile
│   └── docker-compose.yml       # qdrant + api + ui services
│
├── evaluation/                  # Week 2 retrieval evaluation
│   ├── queries.jsonl
│   └── report.md
│
├── docs/
│   └── architecture.md          # Full architecture documentation
│
├── qdrant_storage/              # Persistent vector index (gitignored)
├── .env                         # Secrets (gitignored)
└── requirements.txt
```

---

## Datasets

All datasets loaded programmatically from HuggingFace (`datasets` library):

| Dataset | Subset | Department | Type | Region |
|---------|--------|-----------|------|--------|
| `pile-of-law/pile-of-law` | `cfr` | Compliance | Law | Global |
| `lex_glue` | `eurlex` | Compliance | Law | EU |
| `alzoubi36/policy_qa` | — | HR | Policy | 
| `joelniklaus/Multi_Legal_Pile` | `en_legislation` | Compliance | Law | 

---

## Metadata Schema

### Document-level (`data/metadata.csv`)

| Field | Description |
|-------|-------------|
| `doc_id` | Unique document ID |
| `file_name` | Relative path under `data/raw/` |
| `dataset_name` | HuggingFace dataset ID |
| `subset` | HF config/subset |
| `split` | Dataset split (train/test) |
| `subset_percent` | Loaded subset fraction |
| `department` | HR / Compliance |
| `document_type` | law / policy / handbook / SOP |
| `category` | Compliance / Policy / Regulation |
| `region` | EU / Global / Unknown |
| `year` | Document year or `unknown` |
| `source` | e.g. `huggingface:<dataset>` |
| `created_at` | ISO timestamp |

### Chunk-level (`data/chunks_metadata.csv`)

Inherits all document metadata plus:
- `chunk_id`, `chunk_index`, `chunk_file`

---

## Chunking Strategy

- **Chunk size:** 3500 characters (~800–1200 tokens)
- **Overlap:** 400 characters (preserves cross-boundary context)
- **Implementation:** `ingestion/chunker.py`

---

## Embedding & Vector Store

- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
- **Normalization:** Enabled
- **Similarity:** Cosine
- **Database:** Qdrant (persistent local storage)
- **Batch size:** 64 points per upsert

Each Qdrant point stores the full chunk text + all metadata as payload.

**Supported metadata filters:** `department`, `category`, `document_type`, `region`, `dataset_name`, `created_at` (range)

---

## RAG Pipeline (Week 3–5)

### Query flow

```
question + filters
  → retrieve (top_k × 3 if reranking, else top_k)
  → score threshold check (< 0.25 → early "I don't know")
  → [optional] cross-encoder rerank → top_k
  → build_user_prompt(question, chunks)
  → LLM generate(system_prompt, user_prompt)
  → return {answer, sources, latency_ms}
```

### LLM Configuration

- **Provider:** Groq (`LLM_PROVIDER=groq`)
- **Model:** `llama-3.1-8b-instant` (configurable via `GROQ_MODEL`)
- **Temperature:** 0.2

### Advanced Features (Week 5)

| Feature | Description | Env var |
|---------|-------------|---------|
| Score threshold | Skip LLM if best score < threshold | `SCORE_THRESHOLD=0.25` |
| Cross-encoder re-ranking | Re-rank with `ms-marco-MiniLM-L-6-v2` | `ENABLE_RERANKING=true` |

---

## REST API (Week 4)

**Base URL:** `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/query` | Submit a RAG query |
| GET | `/cache/stats` | Cache statistics |
| DELETE | `/cache` | Clear cache |
| GET | `/metrics` | Request counters |

### Example request

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are compliance obligations?",
    "top_k": 5,
    "filters": {"department": "Compliance"}
  }'
```

### Example response

```json
{
  "question": "What are compliance obligations?",
  "answer": "Compliance obligations include... [chunk_id]",
  "sources": [
    {"chunk_id": "...", "doc_id": "...", "score": 0.82, "department": "Compliance"}
  ],
  "filters": {"department": "Compliance"},
  "top_k": 5,
  "latency_ms": 1243.5
}
```

---

## Configuration

All settings loaded from `.env` via `rag_pipeline/configs/settings.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `groq` | LLM provider |
| `GROQ_API_KEY` | — | **Required** |
| `GROQ_MODEL` | `llama-3.1-70b-versatile` | Groq model |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant URL |
| `QDRANT_COLLECTION` | `hr_chunks` | Collection name |
| `TOP_K_DEFAULT` | `5` | Default retrieval count |
| `MAX_CONTEXT_CHARS` | `12000` | Max context sent to LLM |
| `TEMPERATURE` | `0.2` | LLM temperature |
| `SCORE_THRESHOLD` | `0.25` | Min score to trigger LLM |
| `ENABLE_RERANKING` | `false` | Enable cross-encoder |
| `CACHE_TTL_SECONDS` | `300` | API cache TTL |
| `CACHE_MAX_SIZE` | `100` | API cache max entries |

---

## Setup & Run

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file at the project root:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=hr_chunks
TOP_K_DEFAULT=5
TEMPERATURE=0.2
MAX_CONTEXT_CHARS=8000
SCORE_THRESHOLD=0.25
ENABLE_RERANKING=false
```

### 3. Build the data pipeline 

```bash
# Download & ingest datasets
python -m ingestion.loaders --percent 0.01

# Chunk documents
python -m ingestion.chunker

# Validate chunks
python -m ingestion.validator

# Setup Qdrant collection
python -m vectorstore.qdrant_setup

# Build vector index
python -m vectorstore.index_builder

# Test retrieval
python -m vectorstore.retriever

# Run retrieval evaluation 
python -m vectorstore.evaluation
```

### 4. Run the application 

```bash
# Start Qdrant
docker run -p 6333:6333 -v ./qdrant_storage:/qdrant/storage qdrant/qdrant

# Start FastAPI (terminal 1)
uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000

# Start Streamlit UI (terminal 2)
streamlit run ui/streamlit_app.py
```

### 5. Docker Compose (all services)

```bash
docker compose -f deployment/docker-compose.yml up --build
```

Services: `qdrant` (:6333), `api` (:8000), `ui` (:8501)

### 6. Run evaluations 

```bash
# evaluation (15 queries, 5 categories, token counting)
python -m rag_pipeline.evaluation.run_eval_week5

# Week 4 evaluation
python -m rag_pipeline.evaluation.run_eval_week4
```

---

## Evaluation Baselines

| Week | Queries | Citation Rate | Avg Latency | Notes |
|------|---------|--------------|-------------|-------|
| Week 2 | 10 | — | 101 ms | Retrieval: Precision@5=0.20, Recall@5=1.0 |
| Week 3 | 3 | 0.67 | 1430 ms | RAG pipeline baseline |
| Week 4 | 7 | 0.43 | 3674 ms | Extended queries (latency_ms was broken) |
| Week 5 | 15 | TBD | TBD | Score threshold + re-ranking + improved prompt |

Full reports in `rag_pipeline/evaluation/` and `evaluation/`.

---

