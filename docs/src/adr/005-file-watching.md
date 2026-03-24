# ADR-005: File Watching and Re-embedding

## Status

Accepted

## Context

Context components (skills, rules, agents, etc.) are markdown files that change during development. When a file changes:
1. The entity record should update
2. Chunks should be re-extracted
3. Embeddings should be regenerated
4. Similarity cache should be invalidated/recomputed

We need a mechanism to detect changes and trigger re-embedding.

## Decision

**Hybrid approach**:
1. **File hash tracking** in database for change detection
2. **watchdog** Python library for real-time file system events
3. **Manual trigger** via CLI for batch re-embedding

### Change Detection

```sql
-- Track file state
ALTER TABLE entities ADD COLUMN file_hash TEXT;
ALTER TABLE entities ADD COLUMN file_mtime TEXT;
```

```python
import hashlib
from pathlib import Path

def file_changed(entity: dict) -> bool:
    path = Path(entity['file_path'])
    if not path.exists():
        return True  # File deleted

    current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    return current_hash != entity['file_hash']
```

### Real-time Watching

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ContextFileHandler(FileSystemEventHandler):
    PATTERNS = {
        'content/agents/*.md': 'agent',
        'content/skills/*/SKILL.md': 'skill',
        'content/rules/*.md': 'rule',
        '.claude/rules/*.md': 'rule',
        '**/CLAUDE.md': 'claude_md',
    }

    def on_modified(self, event):
        entity_type = self.match_pattern(event.src_path)
        if entity_type:
            queue_reembed(event.src_path, entity_type)

    def on_created(self, event):
        entity_type = self.match_pattern(event.src_path)
        if entity_type:
            queue_ingest(event.src_path, entity_type)

    def on_deleted(self, event):
        queue_delete(event.src_path)

# Run watcher
observer = Observer()
observer.schedule(ContextFileHandler(), path='content/', recursive=True)
observer.schedule(ContextFileHandler(), path='.claude/', recursive=True)
observer.start()
```

### Batch Re-embedding

```bash
# Re-embed all stale entities
scripts/embed.py --check-all

# Re-embed specific type
scripts/embed.py --type skill

# Force re-embed everything (model change)
scripts/embed.py --force --model nomic-embed-text
```

### Rationale

1. **Hash tracking**: Reliable change detection, survives watcher restarts
2. **watchdog**: Cross-platform, battle-tested, low overhead
3. **Queue-based**: Debounces rapid saves, batches for efficiency
4. **Manual CLI**: Escape hatch for bulk operations

### Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Git hooks | Only triggers on commit, not during editing |
| fswatch | macOS-only, less Python integration |
| inotify | Linux-only |
| Polling | Higher CPU usage, slower detection |

## Consequences

- Watcher process must run during development (or use CLI for batch)
- Queue prevents thundering herd on rapid saves
- Similarity cache invalidation must cascade from entity changes
- Need graceful handling of partial re-embed (interrupted process)

## References

- [watchdog](https://python-watchdog.readthedocs.io/)
