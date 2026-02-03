# ADR-003: Embedding Models

## Status

Accepted

## Context

Embeddings power semantic search, similarity detection, and clustering. We need:
- Local execution (no API keys, works offline)
- Apple Silicon optimization (M5 MacBook Pro, 32GB RAM, NPU available)
- Model flexibility (swap models without changing infrastructure)
- Reasonable performance for 1000s of documents

## Decision

**BYOV architecture** with **Ollama** as the primary embedding provider, **sentence-transformers** as fallback.

### Primary: Ollama

```bash
# Install
brew install ollama

# Pull embedding model
ollama pull nomic-embed-text    # 768 dims, good quality
ollama pull mxbai-embed-large   # 1024 dims, higher quality
ollama pull all-minilm          # 384 dims, fastest
```

```python
import ollama

def embed(text: str, model: str = 'nomic-embed-text') -> list[float]:
    response = ollama.embeddings(model=model, prompt=text)
    return response['embedding']
```

### Fallback: sentence-transformers

```python
from sentence_transformers import SentenceTransformer

# Uses MPS (Metal) backend on Apple Silicon
model = SentenceTransformer('all-MiniLM-L6-v2', device='mps')
embeddings = model.encode(texts, convert_to_numpy=True)
```

### Model Selection Guide

| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| `all-minilm` | 384 | Fastest | Good | Development, iteration |
| `nomic-embed-text` | 768 | Fast | Better | Production default |
| `mxbai-embed-large` | 1024 | Medium | Best | High-stakes similarity |
| `snowflake-arctic-embed` | 1024 | Medium | Best | Code-heavy content |

### Rationale

1. **Ollama**: Native Apple Silicon, simple API, model management built-in
2. **sentence-transformers**: Battle-tested, MPS support, wider model selection
3. **Both local**: No API keys, no network dependency, no usage costs
4. **Model swapping**: Store `model_name` in `embedding_meta`, re-embed on model change

### Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| OpenAI API | Requires internet, costs money, privacy concerns |
| llama.cpp | Lower-level, more setup than Ollama |
| MLX | Apple-only, smaller model ecosystem |

## Consequences

- Ollama must be running for embedding generation (`ollama serve`)
- Model dimension must match schema declaration
- Re-embedding required when switching models
- Can store multiple embeddings per chunk (different models) for A/B testing

## References

- [Ollama Embedding Models](https://ollama.com/search?c=embedding)
- [sentence-transformers](https://www.sbert.net/)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
