import os
os.environ["HF_HUB_OFFLINE"] = "1"
from sentence_transformers import SentenceTransformer
from app.core.config import settings

_model = SentenceTransformer(settings.embedding_model.replace("sentence-transformers/", ""))


def get_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Embedding ke liye empty text nahi de sakte")

    vec = _model.encode(text, normalize_embeddings=True)
    embedding = vec.tolist()

    if len(embedding) != settings.embedding_dim:
        raise ValueError(
            f"Embedding dimension mismatch: mila {len(embedding)}, "
            f"expected {settings.embedding_dim}"
        )
    return embedding


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    clean_texts = [t for t in texts if t and t.strip()]
    vecs = _model.encode(clean_texts, normalize_embeddings=True)
    return vecs.tolist()