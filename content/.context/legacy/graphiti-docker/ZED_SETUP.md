# Zed Configuration for Graphiti MCP Server

## Configuration

The Graphiti MCP server is configured to run via `docker-compose` from a global config location.

### Configuration File Location

**Docker Compose:** `/Users/arustydev/.config/mcp/graphiti.yaml`  
**Data Storage:** `/Users/arustydev/.config/mcp/graphiti-data/`

### Zed Settings

Open: `~/.config/zed/settings.json`

Add to `"context_servers"` section:

```json
"graphiti": {
  "source": "custom",
  "command": "docker-compose",
  "args": [
    "-f",
    "/Users/arustydev/.config/mcp/graphiti.yaml",
    "up",
    "-d"
  ],
  "env": {
    "OPENAI_API_KEY": "your_openai_api_key_here",
    "MODEL_NAME": "gpt-4o-mini",
    "SEMAPHORE_LIMIT": "10",
    "LOG_LEVEL": "INFO"
  }
}
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

### Complete Example

Here's what your `context_servers` section might look like:

```json
{
  "context_servers": {
    "docker-gitlab": {
      "source": "custom",
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITLAB_API_URL", "-e", "GITLAB_PERSONAL_ACCESS_TOKEN", "mcp/gitlab"],
      "env": {
        "GITLAB_API_URL": "https://gitlab.com/api/v4",
        "GITLAB_PERSONAL_ACCESS_TOKEN": "your_token"
      }
    },
    "sequentialthinking": {
      "source": "custom",
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp/sequentialthinking"]
    },
    "time": {
      "source": "custom",
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp/time"]
    },
    "graphiti": {
      "source": "custom",
      "command": "docker-compose",
      "args": ["-f", "/Users/arustydev/.config/mcp/graphiti.yaml", "up", "-d"],
      "env": {
        "OPENAI_API_KEY": "sk-proj-...",
        "MODEL_NAME": "gpt-4o-mini",
        "SEMAPHORE_LIMIT": "10",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Restart Zed

Close and reopen Zed for changes to take effect.

## Verification

### Check Container Status

```bash
docker ps | grep graphiti-mcp-server
```

Expected output:
```
CONTAINER ID   IMAGE              STATUS         PORTS                    NAMES
xxxxx          python:3.11-slim   Up 5 minutes   0.0.0.0:8000->8000/tcp   graphiti-mcp-server
```

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
docker-compose -f ~/.config/mcp/graphiti.yaml logs -f
```

## Manual Management

### Start Server
```bash
docker-compose -f ~/.config/mcp/graphiti.yaml up -d
```

### Stop Server
```bash
docker-compose -f ~/.config/mcp/graphiti.yaml down
```

### Restart Server
```bash
docker-compose -f ~/.config/mcp/graphiti.yaml restart
```

## Troubleshooting

### Zed can't find docker-compose

**Problem:** `docker-compose` command not found  
**Solution:** Install Docker Desktop or docker-compose CLI

### Container fails to start

**Problem:** Check logs  
**Solution:**
```bash
docker-compose -f ~/.config/mcp/graphiti.yaml logs
```

### Invalid OpenAI API Key

**Problem:** Authentication error  
**Solution:** Verify your API key in `~/.config/zed/settings.json` under `"graphiti" -> "env" -> "OPENAI_API_KEY"`

### Port 8000 already in use

**Problem:** Another service using port 8000  
**Solution:** Edit `/Users/arustydev/.config/mcp/graphiti.yaml` and change port mapping:
```yaml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

## Data Management

### Backup Database

```bash
tar -czf ~/backups/graphiti-$(date +%Y%m%d).tar.gz ~/.config/mcp/graphiti-data/
```

### Restore Database

```bash
tar -xzf ~/backups/graphiti-YYYYMMDD.tar.gz -C ~/.config/mcp/
docker-compose -f ~/.config/mcp/graphiti.yaml restart
```

### Clear All Memory (DANGEROUS)

```bash
docker-compose -f ~/.config/mcp/graphiti.yaml down
rm -rf ~/.config/mcp/graphiti-data/*
docker-compose -f ~/.config/mcp/graphiti.yaml up -d
```

## See Also

- [QUICKSTART.md](./QUICKSTART.md) - Fast setup guide
- [README.md](./README.md) - Complete documentation
- [ADR-001](../../blog/docs/src/ai/ADR-001.md) - Architecture decision
- [MCP Config README](~/.config/mcp/README.md) - Global MCP server configs
