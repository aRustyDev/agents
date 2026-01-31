# Graphiti MCP Server - Quick Start Guide

## 🚀 Setup (One-Time)

```bash
cd /Users/arustydev/repos/configs/ai/graphiti-docker
./setup.sh
```

This will:
1. Create `.env` from template
2. Prompt you to add your `OPENAI_API_KEY`
3. Start the Docker container
4. Show you the Zed configuration to add

## ✅ Add to Zed

Open `~/.config/zed/settings.json` and add to `"context_servers"`:

```json
"graphiti": {
  "source": "custom",
  "command": "docker",
  "args": [
    "exec",
    "-i",
    "graphiti-mcp-server",
    "python",
    "-m",
    "graphiti_mcp_server"
  ]
}
```

Restart Zed.

## 📝 Usage in Zed

The Graphiti memory server will be available automatically. Use it via:

- MCP tools/prompts exposed in Zed
- Agent interactions will store/retrieve from knowledge graph
- All entities namespaced by project UUID

## 🔄 Daily Operations

### Start Server
```bash
cd /Users/arustydev/repos/configs/ai/graphiti-docker
docker compose up -d
```

### Stop Server
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f graphiti-mcp
```

### Check Status
```bash
docker ps | grep graphiti
curl http://localhost:8000/health
```

## 🗄️ Data Management

### Backup
```bash
tar -czf ~/backups/graphiti-$(date +%Y%m%d).tar.gz data/kuzu/
```

### Restore
```bash
tar -xzf ~/backups/graphiti-YYYYMMDD.tar.gz
docker compose restart
```

### Reset (Clear All Memory)
```bash
docker compose down
rm -rf data/kuzu/*
docker compose up -d
```

## 🐛 Troubleshooting

### Container won't start
```bash
docker compose logs graphiti-mcp
docker compose down
docker compose up -d
```

### Zed can't connect
1. Check container is running: `docker ps | grep graphiti`
2. Check logs: `docker compose logs`
3. Restart Zed
4. Verify settings.json syntax

### Out of memory errors
Reduce `SEMAPHORE_LIMIT` in `.env`:
```
SEMAPHORE_LIMIT=5
```
Then restart: `docker compose restart`

## 📚 See Also

- [Full README](./README.md)
- [ADR-001: Memory Architecture](../../../docs/src/ai/ADR-001.md)
- [Graphiti Docs](https://github.com/getzep/graphiti)
