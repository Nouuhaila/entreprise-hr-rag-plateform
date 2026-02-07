from typing import List
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = SentenceTransformer(_MODEL_NAME)

def embedding_dim() -> int:
    return _model.get_sentence_embedding_dimension()

def embed_texts(texts: List[str]) -> List[List[float]]:
    # normalize_embeddings=True 
    vectors = _model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    return vectors.tolist()
def embed_text(text: str) -> List[float]:
    return embed_texts([text])[0]

