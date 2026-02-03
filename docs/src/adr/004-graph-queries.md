# ADR-004: Graph Query Strategy

## Status

Accepted

## Context

The knowledge graph has both explicit relationships (agent uses skill) and computed relationships (semantic similarity). Query patterns include:
- Multi-hop traversal: "What uses X, and what do those use?"
- Neighborhood comparison: "Which agents have similar ecosystems?"
- Set operations: "Find servers covering tools X, Y, Z with minimal deps"
- Clustering: "Group entities by their relationships, not just content"

## Decision

**Tiered approach**:
1. **Recursive CTEs** for traversal queries (1-3 hops)
2. **Precomputed similarity cache** for pairwise comparisons
3. **Application code** for NP-hard optimization (set cover)
4. **Future: Bighorn** as read-only analytics layer if graph complexity increases

### Tier 1: Recursive CTEs (SQLite native)

```sql
-- 2-hop: What uses X, and what do those use?
WITH RECURSIVE usage_chain(entity_id, depth, path) AS (
  SELECT to_entity_id, 1, '/' || from_entity_id || '/'
  FROM relationships
  WHERE from_entity_id = :start_id AND rel_type = 'uses'

  UNION ALL

  SELECT r.to_entity_id, uc.depth + 1, uc.path || r.from_entity_id || '/'
  FROM usage_chain uc
  JOIN relationships r ON uc.entity_id = r.from_entity_id
  WHERE uc.depth < 3
    AND instr(uc.path, '/' || r.to_entity_id || '/') = 0
)
SELECT DISTINCT e.* FROM usage_chain uc
JOIN entities e ON uc.entity_id = e.id;
```

**Performance**: Good for depth ≤ 3, degrades on dense graphs.

### Tier 2: Precomputed Similarity Cache

```sql
CREATE TABLE similarity_cache (
  entity_a_id INTEGER,
  entity_b_id INTEGER,
  similarity_type TEXT,  -- 'semantic', 'neighborhood', 'tool_overlap'
  score REAL,
  computed_at TEXT,
  PRIMARY KEY (entity_a_id, entity_b_id, similarity_type)
);
```

Recomputed on entity update. Enables fast lookups:
```sql
SELECT * FROM similarity_cache
WHERE entity_a_id = :id AND similarity_type = 'neighborhood'
ORDER BY score DESC LIMIT 10;
```

### Tier 3: Application Code (NP-hard problems)

Set cover ("minimize servers while covering required tools") is NP-hard. SQL can fetch candidates; greedy algorithm runs in Python:

```python
def greedy_set_cover(required_tools: set, candidates: list[Server]) -> list[Server]:
    covered = set()
    selected = []
    while covered < required_tools:
        best = max(candidates,
                   key=lambda s: len(s.tools & required_tools - covered) / (len(s.deps) + 1))
        selected.append(best)
        covered |= best.tools
    return selected
```

### Tier 4: Future Bighorn Integration

If queries like "cluster by graph neighborhood" become frequent:

```python
# Periodic sync: SQLite → Bighorn
kuzu_conn.execute("ATTACH 'knowledge-graph.db' AS sqlite (DBTYPE sqlite)")
kuzu_conn.execute("COPY entities FROM (LOAD FROM sqlite.entities RETURN *)")
kuzu_conn.execute("COPY relationships FROM (LOAD FROM sqlite.relationships RETURN *)")

# Cypher for complex graph analytics
result = kuzu_conn.execute("""
  MATCH (a:Entity)-[r1]->(shared)<-[r2]-(b:Entity)
  WHERE a.id < b.id
  RETURN a.name, b.name, COUNT(shared) AS common
""")
```

### Rationale

1. **CTEs handle 80% of graph queries** without new dependencies
2. **Precomputation avoids repeated expensive calculations**
3. **NP-hard problems can't be solved in SQL anyway** — offload to application
4. **Bighorn is additive**, not a replacement — SQLite stays source of truth

## Consequences

- Complex graph algorithms (PageRank, community detection) not available in pure SQLite
- Similarity cache requires maintenance (recompute on changes)
- Bighorn adds complexity but can be deferred until truly needed
- Some queries will be verbose SQL vs clean Cypher

## References

- [SQLite Recursive CTEs](https://sqlite.org/lang_with.html)
- [Bighorn (KuzuDB fork)](https://github.com/Kineviz/bighorn)
