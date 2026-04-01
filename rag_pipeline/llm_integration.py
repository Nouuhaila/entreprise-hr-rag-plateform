from rag_pipeline.configs.settings import (
    LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL, OLLAMA_MODEL, TEMPERATURE
)


class LLMError(RuntimeError):
    pass


def generate(system_prompt: str, user_prompt: str) -> str:
    if LLM_PROVIDER != "groq":
        raise LLMError(f"LLM_PROVIDER must be 'groq' for this setup, got: {LLM_PROVIDER}")

    if not GROQ_API_KEY:
        raise LLMError("Missing GROQ_API_KEY. Put it in your .env file.")

    from langchain_groq import ChatGroq

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=TEMPERATURE,
    )

    resp = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ])
    return resp.content


def _openai_generate(system_prompt: str, user_prompt: str) -> str:
    if not OPENAI_API_KEY:
        raise LLMError("Missing OPENAI_API_KEY. Set it as an environment variable.")

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=TEMPERATURE,
    )
    return resp.choices[0].message.content


def _ollama_generate(system_prompt: str, user_prompt: str) -> str:
    import ollama
    resp = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": TEMPERATURE},
    )
    return resp["message"]["content"]
