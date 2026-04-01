# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (required for some sentence-transformers C extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY api/          api/
COPY rag_pipeline/ rag_pipeline/
COPY vectorstore/  vectorstore/
COPY ingestion/    ingestion/
COPY ui/           ui/

EXPOSE 8000
EXPOSE 8501

# CMD is overridden per service in docker-compose.yml
