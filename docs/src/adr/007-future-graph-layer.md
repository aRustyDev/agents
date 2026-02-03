# ADR-007: Future Graph Layer (Bighorn/KuzuDB)

## Status

Proposed (not yet implemented)

## Context

Some query patterns are awkward in SQL:
- Graph neighborhood clustering (similarity by connections, not content)
- Complex pattern matching ("find all A→B→C where B also connects to D")
- Graph algorithms (PageRank, community detection, centrality)

SQLite with recursive CTEs handles 80% of graph queries. This ADR documents when and how to add a dedicated graph layer.

## Decision

**Defer Bighorn integration** until one of these triggers:

### Trigger Conditions

1. **Neighborhood queries become frequent**: "Find entities with similar ecosystems" asked >10 times/week
2. **Deep traversals needed**: Queries requiring 4+ hops
3. **Graph algorithms needed**: PageRank for importance ranking, Louvain for clustering
4. **SQL becomes unmaintainable**: Graph queries exceeding 50 lines of CTE

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  SQLite (Source of Truth)  │  Bighorn (Analytics Layer)     │
│  - Entity CRUD             │  - Complex graph queries       │
│  - Vector search           │  - Neighborhood clustering     │
│  - Simple relationships    │  - Pattern matching            │
│  - FTS keyword search      │  - Graph algorithms            │
├─────────────────────────────────────────────────────────────┤
│              Sync Layer (SQLite → Bighorn)                  │
│  - Periodic full sync                                        │
│  - Triggered on significant changes                          │
└─────────────────────────────────────────────────────────────┘
```

### Sync Implementation

```python
import kuzu

def sync_to_bighorn():
    kuzu_db = kuzu.Database('./bighorn')
    kuzu_conn = kuzu.Connection(kuzu_db)

    # Load SQLite extension
    kuzu_conn.execute("INSTALL sqlite")
    kuzu_conn.execute("LOAD EXTENSION sqlite")
    kuzu_conn.execute("ATTACH '.data/mcp/knowledge-graph.db' AS sqlite (DBTYPE sqlite)")

    # Clear and reload (simple strategy)
    kuzu_conn.execute("DROP TABLE IF EXISTS Entity")
    kuzu_conn.execute("DROP TABLE IF EXISTS Relationship")

    # Create schema
    kuzu_conn.execute("""
        CREATE NODE TABLE Entity(
            id INT64 PRIMARY KEY,
            entity_type STRING,
            name STRING,
            slug STRING
        )
    """)
    kuzu_conn.execute("""
        CREATE REL TABLE Relationship(
            FROM Entity TO Entity,
            rel_type STRING
        )
    """)

    # Copy data
    kuzu_conn.execute("COPY Entity FROM (LOAD FROM sqlite.entities RETURN id, entity_type, name, slug)")
    kuzu_conn.execute("""
        COPY Relationship FROM (
            LOAD FROM sqlite.relationships
            RETURN from_entity_id, to_entity_id, rel_type
        )
    """)
```

### Example Graph Queries (Cypher)

```cypher
-- Neighborhood similarity (why we'd add Bighorn)
MATCH (a:Entity)-[r1]->(shared)<-[r2]-(b:Entity)
WHERE a.entity_type = 'agent' AND b.entity_type = 'agent' AND a.id < b.id
WITH a, b, COUNT(DISTINCT shared) AS common
MATCH (a)-[ra]->()
WITH a, b, common, COUNT(ra) AS a_degree
MATCH (b)-[rb]->()
WITH a, b, common, a_degree, COUNT(rb) AS b_degree
RETURN a.name, b.name,
       common * 1.0 / (a_degree + b_degree - common) AS jaccard
ORDER BY jaccard DESC

-- Transitive dependencies (4+ hops)
MATCH path = (s:Entity)-[:depends_on*1..5]->(d:Entity)
WHERE s.slug = 'my-plugin'
RETURN d.name, length(path) AS depth
ORDER BY depth

-- PageRank for entity importance
CALL algo.pageRank('Entity', 'Relationship')
YIELD node, score
RETURN node.name, score
ORDER BY score DESC
LIMIT 20
```

### Rationale for Deferral

1. **Complexity cost**: Second database to manage, sync logic, two query languages
2. **Current needs met**: Recursive CTEs + precomputed similarity handle existing queries
3. **KuzuDB archived**: Bighorn fork is young, stability uncertain
4. **YAGNI**: Don't add infrastructure until pain is real

### Alternatives

| Option | Notes |
|--------|-------|
| Ladybug (KuzuDB fork) | Less mature than Bighorn, focused on stability |
| Neo4j | Server-based, heavyweight |
| Apache AGE | Requires PostgreSQL |
| FalkorDBLite | Different architecture, not SQLite-compatible |

## Consequences

- Must monitor query complexity and frequency
- SQLite remains source of truth (Bighorn is read-only replica)
- Sync lag acceptable for analytics (not real-time)
- Can remove Bighorn if it doesn't prove valuable

## References

- [Bighorn GitHub](https://github.com/Kineviz/bighorn)
- [KuzuDB SQLite Extension](https://docs.kuzudb.com/extensions/attach/sqlite/)
