-- Knowledge Graph Schema
-- Version: 1.1.0
-- See: docs/src/adr/001-primary-store.md
--
-- v1.1.0: Merged registry-cache fields into mcp_servers_ext and mcp_server_assessments

-- =============================================================================
-- CORE ENTITY STORAGE
-- =============================================================================

-- Universal entity table (all context component types)
CREATE TABLE IF NOT EXISTS entities (
  id INTEGER PRIMARY KEY,
  entity_type TEXT NOT NULL,  -- 'mcp_server', 'skill', 'rule', 'agent', 'plugin', 'hook', 'claude_md', 'command', 'output_style'
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  file_path TEXT,             -- Source file (for re-embedding triggers)
  file_hash TEXT,             -- SHA256 for change detection
  file_mtime TEXT,            -- Last modified time
  content TEXT,               -- Full text content (retained for re-embedding)
  metadata JSON,              -- Type-specific structured data
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_file ON entities(file_path);
CREATE INDEX IF NOT EXISTS idx_entities_slug ON entities(slug);

-- =============================================================================
-- TYPE-SPECIFIC EXTENSION TABLES
-- =============================================================================

-- MCP Server specific fields
CREATE TABLE IF NOT EXISTS mcp_servers_ext (
  entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
  install_method TEXT,        -- 'brew', 'npx', 'pip', 'uvx', 'docker', 'manual'
  install_command TEXT,
  repository TEXT,
  homepage TEXT,
  language TEXT,
  transport TEXT,             -- 'stdio', 'sse', 'http-stream', 'multi'
  stars INTEGER,
  last_updated TEXT,
  pricing TEXT,               -- 'free', 'paid', 'freemium'
  pricing_notes TEXT,         -- details on tiers/limits
  source_registry TEXT,
  source_url TEXT,
  -- v1.1.0: Fields merged from registry-cache
  dockerized INTEGER DEFAULT 0,  -- 0=no, 1=yes, 2=docker-only
  locale TEXT DEFAULT 'en',      -- ISO 639-1 codes, comma-sep
  config_schema TEXT,            -- JSON: server's configuration/env schema
  discovered_at TEXT,
  refreshed_at TEXT
);

-- Skill specific fields
CREATE TABLE IF NOT EXISTS skills_ext (
  entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
  disable_model_invocation INTEGER DEFAULT 0,
  allowed_tools TEXT          -- Comma-separated or JSON array
);

-- Agent specific fields
CREATE TABLE IF NOT EXISTS agents_ext (
  entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
  model TEXT,                 -- 'sonnet', 'haiku', 'opus'
  tools TEXT                  -- Comma-separated or JSON array
);

-- Plugin specific fields
CREATE TABLE IF NOT EXISTS plugins_ext (
  entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
  domain TEXT,
  maturity TEXT,              -- 'draft', 'beta', 'stable'
  component_count INTEGER
);

-- Hook specific fields
CREATE TABLE IF NOT EXISTS hooks_ext (
  entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
  hook_type TEXT,             -- 'PreToolUse', 'PostToolUse', 'Notification', etc.
  matcher TEXT,
  command TEXT
);

-- =============================================================================
-- MCP SERVER DETAILS (existing schema compatibility)
-- =============================================================================

-- Tools exposed by MCP servers
CREATE TABLE IF NOT EXISTS mcp_server_tools (
  id INTEGER PRIMARY KEY,
  server_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  input_schema JSON,
  UNIQUE(server_id, name)
);

CREATE INDEX IF NOT EXISTS idx_tools_server ON mcp_server_tools(server_id);
CREATE INDEX IF NOT EXISTS idx_tools_name ON mcp_server_tools(name);

-- Dependencies required by MCP servers
CREATE TABLE IF NOT EXISTS mcp_server_deps (
  id INTEGER PRIMARY KEY,
  server_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  kind TEXT,                  -- 'binary', 'api', 'service', 'library', 'runtime'
  required INTEGER DEFAULT 1,
  version_constraint TEXT,
  notes TEXT,                 -- e.g., "needs BRAVE_API_KEY env var"
  UNIQUE(server_id, name)
);

CREATE INDEX IF NOT EXISTS idx_deps_server ON mcp_server_deps(server_id);

-- Assessments of MCP servers (domain relevance + code quality)
CREATE TABLE IF NOT EXISTS mcp_server_assessments (
  id INTEGER PRIMARY KEY,
  server_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  -- Domain relevance (optional, for use-case specific assessments)
  domain TEXT,                    -- NULL for global assessments
  relevance_score REAL,
  coverage_pct REAL,
  recommendation TEXT,            -- 'reuse', 'extend', 'create'
  notes TEXT,
  -- v1.1.0: Code quality fields merged from registry-cache
  has_unit_tests INTEGER DEFAULT 0,
  has_integration_tests INTEGER DEFAULT 0,
  has_e2e_tests INTEGER DEFAULT 0,
  test_coverage_pct REAL,         -- 0.0-100.0 if measurable
  test_robustness TEXT,           -- summary assessment of test quality
  codebase_ast TEXT,              -- JSON: simplified AST / structure map
  codebase_index TEXT,            -- JSON: file index with line counts, exports
  codebase_summary TEXT,          -- prose summary of architecture
  assessed_at TEXT DEFAULT (datetime('now')),
  UNIQUE(server_id, domain)
);

CREATE INDEX IF NOT EXISTS idx_assessments_server ON mcp_server_assessments(server_id);

-- =============================================================================
-- CHUNKING AND EMBEDDINGS
-- =============================================================================

-- Chunks for multi-level embedding
CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY,
  entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  chunk_level TEXT NOT NULL,  -- 'file', 'section', 'heading', 'paragraph', 'sentence'
  chunk_index INTEGER,        -- Position within entity at this level
  chunk_text TEXT NOT NULL,   -- Original text (retained for re-embedding)
  heading TEXT,               -- Section heading if applicable
  start_line INTEGER,
  end_line INTEGER,
  parent_chunk_id INTEGER REFERENCES chunks(id),  -- For hierarchical chunks
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chunks_entity ON chunks(entity_id);
CREATE INDEX IF NOT EXISTS idx_chunks_level ON chunks(chunk_level);
CREATE INDEX IF NOT EXISTS idx_chunks_parent ON chunks(parent_chunk_id);

-- Embedding metadata (tracks model, dimensions, when generated)
CREATE TABLE IF NOT EXISTS embedding_meta (
  id INTEGER PRIMARY KEY,
  chunk_id INTEGER REFERENCES chunks(id) ON DELETE CASCADE,
  model_name TEXT NOT NULL,   -- 'nomic-embed-text', 'all-MiniLM-L6-v2', etc.
  model_version TEXT,
  dimensions INTEGER NOT NULL,
  quantization TEXT DEFAULT 'float32',  -- 'float32', 'int8', 'binary'
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(chunk_id, model_name)  -- One embedding per model per chunk
);

CREATE INDEX IF NOT EXISTS idx_embedding_chunk ON embedding_meta(chunk_id);
CREATE INDEX IF NOT EXISTS idx_embedding_model ON embedding_meta(model_name);

-- Vector storage (sqlite-vec virtual tables)
-- Note: Must load sqlite-vec extension before creating these
-- CREATE VIRTUAL TABLE vec_chunks USING vec0(
--   embedding_id INTEGER PRIMARY KEY,
--   embedding FLOAT[768]  -- Dimension must match model (768 for nomic-embed-text)
-- );

-- =============================================================================
-- RELATIONSHIPS (GRAPH EDGES)
-- =============================================================================

-- Explicit relationships between entities
CREATE TABLE IF NOT EXISTS relationships (
  id INTEGER PRIMARY KEY,
  from_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  to_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  rel_type TEXT NOT NULL,     -- 'uses', 'extends', 'contains', 'integrates_with', 'depends_on', 'similar_to'
  weight REAL DEFAULT 1.0,    -- Relationship strength (for weighted queries)
  metadata JSON,              -- Additional relationship data
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(from_entity_id, to_entity_id, rel_type)
);

CREATE INDEX IF NOT EXISTS idx_rel_from ON relationships(from_entity_id);
CREATE INDEX IF NOT EXISTS idx_rel_to ON relationships(to_entity_id);
CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(rel_type);

-- Computed similarity cache (refreshed periodically)
CREATE TABLE IF NOT EXISTS similarity_cache (
  id INTEGER PRIMARY KEY,
  entity_a_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  entity_b_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
  similarity_type TEXT NOT NULL,  -- 'semantic', 'neighborhood', 'tool_overlap', 'structural'
  score REAL NOT NULL,
  computed_at TEXT DEFAULT (datetime('now')),
  UNIQUE(entity_a_id, entity_b_id, similarity_type)
);

CREATE INDEX IF NOT EXISTS idx_sim_a ON similarity_cache(entity_a_id);
CREATE INDEX IF NOT EXISTS idx_sim_b ON similarity_cache(entity_b_id);
CREATE INDEX IF NOT EXISTS idx_sim_type ON similarity_cache(similarity_type);

-- =============================================================================
-- FULL-TEXT SEARCH
-- =============================================================================

-- FTS5 index over entities (name + content)
CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts USING fts5(
  name,
  content,
  content='entities',
  content_rowid='id',
  tokenize='porter unicode61'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS entities_ai AFTER INSERT ON entities BEGIN
  INSERT INTO entities_fts(rowid, name, content) VALUES (new.id, new.name, new.content);
END;

CREATE TRIGGER IF NOT EXISTS entities_ad AFTER DELETE ON entities BEGIN
  INSERT INTO entities_fts(entities_fts, rowid, name, content) VALUES('delete', old.id, old.name, old.content);
END;

CREATE TRIGGER IF NOT EXISTS entities_au AFTER UPDATE ON entities BEGIN
  INSERT INTO entities_fts(entities_fts, rowid, name, content) VALUES('delete', old.id, old.name, old.content);
  INSERT INTO entities_fts(rowid, name, content) VALUES (new.id, new.name, new.content);
END;

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Unified view of entities with their type-specific extensions
CREATE VIEW IF NOT EXISTS v_mcp_servers AS
SELECT
  e.*,
  ext.install_method,
  ext.install_command,
  ext.repository,
  ext.homepage,
  ext.language,
  ext.transport,
  ext.stars,
  ext.last_updated,
  ext.pricing,
  ext.pricing_notes,
  ext.source_registry,
  ext.source_url,
  ext.dockerized,
  ext.locale,
  ext.config_schema,
  ext.discovered_at,
  ext.refreshed_at,
  (SELECT COUNT(*) FROM mcp_server_tools t WHERE t.server_id = e.id) AS tool_count,
  (SELECT COUNT(*) FROM mcp_server_deps d WHERE d.server_id = e.id) AS dep_count
FROM entities e
LEFT JOIN mcp_servers_ext ext ON e.id = ext.entity_id
WHERE e.entity_type = 'mcp_server';

CREATE VIEW IF NOT EXISTS v_skills AS
SELECT
  e.*,
  ext.disable_model_invocation,
  ext.allowed_tools
FROM entities e
LEFT JOIN skills_ext ext ON e.id = ext.entity_id
WHERE e.entity_type = 'skill';

CREATE VIEW IF NOT EXISTS v_agents AS
SELECT
  e.*,
  ext.model,
  ext.tools
FROM entities e
LEFT JOIN agents_ext ext ON e.id = ext.entity_id
WHERE e.entity_type = 'agent';

-- Server similarity view (tools in common)
CREATE VIEW IF NOT EXISTS v_server_tool_similarity AS
SELECT
  s1.id AS server_1_id,
  s2.id AS server_2_id,
  e1.name AS server_1_name,
  e2.name AS server_2_name,
  COUNT(DISTINCT t1.name) AS shared_tools,
  GROUP_CONCAT(DISTINCT t1.name) AS shared_tool_names
FROM mcp_server_tools t1
JOIN mcp_server_tools t2 ON t1.name = t2.name AND t1.server_id < t2.server_id
JOIN entities e1 ON t1.server_id = e1.id
JOIN entities e2 ON t2.server_id = e2.id
CROSS JOIN (SELECT id FROM entities WHERE entity_type = 'mcp_server') s1
CROSS JOIN (SELECT id FROM entities WHERE entity_type = 'mcp_server') s2
WHERE t1.server_id = s1.id AND t2.server_id = s2.id
GROUP BY s1.id, s2.id;
