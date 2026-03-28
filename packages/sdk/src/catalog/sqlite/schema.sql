-- Catalog schema for SQLite backend
-- Matches CatalogEntry type from types.ts

CREATE TABLE IF NOT EXISTS catalog_entries (
  source TEXT NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  availability TEXT NOT NULL DEFAULT 'available',
  discovered_at TEXT,
  analyzed_at TEXT,
  content_hash TEXT,
  error_count INTEGER DEFAULT 0,
  -- Mechanical fields (JSON blob)
  mechanical TEXT,
  -- Analysis fields (JSON blob)
  analysis TEXT,
  PRIMARY KEY (source, name)
);

CREATE INDEX IF NOT EXISTS idx_catalog_type ON catalog_entries (type);
CREATE INDEX IF NOT EXISTS idx_catalog_availability ON catalog_entries (availability);
CREATE INDEX IF NOT EXISTS idx_catalog_source ON catalog_entries (source);

CREATE TABLE IF NOT EXISTS catalog_errors (
  source TEXT NOT NULL,
  name TEXT NOT NULL,
  run_id TEXT NOT NULL,
  error TEXT NOT NULL,
  error_type TEXT NOT NULL,
  error_detail TEXT NOT NULL,
  attempt_count INTEGER NOT NULL DEFAULT 1,
  last_attempt_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_errors_source_name ON catalog_errors (source, name);
CREATE INDEX IF NOT EXISTS idx_errors_run_id ON catalog_errors (run_id);
