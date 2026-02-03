-- Analyze coverage: which servers can cover a set of required tools
-- with minimal dependencies
--
-- Parameters:
--   Required tools should be inserted into a temp table before running:
--   CREATE TEMP TABLE required_tools(name TEXT);
--   INSERT INTO required_tools VALUES ('tool1'), ('tool2'), ('tool3');

WITH
-- Count how many required tools each server provides
server_tool_coverage AS (
  SELECT
    e.id AS server_id,
    e.name AS server_name,
    e.slug,
    COUNT(DISTINCT t.name) AS tools_provided,
    GROUP_CONCAT(DISTINCT t.name) AS provided_tool_list
  FROM entities e
  JOIN mcp_server_tools t ON e.id = t.server_id
  JOIN required_tools rt ON t.name = rt.name
  WHERE e.entity_type = 'mcp_server'
  GROUP BY e.id
),

-- Count dependencies per server
server_dep_count AS (
  SELECT
    server_id,
    COUNT(*) AS total_deps,
    SUM(CASE WHEN required = 1 THEN 1 ELSE 0 END) AS required_deps
  FROM mcp_server_deps
  GROUP BY server_id
),

-- Get total required tools count
required_count AS (
  SELECT COUNT(*) AS total FROM required_tools
)

SELECT
  stc.server_name,
  stc.slug,
  stc.tools_provided,
  rc.total AS tools_required,
  ROUND(stc.tools_provided * 100.0 / rc.total, 1) AS coverage_pct,
  COALESCE(sdc.required_deps, 0) AS required_deps,
  COALESCE(sdc.total_deps, 0) AS total_deps,
  -- Efficiency: tools provided per required dependency
  ROUND(stc.tools_provided * 1.0 / (COALESCE(sdc.required_deps, 0) + 1), 2) AS efficiency,
  stc.provided_tool_list
FROM server_tool_coverage stc
CROSS JOIN required_count rc
LEFT JOIN server_dep_count sdc ON stc.server_id = sdc.server_id
ORDER BY
  coverage_pct DESC,
  efficiency DESC,
  required_deps ASC;
