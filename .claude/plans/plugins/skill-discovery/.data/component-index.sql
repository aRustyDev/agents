-- Component Index Database Schema
-- Phase 5: Aggregation & Indexing
-- Created: 2026-03-08

-- Drop existing tables if recreating
DROP TABLE IF EXISTS components_fts;
DROP TABLE IF EXISTS plugin_components;
DROP TABLE IF EXISTS components;
DROP TABLE IF EXISTS registries;

-- Registries table: stores metadata about discovery sources
CREATE TABLE registries (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT UNIQUE,
    type TEXT CHECK (type IN (
        'skill_registry', 'plugin_registry', 'mcp_registry',
        'code_repository', 'awesome_list', 'marketplace', 'aggregator'
    )),
    component_types TEXT,  -- JSON array of types it contains
    api_docs_url TEXT,
    has_search BOOLEAN DEFAULT FALSE,
    has_api BOOLEAN DEFAULT FALSE,
    auth_required BOOLEAN DEFAULT FALSE,
    rate_limit TEXT,
    scraping_allowed BOOLEAN DEFAULT TRUE,
    access_method TEXT,  -- 'api', 'webfetch', 'crawl4ai', 'gh_cli'
    component_count INTEGER,
    last_checked DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Components table: stores individual skills, agents, commands, etc.
CREATE TABLE components (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN (
        'skill', 'agent', 'command', 'rule',
        'prompt', 'hook', 'mcp_server', 'plugin'
    )),
    description TEXT,
    author TEXT,
    canonical_url TEXT,
    github_url TEXT,
    content_hash TEXT,
    category TEXT,
    tags TEXT,  -- JSON array
    quality_score REAL DEFAULT 0.0,
    star_count INTEGER DEFAULT 0,
    source_type TEXT CHECK (source_type IN (
        'registry', 'github', 'npm', 'pypi', 'crates', 'awesome_list'
    )),
    source_name TEXT,  -- e.g., "skillsmp", "buildwithclaude"
    source_url TEXT,
    install_command TEXT,
    last_updated DATETIME,
    last_checked DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(name, author, type)
);

-- Plugin components: maps plugins to their bundled components
CREATE TABLE plugin_components (
    plugin_id TEXT NOT NULL REFERENCES components(id),
    component_id TEXT NOT NULL REFERENCES components(id),
    component_type TEXT NOT NULL,
    component_path TEXT,  -- path within plugin
    PRIMARY KEY (plugin_id, component_id)
);

-- Full-text search index for component discovery
CREATE VIRTUAL TABLE components_fts USING fts5(
    name,
    description,
    author,
    tags,
    content='components',
    content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER components_ai AFTER INSERT ON components BEGIN
    INSERT INTO components_fts(rowid, name, description, author, tags)
    VALUES (NEW.rowid, NEW.name, NEW.description, NEW.author, NEW.tags);
END;

CREATE TRIGGER components_ad AFTER DELETE ON components BEGIN
    INSERT INTO components_fts(components_fts, rowid, name, description, author, tags)
    VALUES ('delete', OLD.rowid, OLD.name, OLD.description, OLD.author, OLD.tags);
END;

CREATE TRIGGER components_au AFTER UPDATE ON components BEGIN
    INSERT INTO components_fts(components_fts, rowid, name, description, author, tags)
    VALUES ('delete', OLD.rowid, OLD.name, OLD.description, OLD.author, OLD.tags);
    INSERT INTO components_fts(rowid, name, description, author, tags)
    VALUES (NEW.rowid, NEW.name, NEW.description, NEW.author, NEW.tags);
END;

-- Indexes for common queries
CREATE INDEX idx_components_type ON components(type);
CREATE INDEX idx_components_source ON components(source_name);
CREATE INDEX idx_components_quality ON components(quality_score DESC);
CREATE INDEX idx_components_stars ON components(star_count DESC);
CREATE INDEX idx_components_author ON components(author);
CREATE INDEX idx_registries_type ON registries(type);
