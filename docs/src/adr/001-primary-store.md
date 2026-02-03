# ADR-001: Primary Data Store

## Status

Accepted

## Context

This project manages a knowledge graph of Claude Code context components: MCP servers, skills, rules, agents, plugins, hooks, CLAUDE.md files, commands, and output styles. We need a primary data store that supports:

- Heterogeneous entity storage with type-specific metadata
- Explicit relationships (uses, extends, contains)
- Computed similarity relationships
- Full-text search
- Vector similarity search
- Version control (text dump for git)
- CLI accessibility for agent scripts

## Decision

**SQLite** as the primary relational store.

### Rationale

1. **Version control**: Single-file database with `.dump` producing human-readable SQL text
2. **Embedded**: No server process, works in scripts and agents
3. **Mature**: 25+ years, battle-tested, extensive tooling
4. **Extensible**: Supports FTS5 (full-text), sqlite-vec (vectors), JSON functions
5. **Universal CLI**: `sqlite3` available everywhere, agents can query directly
6. **ACID**: Full transaction support for concurrent access

### Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| PostgreSQL | Server process overhead, overkill for single-user project |
| DuckDB | Less tooling ecosystem, analytics-focused not OLTP |
| HelixDB | No local embedding support, unclear version control story |
| KuzuDB/Bighorn | Adds complexity; can layer on top if graph queries become critical |

## Consequences

- All data lives in `.data/mcp/knowledge-graph.db`
- Agents use `sqlite3` CLI or Python `sqlite3` module
- Schema must accommodate heterogeneous entities (single `entities` table with type column, plus extension tables)
- Graph traversal uses recursive CTEs (adequate for 2-3 hop queries)
- Complex graph algorithms may require future Bighorn integration

## References

- [SQLite Documentation](https://sqlite.org/docs.html)
- [sqlite-vec](https://github.com/asg017/sqlite-vec)
