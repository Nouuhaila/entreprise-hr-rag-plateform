import json
import os

import requests
import streamlit as st

st.set_page_config(
    page_title="HR Compliance RAG",
    page_icon="",
    layout="wide",
)

BACKEND_DEFAULT = os.getenv("BACKEND_URL", "http://localhost:8000")

st.sidebar.title("⚙️ Configuration")

backend_url = st.sidebar.text_input("Backend URL", value=BACKEND_DEFAULT)

top_k = st.sidebar.slider("Top-K results", min_value=1, max_value=20, value=5)

st.sidebar.markdown("---")
st.sidebar.subheader("Filters (optional)")

DEPT_OPTIONS = ["", "HR", "Compliance", "Legal", "Finance", "Operations"]
CAT_OPTIONS = ["", "Policy", "Regulation", "Contract", "Guideline", "Report"]
TYPE_OPTIONS = ["", "law", "policy", "handbook", "report"]
REGION_OPTIONS = ["", "EU", "US", "Global", "Unknown"]

department = st.sidebar.selectbox("Department", DEPT_OPTIONS)
category = st.sidebar.selectbox("Category", CAT_OPTIONS)
document_type = st.sidebar.selectbox("Document Type", TYPE_OPTIONS)
region = st.sidebar.selectbox("Region", REGION_OPTIONS)

st.sidebar.markdown("---")
st.sidebar.subheader("Cache")

col1, col2 = st.sidebar.columns(2)
if col1.button("Stats"):
    try:
        r = requests.get(f"{backend_url}/cache/stats", timeout=3)
        stats = r.json()
        st.sidebar.caption(
            f"Live: {stats['live_entries']}/{stats['total_entries']} | TTL: {stats['ttl_seconds']}s"
        )
    except Exception:
        st.sidebar.warning("Cannot reach backend")

if col2.button("Clear"):
    try:
        requests.delete(f"{backend_url}/cache", timeout=3)
        st.sidebar.success("Cache cleared")
    except Exception:
        st.sidebar.error("Failed")

st.title("HR Compliance Assistant")
st.caption("Powered by Groq LLM + Qdrant vector search")

if "history" not in st.session_state:
    st.session_state.history = []

question = st.text_area(
    "Ask a compliance or HR policy question:",
    height=100,
    placeholder="e.g. What are the notice period requirements for employee termination?",
)

submitted = st.button("Ask", type="primary", disabled=not question.strip())

if submitted and question.strip():
    filters: dict = {}
    if department:
        filters["department"] = department
    if category:
        filters["category"] = category
    if document_type:
        filters["document_type"] = document_type
    if region:
        filters["region"] = region

    payload = {
        "question": question.strip(),
        "top_k": top_k,
        "filters": filters if filters else None,
    }

    with st.spinner("Querying backend..."):
        try:
            resp = requests.post(
                f"{backend_url}/query",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.ConnectionError:
            st.error(f"Cannot connect to backend at **{backend_url}**. Is FastAPI running?")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("Request timed out after 60 seconds.")
            st.stop()
        except requests.exceptions.HTTPError:
            st.error(f"Backend error {resp.status_code}: {resp.text[:300]}")
            st.stop()

    latency = result.get("latency_ms", -1)
    if latency == 0.0:
        st.info("Result served from cache")
    else:
        st.success(f"Response received in **{latency:.0f} ms**")

    st.markdown("### Answer")
    st.markdown(result["answer"])

    sources = result.get("sources", [])
    with st.expander(f"Sources ({len(sources)} documents retrieved)"):
        if sources:
            headers = ["Score", "Chunk ID", "Doc ID", "Department", "Category", "Region"]
            cols = st.columns([1, 2, 2, 2, 2, 2])
            for col, h in zip(cols, headers):
                col.markdown(f"**{h}**")
            st.divider()
            for src in sources:
                cols = st.columns([1, 2, 2, 2, 2, 2])
                cols[0].write(f"{src.get('score', 0):.3f}")
                cols[1].write(src.get("chunk_id") or "-")
                cols[2].write(src.get("doc_id") or "-")
                cols[3].write(src.get("department") or "-")
                cols[4].write(src.get("category") or "-")
                cols[5].write(src.get("region") or "-")
        else:
            st.write("No sources returned.")

    st.caption(
        f"Latency: {latency:.0f} ms | top_k: {result.get('top_k')} | "
        f"filters: {json.dumps(result.get('filters', {}))}"
    )

    st.session_state.history.insert(0, {
        "question": question.strip(),
        "answer": result["answer"],
        "latency_ms": latency,
        "n_sources": len(sources),
    })

if st.session_state.history:
    with st.expander(f"Query History ({len(st.session_state.history)} this session)"):
        for item in st.session_state.history[:10]:
            st.markdown(f"**Q:** {item['question']}")
            st.caption(
                f"Latency: {item['latency_ms']:.0f} ms | Sources: {item['n_sources']}"
            )
            st.divider()
