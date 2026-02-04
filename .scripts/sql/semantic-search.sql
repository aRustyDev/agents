-- Semantic search for entities similar to a query
-- Usage: Requires query embedding to be passed as parameter
--
-- Example (Python):
--   embedding = ollama.embeddings(model='nomic-embed-text', prompt='kubernetes management')['embedding']
--   results = conn.execute(open('scripts/sql/semantic-search.sql').read(), {
--       'query_embedding': struct.pack(f'{len(embedding)}f', *embedding),
--       'entity_type': 'mcp_server',  -- or NULL for all types
--       'limit': 20
--   })

SELECT
  e.id,
  e.entity_type,
  e.name,
  e.slug,
  e.file_path,
  substr(e.content, 1, 200) AS content_preview,
  json_extract(e.metadata, '$.description') AS description,
  vec_distance_cosine(:query_embedding, vc.embedding) AS distance,
  1.0 - vec_distance_cosine(:query_embedding, vc.embedding) AS similarity
FROM vec_chunks vc
JOIN embedding_meta em ON vc.embedding_id = em.id
JOIN chunks c ON em.chunk_id = c.id
JOIN entities e ON c.entity_id = e.id
WHERE c.chunk_level = 'file'
  AND (:entity_type IS NULL OR e.entity_type = :entity_type)
ORDER BY distance ASC
LIMIT :limit;
