# Embedding Pipeline Design

This document describes the embedding pipeline for the knowledge graph.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           File System                                        │
│  context/agents/*.md  context/skills/*/SKILL.md  .claude/rules/*.md  etc.   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         File Watcher (watchdog)                              │
│  Detects: created, modified, deleted                                         │
│  Filters: *.md, *.yaml matching known patterns                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Content Extraction                                   │
│  Markdown: mistune parser                                                    │
│  YAML frontmatter: pyyaml                                                    │
│  (Optional) Complex formats: docling                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Chunking Strategy                                    │
│  Level: file → section (## headings) → paragraph                            │
│  Preserves hierarchy via parent_chunk_id                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Embedding Generation                                    │
│  Primary: Ollama (nomic-embed-text)                                         │
│  Fallback: sentence-transformers (MPS backend)                              │
│  Batched for efficiency                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Storage (SQLite)                                     │
│  entities → chunks → embedding_meta → vec_chunks (sqlite-vec)               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Post-Processing                                           │
│  Update FTS index                                                            │
│  Invalidate similarity cache for affected entities                           │
│  Recompute similarity for nearest neighbors                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. File Watcher

See `scripts/watch-embed.py` for implementation.

**Watched paths:**
- `context/agents/*.md` → entity_type: `agent`
- `context/skills/*/SKILL.md` → entity_type: `skill`
- `context/commands/*.md` → entity_type: `command`
- `context/rules/*.md` → entity_type: `rule`
- `.claude/rules/*.md` → entity_type: `rule`
- `**/CLAUDE.md` → entity_type: `claude_md`
- `context/plugins/*/.claude-plugin/plugin.json` → entity_type: `plugin`
- `context/output-styles/*.md` → entity_type: `output_style`
- `.claude/settings.json` hooks section → entity_type: `hook`

### 2. Content Extraction

**Markdown files:** Parse frontmatter (YAML between `---`) and body separately.

**Structured files (JSON/YAML):** Extract as metadata, generate text summary for embedding.

**Complex formats (optional):** If docling is installed, use it for PDFs, DOCX, etc. in `references/` directories.

### 3. Chunking Strategy

```python
def chunk_markdown(content: str, file_path: str) -> list[Chunk]:
    chunks = []

    # Level 1: Whole file
    chunks.append(Chunk(
        level='file',
        index=0,
        text=content,
        heading=None,
        parent=None
    ))

    # Level 2: Sections (## headings)
    sections = split_by_headings(content, level=2)
    for i, (heading, section_text) in enumerate(sections):
        section_chunk = Chunk(
            level='section',
            index=i,
            text=section_text,
            heading=heading,
            parent=chunks[0]
        )
        chunks.append(section_chunk)

        # Level 3: Paragraphs within section
        paragraphs = split_paragraphs(section_text)
        for j, para in enumerate(paragraphs):
            if len(para.strip()) > 50:  # Skip tiny fragments
                chunks.append(Chunk(
                    level='paragraph',
                    index=j,
                    text=para,
                    heading=None,
                    parent=section_chunk
                ))

    return chunks
```

### 4. Embedding Generation

**Primary: Ollama**

```python
import ollama

class OllamaEmbedder:
    def __init__(self, model: str = 'nomic-embed-text'):
        self.model = model
        self.dimensions = self._get_dimensions()

    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            response = ollama.embeddings(model=self.model, prompt=text)
            embeddings.append(response['embedding'])
        return embeddings

    def _get_dimensions(self) -> int:
        # Probe model for dimension
        test = ollama.embeddings(model=self.model, prompt='test')
        return len(test['embedding'])
```

**Fallback: sentence-transformers**

```python
from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbedder:
    def __init__(self, model: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model, device='mps')
        self.dimensions = self.model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()
```

### 5. Storage

See `.data/mcp/knowledge-graph.schema.sql` for full schema.

**Key operations:**

```python
def store_embedding(conn, chunk_id: int, embedding: list[float], model: str):
    # Insert metadata
    meta_id = conn.execute("""
        INSERT INTO embedding_meta (chunk_id, model_name, dimensions, quantization)
        VALUES (?, ?, ?, 'float32')
    """, (chunk_id, model, len(embedding))).lastrowid

    # Insert vector (requires sqlite-vec loaded)
    conn.execute("""
        INSERT INTO vec_chunks (embedding_id, embedding)
        VALUES (?, ?)
    """, (meta_id, struct.pack(f'{len(embedding)}f', *embedding)))
```

### 6. Post-Processing

After embedding an entity:

1. **Update FTS:** Handled automatically by triggers
2. **Invalidate similarity cache:**
   ```sql
   DELETE FROM similarity_cache
   WHERE entity_a_id = :entity_id OR entity_b_id = :entity_id;
   ```
3. **Recompute nearest neighbors:**
   ```python
   def recompute_similarity(conn, entity_id: int, k: int = 20):
       # Get entity's file-level embedding
       embedding = get_entity_embedding(conn, entity_id)

       # Find nearest neighbors
       neighbors = conn.execute("""
           SELECT em.chunk_id, c.entity_id,
                  vec_distance_cosine(?, vc.embedding) AS distance
           FROM vec_chunks vc
           JOIN embedding_meta em ON vc.embedding_id = em.id
           JOIN chunks c ON em.chunk_id = c.id
           WHERE c.chunk_level = 'file' AND c.entity_id != ?
           ORDER BY distance
           LIMIT ?
       """, (embedding, entity_id, k)).fetchall()

       # Store in similarity cache
       for chunk_id, neighbor_id, distance in neighbors:
           conn.execute("""
               INSERT OR REPLACE INTO similarity_cache
               (entity_a_id, entity_b_id, similarity_type, score)
               VALUES (?, ?, 'semantic', ?)
           """, (entity_id, neighbor_id, 1.0 - distance))
   ```

## CLI Interface

```bash
# Ingest all context files
scripts/embed.py ingest --all

# Ingest specific type
scripts/embed.py ingest --type skill

# Re-embed with different model
scripts/embed.py ingest --all --model mxbai-embed-large --force

# Watch for changes
scripts/embed.py watch

# Check for stale embeddings
scripts/embed.py check

# Dump database
scripts/embed.py dump
```

## Model Configuration

Models are configured in `settings/embedding-models.yaml`:

```yaml
models:
  nomic-embed-text:
    provider: ollama
    dimensions: 768
    default: true

  mxbai-embed-large:
    provider: ollama
    dimensions: 1024

  all-MiniLM-L6-v2:
    provider: sentence-transformers
    dimensions: 384
    fallback: true
```

## Optional: Docling Integration

If you need to embed PDFs, Word docs, or other complex formats in `references/` directories:

```python
# Only import if installed
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

def extract_content(file_path: Path) -> str:
    if file_path.suffix == '.md':
        return file_path.read_text()

    if DOCLING_AVAILABLE and file_path.suffix in ['.pdf', '.docx', '.pptx']:
        converter = DocumentConverter()
        result = converter.convert(str(file_path))
        return result.document.export_to_markdown()

    # Fallback: skip or use basic text extraction
    return None
```

Docling adds ~500MB of dependencies. Only install if you have non-markdown reference materials.
