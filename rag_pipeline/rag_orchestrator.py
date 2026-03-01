from typing import Dict, Any, Optional
from rag_pipeline.prompt_engineering import SYSTEM_PROMPT, build_user_prompt
from rag_pipeline.llm_integration import generate
from rag_pipeline.configs.settings import TOP_K_DEFAULT

from vectorstore.retriever import retrieve 


def rag_query(
    question: str,
    top_k: int = TOP_K_DEFAULT,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    #Retrieval
    retrieved = retrieve(
        question,
        top_k=top_k,
        filters=filters,
        with_payload=True,
    )

    # Prompt
    user_prompt = build_user_prompt(question, retrieved)

    # LLM generation
    answer = generate(SYSTEM_PROMPT, user_prompt)

    # Traceability output
    sources = []
    for r in retrieved:
        p = r.get("payload", {}) or {}
        sources.append({
            "chunk_id": p.get("chunk_id"),
            "doc_id": p.get("doc_id"),
            "score": r.get("score"),
            "dataset_name": p.get("dataset_name"),
            "department": p.get("department"),
            "category": p.get("category"),
            "document_type": p.get("document_type"),
            "region": p.get("region"),
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "filters": filters or {},
        "top_k": top_k,
    }

if __name__ == "__main__":
    out = rag_query("What are compliance obligations?", filters={"department": "Compliance"})
    print(out["answer"])
    print("\nSOURCES:", out["sources"])