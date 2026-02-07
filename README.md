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

##  Production RAG Architecture

### Pipeline

Raw Datasets (HuggingFace)  
→ Ingestion (`loaders.py`)  
→ Metadata Enrichment (`metadata.csv`)  
→ Chunking (`chunker.py`)  
→ Embeddings (`embeddings.py`)  
→ Vector Indexing (Qdrant)  
→ Filtered Semantic Retrieval


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

------------------------------------------------------------------------

## 🗂 Metadata Schema Design

Each document includes:

-   doc_id
-   dataset_name
-   subset
-   split
-   department
-   document_type
-   category
-   region
-   created_at

Each chunk inherits document metadata and stores:

-   chunk_id
-   doc_id
-   chunk_index
-   dataset_name
-   department
-   document_type
-   region
-   text

This enables filtered retrieval such as:

-   department="HR"
-   region="EU"
-   document_type="policy"

------------------------------------------------------------------------

##  Scalable Ingestion Pipeline

Modular design:

-   ingestion/loaders.py → dataset loading
-   ingestion/chunker.py → chunk generation
-   vectorstore/embeddings.py → embedding creation
-   vectorstore/qdrant_setup.py → collection setup
-   vectorstore/index_chunks.py → vector indexing
-   vectorstore/search_test.py → retrieval testing

Design principles:

-   Separation of concerns
-   Batch processing
-   Idempotent indexing
-   Reproducibility
-   Production-ready structure

------------------------------------------------------------------------

##  Vector Database Preparation

-   Normalized embeddings
-   Cosine similarity metric
-   Batch upserts
-   Metadata payload indexing
-   Persistent Qdrant storage

------------------------------------------------------------------------

##  Setup & Run

### 1. Create Environment

python -m venv .venv .venv`\Scripts`{=tex}`\activate`{=tex} 
pip install -r requirements.txt

### 2. Run Qdrant (Docker)

docker run -p 6333:6333 qdrant/qdrant

### 3. Create Collection

python -m vectorstore.qdrant_setup

### 4. Index Chunks

python -m vectorstore.index_chunks

### 5. Test Search

python -m vectorstore.search_test

