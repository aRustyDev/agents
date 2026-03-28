"""Embedding generation module.

Supports multiple embedding backends:
- Ollama (primary, local)
- sentence-transformers (fallback)
"""

import struct
from typing import Protocol


class Embedder(Protocol):
    """Protocol for embedding generators."""

    model_name: str
    dimensions: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...

    def embed_one(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        ...


class OllamaEmbedder:
    """Ollama-based embedder (primary)."""

    def __init__(self, model: str = 'nomic-embed-text'):
        import ollama
        self._client = ollama
        self.model_name = model
        self._dimensions: int | None = None

    @property
    def dimensions(self) -> int:
        if self._dimensions is None:
            # Probe model for dimensions
            test = self._client.embeddings(model=self.model_name, prompt='test')
            self._dimensions = len(test['embedding'])
        return self._dimensions

    def embed_one(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        response = self._client.embeddings(model=self.model_name, prompt=text)
        return response['embedding']

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Note: Ollama doesn't support batching, so we process sequentially.
        """
        return [self.embed_one(text) for text in texts]


class SentenceTransformerEmbedder:
    """sentence-transformers based embedder (fallback)."""

    def __init__(self, model: str = 'all-MiniLM-L6-v2', device: str = 'mps'):
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model, device=device)
        self.model_name = model

    @property
    def dimensions(self) -> int:
        return self._model.get_sentence_embedding_dimension()

    def embed_one(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        return self._model.encode(text, convert_to_numpy=True).tolist()

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (batched)."""
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


def get_embedder(model: str = 'st:all-MiniLM-L6-v2', fallback: bool = True) -> Embedder:
    """Get an embedder instance.

    Args:
        model: Model name. For Ollama models, use the Ollama model name.
               For sentence-transformers, prefix with 'st:' (e.g., 'st:all-MiniLM-L6-v2')
        fallback: If True and Ollama fails, fall back to sentence-transformers.

    Returns:
        Embedder instance.
    """
    # Check for explicit sentence-transformers prefix
    if model.startswith('st:'):
        st_model = model[3:]
        return SentenceTransformerEmbedder(model=st_model)

    # Try Ollama first
    try:
        import ollama
        # Verify model is available
        ollama.embeddings(model=model, prompt='test')
        return OllamaEmbedder(model=model)
    except Exception as e:
        if not fallback:
            raise RuntimeError(f"Ollama model '{model}' not available: {e}")

        print(f"Warning: Ollama model '{model}' not available, falling back to sentence-transformers")
        return SentenceTransformerEmbedder()


def serialize_embedding(embedding: list[float]) -> bytes:
    """Serialize embedding to bytes for sqlite-vec storage."""
    return struct.pack(f'{len(embedding)}f', *embedding)


def deserialize_embedding(data: bytes, dimensions: int) -> list[float]:
    """Deserialize embedding from bytes."""
    return list(struct.unpack(f'{dimensions}f', data))
