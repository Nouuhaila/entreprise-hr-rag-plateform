# HR Compliance RAG Pipeline

Production-ready Retrieval-Augmented Generation (RAG) pipeline for HR and Compliance document intelligence.

------------------------------------------------------------------------

##  Project Overview

This project implements a scalable, production-oriented RAG (Retrieval-Augmented Generation) system designed for HR and compliance document processing.

It includes:

-   Programmatic dataset ingestion (HuggingFace)
-   Metadata-enriched document processing
-   Chunking strategy with overlap
-   Embedding generation (SentenceTransformers)
-   Vector indexing with Qdrant
-   Filtered semantic retrieval

------------------------------------------------------------------------

##  Why RAG Instead of Fine-Tuning?

Fine-tuning permanently modifies model weights and is expensive to
retrain when documents change.

HR & Compliance systems require:

-   Frequently updated policies
-   Regulatory changes reflected instantly
-   Multi-GB document corpora
-   Transparent and filterable retrieval

RAG keeps the model frozen and retrieves relevant documents dynamically at query time.

Benefits:

-   Lower cost
-   Real-time knowledge updates
-   Better scalability
-   Metadata-based filtered retrieval
-   No model retraining required

------------------------------------------------------------------------

# Production RAG Architecture

HuggingFace Dataset\
→ Ingestion (`loaders.py`)\
→ Metadata Attachment (`metadata.csv`)\
→ Chunking (`chunker.py`)\
→ Validation (`validator.py`)\
→ Embeddings (`vectorstore/embedding_generator.py`)
→ Vector Indexing (`vectorstore/index_builder.py`)
→ Metadata Filtering (`vectorstore/metadata_filter.py`)
→ Semantic Retrieval (`vectorstore/retriever.py`)
→ Retrieval Evaluation (`vectorstore/evaluation.py`)

Retrieval Quality \> Model Size
------------------------------------------------------------------------

##  Handling Large Unstructured Datasets (2--3GB)

The system is designed to scale:

-   Controlled subset loading for testing
-   Batch embedding generation
-   Overlapping chunk strategy
-   Modular ingestion pipeline
-   Vector database persistence
-   Memory-safe processing

Even when tested with small subsets, the architecture supports multi-GB corpora.

-----------------------------------------------------------------------
## Dataset Strategy

All datasets are sourced **programmatically** using the Hugging Face `datasets` library.

This ensures:
- reproducibility (one-line dataset load)
- stable versions
- scalable ingestion design
- subset scaling (0.2%, 0.5%, 1%, 2–5%…)

### Datasets used

- **pile-of-law/pile-of-law** (subset: `cfr`)  
- **lex_glue** (config: `eurlex`)  
- **alzoubi36/policy_qa**  
-  **joelniklaus/Multi_Legal_Pile** (`en_legislation`)

---
## Metadata Schema (Document-level)

`data/metadata.csv` (no header — column order is enforced in code):

| field | meaning |
|------|---------|
| doc_id | unique document id |
| file_name | relative path under `data/raw/` |
| dataset_name | HF dataset id |
| subset | HF config/subset |
| split | dataset split |
| subset_percent | used subset percent |
| department | HR / Compliance |
| document_type | Policy / Law / Handbook / SOP / etc. |
| category | Compliance / Policy / Regulation / etc. |
| region | EU / Global / etc. |
| year | if unknown → `unknown` |
| source | e.g. `huggingface:<dataset>` |
| created_at | ISO timestamp |

### Chunk-level metadata

`data/chunks_metadata.csv` **includes a header** and each chunk inherits parent metadata:

- `chunk_id`, `doc_id`, `chunk_index`
- `chunk_file`
- `dataset_name`, `subset`, `split`
- `department`, `document_type`, `category`, `region`
- `created_at`

This enables filtered retrieval such as:

-   department="HR"
-   region="EU"
-   document_type="policy"

---

## Chunking Strategy

Implemented in `ingestion/chunker.py`.

- `CHUNK_SIZE_CHARS = 3500`
- `CHUNK_OVERLAP_CHARS = 400`

This approximates ~800–1200 tokens depending on text density and preserves continuity across boundaries.

# Data Validation

Implemented validation checks:

-   Empty chunk detection
-   Missing file handling
-   Metadata completeness enforcement
-   Controlled dataset slicing
-   Batch-safe indexing

Validation ensures ingestion stability and production-readiness.

------------------------------------------------------------------------

# Repository Structure

hr-compliance-rag/
│
├── data/
│ ├── raw/ 
│ ├── processed/ 
│ ├── metadata.csv
│ └── chunks_metadata.csv
│
├── ingestion/
│ ├── loaders.py
│ ├── chunker.py
│ └── validator.py 
│
├── vectorstore/
│ ├── embedding_generator.py 
│ ├── qdrant_setup.py 
│ ├── index_builder.py 
│ ├── metadata_filter.py
│ ├── retriever.py 
│ ├── evaluation.py
│ └── reset_collection.py 
│
├── notebooks/
│
├── api/ 
│
├── evaluation/
│ ├── queries.jsonl 
│ └── report.md
│
├── README.md 
└── requirements.txt
------------------------------------------------------------------------

##  Vector Database Preparation

-   Normalized embeddings
-   Cosine similarity metric
-   Batch upserts
-   Metadata payload indexing
-   Persistent Qdrant storage

------------------------------------------------------------------------
## Embedding Model

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding dimension: **384**
- Normalized embeddings: **Enabled**
- Similarity metric: **Cosine**
- Batch processing supported (32–64 texts per batch)

Model selected for:
- Strong semantic understanding
- Lightweight architecture
- High throughput
- Low latency in production environments

------------------------------------------------------------------------

## Vector Database Configuration

- Engine: **Qdrant**
- Distance metric: **Cosine**
- Persistent local storage
- Batch upserts (64 points per batch)
- Stable deterministic chunk IDs
- Metadata payload indexing

Each stored chunk includes:

- Chunk ID
- Parent document ID
- Full metadata fields
- Original text
- Timestamp (`created_at`)

This enables precise and filtered semantic retrieval.

------------------------------------------------------------------------

## Semantic Retrieval Pipeline

Retrieval workflow:

1. Query text → embedding generation
2. Optional metadata filter construction
3. Top-K similarity search in Qdrant
4. Ranked chunk return with metadata payload
5. Context ready for LLM integration (Week 3)

Supported metadata filters:

- `department`
- `category`
- `document_type`
- `region`
- `dataset_name`
- `created_at` (range filtering)

------------------------------------------------------------------------

## Retrieval Evaluation (Week 2 Validation)

Evaluation performed on structured test queries.

### Quality Metrics

| Precision@5 
| Recall@5     
| MRR@5        

### Performance Metrics

| Avg Latency            
| P95 Latency            
| Embedding Throughput  

Full evaluation report available at:

`evaluation/report.md`

------------------------------------------------------------------------
## Scalability Considerations

- Designed for multi-GB document corpora
- Memory-safe ingestion pipeline
- Batch embedding generation
- Persistent vector indexing
- Metadata-driven compliance filtering
- Production-ready modular design

Retrieval quality is prioritized over model size.

##  Setup & Run
### Create Environment

python -m venv .venv .venv`\Scripts`{=tex}`\activate`{=tex} 
pip install -r requirements.txt

# 1. Ingestion
python -m ingestion.loaders --percent 0.01

# 2. Chunking
python -m ingestion.chunker

# 3. Validation
python -m ingestion.validator

# 4. Setup Qdrant
python -m vectorstore.qdrant_setup

# 5. Indexing
python -m vectorstore.index_builder

# 6. Test retrieval
python -m vectorstore.retriever

# 7. Run evaluation (Week 2)
python -m vectorstore.evaluation

