from typing import List, Optional
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = SentenceTransformer(_MODEL_NAME)

def embedding_dim() -> int:
    return _model.get_sentence_embedding_dimension()

def embed_texts(
    texts: List[str],
    batch_size: int = 32,
    show_progress: bool = False,
    normalize: bool = True,
) -> List[List[float]]:
    vectors = _model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=normalize,
    )
    return vectors.tolist()

def embed_text(text: str) -> List[float]:
    return embed_texts([text], show_progress=False)[0]
