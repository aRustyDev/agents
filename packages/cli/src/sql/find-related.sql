-- Find all entities related to a given entity
-- Combines explicit relationships with semantic similarity
--
-- Parameters:
--   :entity_id - The entity to find relations for
--   :include_semantic - 1 to include semantic similarity, 0 for explicit only

WITH explicit_relations AS (
  -- Outgoing relationships (what this entity uses/extends/etc)
  SELECT
    'outgoing' AS direction,
    r.rel_type,
    e.id AS related_id,
    e.entity_type AS related_type,
    e.name AS related_name,
    r.weight AS score
  FROM relationships r
  JOIN entities e ON r.to_entity_id = e.id
  WHERE r.from_entity_id = :entity_id

  UNION ALL

  -- Incoming relationships (what uses/extends this entity)
  SELECT
    'incoming' AS direction,
    r.rel_type,
    e.id AS related_id,
    e.entity_type AS related_type,
    e.name AS related_name,
    r.weight AS score
  FROM relationships r
  JOIN entities e ON r.from_entity_id = e.id
  WHERE r.to_entity_id = :entity_id
),
semantic_relations AS (
  SELECT
    'semantic' AS direction,
    'similar_to' AS rel_type,
    sc.entity_b_id AS related_id,
    e.entity_type AS related_type,
    e.name AS related_name,
    sc.score
  FROM similarity_cache sc
  JOIN entities e ON sc.entity_b_id = e.id
  WHERE sc.entity_a_id = :entity_id
    AND sc.similarity_type = 'semantic'
    AND :include_semantic = 1
)
SELECT * FROM explicit_relations
UNION ALL
SELECT * FROM semantic_relations
ORDER BY
  CASE direction
    WHEN 'outgoing' THEN 1
    WHEN 'incoming' THEN 2
    WHEN 'semantic' THEN 3
  END,
  score DESC;
