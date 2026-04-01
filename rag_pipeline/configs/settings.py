import os
from dotenv import load_dotenv

load_dotenv()

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "hr_chunks")

# Retrieval
TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", "5"))

# LLM provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Ollama 
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

# Prompt limits
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# Retrieval quality
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.25"))
ENABLE_RERANKING = os.getenv("ENABLE_RERANKING", "false").lower() == "true"