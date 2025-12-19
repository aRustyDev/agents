# Graphiti MCP Server - Docker Setup

Global memory endpoint for AI agents using Graphiti + Kuzu temporal knowledge graph.

## Architecture

- **Graphiti MCP Server**: Knowledge graph memory with temporal awareness
- **Kuzu Database**: Embedded lightweight graph database (~100MB)
- **Transport**: Server-Sent Events (SSE) on port 8000

## Quick Start

### 1. Setup Environment

```bash
cd /Users/arustydev/repos/configs/ai/graphiti-docker
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start the Server

```bash
docker compose up -d
```

### 3. View Logs

```bash
docker compose logs -f graphiti-mcp
```

### 4. Stop the Server

```bash
docker compose down
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `MODEL_NAME` | `gpt-4o-mini` | LLM model for embeddings |
| `SEMAPHORE_LIMIT` | `10` | Concurrent LLM API calls |
| `DATABASE_TYPE` | `kuzu` | Graph database backend |
| `KUZU_DB_PATH` | `/data/kuzu` | Kuzu database storage path |
| `LOG_LEVEL` | `INFO` | Logging level |

### Data Persistence

Kuzu database is persisted in `./data/kuzu/` directory.

**Backup:**
```bash
tar -czf kuzu-backup-$(date +%Y%m%d).tar.gz data/kuzu/
```

**Restore:**
```bash
tar -xzf kuzu-backup-YYYYMMDD.tar.gz
```

## Zed Integration

Add to Zed settings (`~/.config/zed/settings.json`):

```json
{
  "context_servers": {
    "graphiti": {
      "settings": {
        "command": {
          "path": "docker",
          "args": [
            "exec",
            "-i",
            "graphiti-mcp-server",
            "python",
            "-m",
            "graphiti_mcp_server"
          ]
        }
      }
    }
  }
}
```

## Health Check

```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Check if container is running
```bash
docker ps | grep graphiti
```

### View detailed logs
```bash
docker compose logs --tail=100 graphiti-mcp
```

### Rebuild container
```bash
docker compose down
docker compose up --build -d
```

### Clear database (reset)
```bash
docker compose down
rm -rf data/kuzu/*
docker compose up -d
```

## Project UUID Namespacing

All entities are namespaced by project UUID:

```python
# Example entity creation
graphiti.add_entity(
    name="deployment-strategy",
    namespace="1E883314-E3B4-4453-BFCF-098BE37CAF79",
    attributes={"decision": "cloudflare-workers"}
)
```

See ADR-001 for memory architecture details.
