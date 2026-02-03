# Project MCP Servers

This project includes several MCP servers configured in `.mcp.json` for enhanced AI-assisted development.

## Quick Start

```bash
# Install dependencies
just init

# Start Ollama for embeddings (runs on Apple Metal automatically)
ollama serve
```

## Available Servers

### crawl4ai

Web crawling and content extraction via Docker.

**Setup:**
```bash
# Option 1: Docker (recommended)
docker pull unclecode/crawl4ai:latest

# Option 2: Add via SSE transport (after starting container)
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
claude mcp add --transport sse crawl4ai http://localhost:11235/mcp/sse
```

**Tools:** `md`, `html`, `screenshot`, `pdf`, `execute_js`, `crawl`, `ask`

**Playground:** http://localhost:11235/playground

### devrag

Local RAG (Retrieval-Augmented Generation) for project documentation.

**Setup:**
```bash
# Install devrag
brew install devrag  # or pip install devrag

# Index project files (uses .claude/devrag.json config)
devrag index
```

**Config:** `.claude/devrag.json` - indexes agents, commands, skills, and docs.

**Model:** Built-in `multilingual-e5-small` (384 dims) via ONNX - no Ollama needed.

### smart-tree

Directory visualization with MCP support.

**Setup:**
```bash
brew install smart-tree
```

**Usage:** Provides tree-structured file listings to the AI.

### markdownify

Convert HTML to Markdown.

**Setup:**
```bash
# Clone and build
git clone https://github.com/zcaceres/markdownify-mcp
cd markdownify-mcp && npm install && npm run build
mkdir -p ~/.local/share/mcp/markdownify-mcp
cp -r dist ~/.local/share/mcp/markdownify-mcp/
```

### text-editor

File editing capabilities.

**Setup:** No setup needed - runs via `uvx mcp-text-editor`.

### mindmap / markmap

Generate mind maps from content.

**Setup:** No setup needed - runs via `uvx` / `npx`.

## Knowledge Graph (sqlite-vec)

The project includes a semantic knowledge graph for context components.

**Models:**
- **Embeddings:** `nomic-embed-text` (768 dims) via Ollama
- **Runs on:** Apple Metal (automatic), MPS fallback

**Commands:**
```bash
# Initialize and populate
just kg-init
just kg-ingest

# Search and explore
just kg-search "code analysis"
just kg-similar <entity-slug>
just kg-stats
```

## Apple Silicon Optimization

All embedding models run natively on Apple Metal:

| Component | Backend | Hardware |
|-----------|---------|----------|
| Ollama | llama.cpp | Metal GPU |
| sentence-transformers | PyTorch MPS | Metal GPU |
| devrag | ONNX Runtime | Apple Neural Engine |

No additional configuration required - detected automatically.
