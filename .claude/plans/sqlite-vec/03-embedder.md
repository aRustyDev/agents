# Task 3: Implement embedding generation with Ollama

## Objective

Create the embedder module that generates vectors using Ollama (primary) with sentence-transformers fallback.

## Prerequisites

- Task 1 complete (sqlite-vec installed)
- Ollama installed and running (`ollama serve`)
- nomic-embed-text model pulled (`ollama pull nomic-embed-text`)

## Steps

### 3.1 Create lib directory structure

```bash
mkdir -p scripts/lib
touch scripts/lib/__init__.py
```

### 3.2 Create embedder module

Create `scripts/lib/embedder.py`:

```python
"""Embedding generation module.

Supports multiple embedding backends:
- Ollama (primary, local)
- sentence-transformers (fallback)
"""

from abc import ABC, abstractmethod
from typing import Protocol
import struct


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


def get_embedder(model: str = 'nomic-embed-text', fallback: bool = True) -> Embedder:
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
```

### 3.3 Create test script

Create `scripts/test-embedder.py`:

```python
#!/usr/bin/env python3
"""Test embedding generation."""

from lib.embedder import get_embedder, serialize_embedding

def main():
    print("Testing Ollama embedder...")
    embedder = get_embedder('nomic-embed-text')
    print(f"Model: {embedder.model_name}")
    print(f"Dimensions: {embedder.dimensions}")

    # Test single embedding
    text = "This is a test sentence about Python programming."
    embedding = embedder.embed_one(text)
    print(f"Single embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Test batch embedding
    texts = [
        "First test sentence.",
        "Second test sentence.",
        "Third test sentence."
    ]
    embeddings = embedder.embed(texts)
    print(f"Batch embeddings: {len(embeddings)} vectors")

    # Test serialization
    serialized = serialize_embedding(embedding)
    print(f"Serialized size: {len(serialized)} bytes")

    print("\n✓ Embedder working correctly")

if __name__ == '__main__':
    main()
```

### 3.4 Test embedder

```bash
# Ensure Ollama is running
ollama serve &  # If not already running

# Run test
cd scripts && uv run python test-embedder.py
```

Expected output:
```
Testing Ollama embedder...
Model: nomic-embed-text
Dimensions: 768
Single embedding length: 768
First 5 values: [0.123, -0.456, ...]
Batch embeddings: 3 vectors
Serialized size: 3072 bytes
✓ Embedder working correctly
```

## Acceptance Criteria

- [ ] `OllamaEmbedder` generates 768-dimensional vectors with nomic-embed-text
- [ ] `SentenceTransformerEmbedder` works as fallback
- [ ] `get_embedder()` auto-detects available backend
- [ ] `serialize_embedding()` produces correct byte format for sqlite-vec
- [ ] Batch embedding works for multiple texts

## Files Created

- `scripts/lib/__init__.py`
- `scripts/lib/embedder.py`
- `scripts/test-embedder.py`

## Next

→ [04-chunker.md](04-chunker.md)
