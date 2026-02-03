# Common Knowledge Graph Queries

SQL query patterns for the knowledge graph. See also `scripts/sql/` for executable versions.

## Semantic Search

### Find entities similar to a query

```sql
-- Requires: query embedding generated externally
-- :query_embedding = embed("kubernetes deployment management")
-- :entity_type = 'mcp_server' (or NULL for all types)

SELECT
  e.entity_type,
  e.name,
  e.slug,
  vec_distance_cosine(:query_embedding, vc.embedding) AS distance
FROM vec_chunks vc
JOIN embedding_meta em ON vc.embedding_id = em.id
JOIN chunks c ON em.chunk_id = c.id
JOIN entities e ON c.entity_id = e.id
WHERE c.chunk_level = 'file'
  AND (:entity_type IS NULL OR e.entity_type = :entity_type)
ORDER BY distance
LIMIT 20;
```

### Hybrid search (FTS + vector)

```sql
-- Reciprocal Rank Fusion combining keyword and semantic results
WITH
fts_results AS (
  SELECT rowid AS entity_id, ROW_NUMBER() OVER (ORDER BY rank) AS fts_rank
  FROM entities_fts
  WHERE entities_fts MATCH :query_text
  LIMIT 50
),
vec_results AS (
  SELECT c.entity_id, ROW_NUMBER() OVER (ORDER BY vec_distance_cosine(:query_embedding, vc.embedding)) AS vec_rank
  FROM vec_chunks vc
  JOIN embedding_meta em ON vc.embedding_id = em.id
  JOIN chunks c ON em.chunk_id = c.id
  WHERE c.chunk_level = 'file'
  LIMIT 50
),
combined AS (
  SELECT
    COALESCE(f.entity_id, v.entity_id) AS entity_id,
    COALESCE(1.0 / (60 + f.fts_rank), 0) + COALESCE(1.0 / (60 + v.vec_rank), 0) AS rrf_score
  FROM fts_results f
  FULL OUTER JOIN vec_results v ON f.entity_id = v.entity_id
)
SELECT e.*, c.rrf_score
FROM combined c
JOIN entities e ON c.entity_id = e.id
ORDER BY c.rrf_score DESC
LIMIT 20;
```

## Relationship Queries

### Find what an entity uses (1-hop)

```sql
SELECT
  e.entity_type,
  e.name,
  r.rel_type
FROM relationships r
JOIN entities e ON r.to_entity_id = e.id
WHERE r.from_entity_id = :entity_id;
```

### Find what uses an entity (reverse lookup)

```sql
SELECT
  e.entity_type,
  e.name,
  r.rel_type
FROM relationships r
JOIN entities e ON r.from_entity_id = e.id
WHERE r.to_entity_id = :entity_id;
```

### Multi-hop traversal (2-3 hops)

```sql
-- What uses X, and what do THOSE things use?
WITH RECURSIVE usage_chain(entity_id, depth, path) AS (
  -- Base: direct users of target
  SELECT from_entity_id, 1, '/' || :start_id || '/' || from_entity_id || '/'
  FROM relationships
  WHERE to_entity_id = :start_id AND rel_type = 'uses'

  UNION ALL

  -- Recursive: what do those use?
  SELECT r.to_entity_id, uc.depth + 1, uc.path || r.to_entity_id || '/'
  FROM usage_chain uc
  JOIN relationships r ON uc.entity_id = r.from_entity_id
  WHERE uc.depth < 3
    AND r.rel_type = 'uses'
    AND instr(uc.path, '/' || r.to_entity_id || '/') = 0  -- Prevent cycles
)
SELECT DISTINCT
  e.entity_type,
  e.name,
  uc.depth
FROM usage_chain uc
JOIN entities e ON uc.entity_id = e.id
ORDER BY uc.depth, e.entity_type;
```

## MCP Server Queries

### Servers providing specific tools

```sql
SELECT
  e.name AS server_name,
  e.slug,
  GROUP_CONCAT(t.name) AS matching_tools,
  COUNT(*) AS match_count
FROM entities e
JOIN mcp_server_tools t ON e.id = t.server_id
WHERE t.name IN ('file_read', 'file_write', 'search')
GROUP BY e.id
ORDER BY match_count DESC;
```

### Tool overlap between servers

```sql
SELECT
  e1.name AS server_1,
  e2.name AS server_2,
  COUNT(*) AS shared_tools,
  GROUP_CONCAT(t1.name) AS shared_tool_names
FROM mcp_server_tools t1
JOIN mcp_server_tools t2 ON t1.name = t2.name
JOIN entities e1 ON t1.server_id = e1.id
JOIN entities e2 ON t2.server_id = e2.id
WHERE t1.server_id < t2.server_id
GROUP BY t1.server_id, t2.server_id
HAVING shared_tools > 2
ORDER BY shared_tools DESC;
```

### Servers with minimal dependencies covering required tools

```sql
-- Step 1: Find servers that have ANY of the required tools
WITH required_tools(name) AS (
  VALUES ('file_read'), ('file_write'), ('execute_command')
),
server_coverage AS (
  SELECT
    e.id,
    e.name,
    COUNT(DISTINCT t.name) AS tools_covered,
    (SELECT COUNT(*) FROM required_tools) AS tools_needed
  FROM entities e
  JOIN mcp_server_tools t ON e.id = t.server_id
  JOIN required_tools rt ON t.name = rt.name
  WHERE e.entity_type = 'mcp_server'
  GROUP BY e.id
),
server_deps AS (
  SELECT server_id, COUNT(*) AS dep_count
  FROM mcp_server_deps
  WHERE required = 1
  GROUP BY server_id
)
SELECT
  sc.name,
  sc.tools_covered,
  COALESCE(sd.dep_count, 0) AS required_deps,
  ROUND(sc.tools_covered * 1.0 / COALESCE(sd.dep_count + 1, 1), 2) AS efficiency
FROM server_coverage sc
LEFT JOIN server_deps sd ON sc.id = sd.server_id
WHERE sc.tools_covered > 0
ORDER BY efficiency DESC, sc.tools_covered DESC
LIMIT 10;
```

## Similarity and Overlap

### Most similar entities (from cache)

```sql
SELECT
  e.entity_type,
  e.name,
  sc.score,
  sc.similarity_type
FROM similarity_cache sc
JOIN entities e ON sc.entity_b_id = e.id
WHERE sc.entity_a_id = :entity_id
  AND sc.similarity_type = 'semantic'
ORDER BY sc.score DESC
LIMIT 10;
```

### Entities with high internal variance (decomposition candidates)

```sql
-- Entities where section embeddings are far apart from each other
-- Indicates the entity covers multiple distinct topics → consider splitting
WITH section_pairs AS (
  SELECT
    c1.entity_id,
    vec_distance_cosine(vc1.embedding, vc2.embedding) AS distance
  FROM chunks c1
  JOIN chunks c2 ON c1.entity_id = c2.entity_id AND c1.id < c2.id
  JOIN embedding_meta em1 ON c1.id = em1.chunk_id
  JOIN embedding_meta em2 ON c2.id = em2.chunk_id
  JOIN vec_chunks vc1 ON em1.id = vc1.embedding_id
  JOIN vec_chunks vc2 ON em2.id = vc2.embedding_id
  WHERE c1.chunk_level = 'section' AND c2.chunk_level = 'section'
)
SELECT
  e.entity_type,
  e.name,
  AVG(sp.distance) AS avg_section_distance,
  COUNT(*) AS section_pairs,
  CASE
    WHEN AVG(sp.distance) > 0.5 THEN 'DECOMPOSE'
    WHEN AVG(sp.distance) > 0.3 THEN 'REFINE'
    ELSE 'OK'
  END AS recommendation
FROM section_pairs sp
JOIN entities e ON sp.entity_id = e.id
GROUP BY sp.entity_id
HAVING section_pairs >= 3
ORDER BY avg_section_distance DESC;
```

## Analytics

### Entity counts by type

```sql
SELECT entity_type, COUNT(*) AS count
FROM entities
GROUP BY entity_type
ORDER BY count DESC;
```

### Embedding coverage

```sql
SELECT
  e.entity_type,
  COUNT(DISTINCT e.id) AS total_entities,
  COUNT(DISTINCT c.entity_id) AS entities_with_chunks,
  COUNT(DISTINCT em.chunk_id) AS chunks_with_embeddings
FROM entities e
LEFT JOIN chunks c ON e.id = c.entity_id
LEFT JOIN embedding_meta em ON c.id = em.chunk_id
GROUP BY e.entity_type;
```

### Stale embeddings (file changed since embedding)

```sql
SELECT
  e.name,
  e.file_path,
  e.updated_at AS file_updated,
  MAX(em.created_at) AS last_embedded
FROM entities e
JOIN chunks c ON e.id = c.entity_id
JOIN embedding_meta em ON c.id = em.chunk_id
GROUP BY e.id
HAVING e.updated_at > MAX(em.created_at);
```
