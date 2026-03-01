from typing import List, Dict, Any
from rag_pipeline.configs.settings import MAX_CONTEXT_CHARS

SYSTEM_PROMPT = """You are an HR & Compliance assistant.
You MUST answer using ONLY the provided context.
If the context does not contain the answer, respond exactly: "I don't know based on the provided documents."
Do NOT invent policies, laws, or facts.
Use clear, concise language.
Cite sources using [chunk_id] after each important claim.
"""

def _format_chunk(payload: Dict[str, Any]) -> str:
    chunk_id = payload.get("chunk_id", "unknown_chunk")
    doc_id = payload.get("doc_id", "")
    meta = {
        "doc_id": doc_id,
        "dataset_name": payload.get("dataset_name", ""),
        "department": payload.get("department", ""),
        "category": payload.get("category", ""),
        "document_type": payload.get("document_type", ""),
        "region": payload.get("region", ""),
    }
    text = (payload.get("text") or "").strip()
    return f"[{chunk_id}]\nMETA: {meta}\nTEXT:\n{text}\n"

def build_user_prompt(question: str, retrieved: List[Dict[str, Any]]) -> str:
    blocks: List[str] = []
    total = 0

    for r in retrieved:
        payload = r.get("payload", {}) or {}
        block = _format_chunk(payload)

        if total + len(block) > MAX_CONTEXT_CHARS:
            break
        blocks.append(block)
        total += len(block)

    context = "\n---\n".join(blocks)

    return f"""QUESTION:
{question}

CONTEXT:
{context}

RULES:
- Answer ONLY from CONTEXT.
- If missing info, say you don't know based on provided documents.
- Add citations like [chunk_id] after each key sentence.
- Do not mention system internals.
"""