-- Convert Skills IR Research Database Schema
-- Version: 1.0
-- Purpose: Store research data for IR design and skill consolidation

-- ============================================================================
-- Language Families (Phase 1)
-- ============================================================================

-- Language families
CREATE TABLE IF NOT EXISTS families (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- paradigm, typing, memory, execution, effects, concurrency
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Family characteristics (EAV for flexibility)
CREATE TABLE IF NOT EXISTS family_characteristics (
    id INTEGER PRIMARY KEY,
    family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    dimension TEXT NOT NULL,  -- typing, memory, control, data, meta
    characteristic TEXT NOT NULL,
    value TEXT NOT NULL,
    notes TEXT,
    UNIQUE(family_id, dimension, characteristic)
);

-- Family relationships (influenced by, similar to, etc.)
CREATE TABLE IF NOT EXISTS family_relationships (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    to_family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,  -- influenced_by, similar_to, subset_of
    notes TEXT,
    UNIQUE(from_family_id, to_family_id, relationship_type)
);

-- ============================================================================
-- Languages (Phase 2)
-- ============================================================================

-- Languages
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    version TEXT,
    tier INTEGER NOT NULL,  -- 1, 2, or 3
    description TEXT,
    popularity_tiobe INTEGER,
    popularity_so REAL,
    github_repos TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Language-family relationships (many-to-many)
CREATE TABLE IF NOT EXISTS language_families (
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (language_id, family_id)
);

-- Language features (EAV for flexibility)
CREATE TABLE IF NOT EXISTS language_features (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    dimension TEXT NOT NULL,  -- typing, memory, control, data, meta
    feature TEXT NOT NULL,
    value TEXT NOT NULL,
    notes TEXT,
    UNIQUE(language_id, dimension, feature)
);

-- Language syntax patterns
CREATE TABLE IF NOT EXISTS language_syntax (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    pattern_name TEXT NOT NULL,  -- function_def, type_def, module_def, import
    pattern TEXT NOT NULL,
    notes TEXT,
    UNIQUE(language_id, pattern_name)
);

-- Language semantic gaps (inherent limitations)
CREATE TABLE IF NOT EXISTS language_gaps (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    gap_description TEXT NOT NULL,
    severity TEXT,  -- minor, moderate, major
    workaround TEXT
);

-- ============================================================================
-- Patterns (Phase 0)
-- ============================================================================

-- IR patterns extracted from convert-* skills
CREATE TABLE IF NOT EXISTS ir_patterns (
    id INTEGER PRIMARY KEY,
    skill_name TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    pattern_type TEXT NOT NULL,  -- type_mapping, idiom, gap, error, concurrency
    category TEXT,               -- subcategory within type
    source_pattern TEXT NOT NULL,
    target_pattern TEXT,
    is_lossy BOOLEAN DEFAULT FALSE,
    severity TEXT,               -- for gaps: impossible, lossy, structural, idiomatic
    mitigation TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patterns_skill ON ir_patterns(skill_name);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON ir_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_langs ON ir_patterns(source_lang, target_lang);

-- FTS for searching patterns
CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
    source_pattern, target_pattern, notes,
    content='ir_patterns',
    content_rowid='id'
);

-- ============================================================================
-- Semantic Gaps (Phase 3)
-- ============================================================================

-- Semantic gaps between families
CREATE TABLE IF NOT EXISTS semantic_gaps (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    gap_category TEXT NOT NULL,  -- impossible, lossy, structural, idiomatic, runtime, semantic
    concept TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL,  -- critical, high, medium, low
    mitigation TEXT,
    automation_level TEXT,  -- none, partial, full
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gaps_families ON semantic_gaps(from_family_id, to_family_id);
CREATE INDEX IF NOT EXISTS idx_gaps_category ON semantic_gaps(gap_category);
CREATE INDEX IF NOT EXISTS idx_gaps_severity ON semantic_gaps(severity);

-- Gap patterns (reusable across family pairs)
CREATE TABLE IF NOT EXISTS gap_patterns (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- type_system, memory, effects, concurrency
    description TEXT,
    from_concept TEXT NOT NULL,
    to_concept TEXT NOT NULL,
    mitigation_strategy TEXT,
    example_from TEXT,
    example_to TEXT
);

-- Human decision points
CREATE TABLE IF NOT EXISTS decision_points (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    options TEXT NOT NULL,  -- JSON array of options
    guidance TEXT,
    applicable_gaps TEXT  -- JSON array of gap IDs
);

-- ============================================================================
-- Conversion Difficulty (Phase 3)
-- ============================================================================

-- Conversion difficulty between families
CREATE TABLE IF NOT EXISTS family_conversion_difficulty (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    difficulty INTEGER NOT NULL,  -- 1=easy, 2=moderate, 3=hard, 4=very_hard
    notes TEXT,
    semantic_gaps TEXT,  -- JSON array of gap descriptions
    UNIQUE(from_family_id, to_family_id)
);

-- ============================================================================
-- Skill Coverage (Phase 2)
-- ============================================================================

-- Convert-* skill coverage
CREATE TABLE IF NOT EXISTS skill_coverage (
    id INTEGER PRIMARY KEY,
    source_lang_id INTEGER REFERENCES languages(id),
    target_lang_id INTEGER REFERENCES languages(id),
    skill_name TEXT,  -- NULL if no skill exists
    skill_path TEXT,
    is_bidirectional BOOLEAN DEFAULT FALSE,
    notes TEXT,
    UNIQUE(source_lang_id, target_lang_id)
);

-- ============================================================================
-- IR Schema (Phase 4)
-- ============================================================================

-- IR versions
CREATE TABLE IF NOT EXISTS ir_versions (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_language TEXT NOT NULL,
    source_path TEXT,
    extraction_tool_version TEXT,
    notes TEXT
);

-- IR units (atomic pieces of IR)
CREATE TABLE IF NOT EXISTS ir_units (
    id INTEGER PRIMARY KEY,
    version_id INTEGER REFERENCES ir_versions(id) ON DELETE CASCADE,
    layer INTEGER NOT NULL,  -- 0-4
    unit_type TEXT NOT NULL,  -- module, type, function, binding, expression
    content_hash TEXT NOT NULL,
    content_json TEXT NOT NULL,
    UNIQUE(version_id, content_hash)
);

CREATE INDEX IF NOT EXISTS idx_units_version ON ir_units(version_id);
CREATE INDEX IF NOT EXISTS idx_units_layer ON ir_units(layer);

-- IR dependencies
CREATE TABLE IF NOT EXISTS ir_dependencies (
    from_unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    to_unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    dependency_type TEXT NOT NULL,  -- uses, extends, imports, calls
    PRIMARY KEY (from_unit_id, to_unit_id, dependency_type)
);

CREATE INDEX IF NOT EXISTS idx_deps_from ON ir_dependencies(from_unit_id);
CREATE INDEX IF NOT EXISTS idx_deps_to ON ir_dependencies(to_unit_id);

-- Semantic annotations
CREATE TABLE IF NOT EXISTS ir_annotations (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    annotation_type TEXT NOT NULL,
    annotation_value TEXT NOT NULL,  -- JSON
    confidence REAL DEFAULT 1.0,
    source TEXT NOT NULL  -- explicit, inferred, default
);

-- IR gap markers
CREATE TABLE IF NOT EXISTS ir_gap_markers (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    gap_type TEXT NOT NULL,
    description TEXT,
    source_concept TEXT,
    mitigations TEXT  -- JSON array
);

-- ============================================================================
-- IR Layers (Phase 4)
-- ============================================================================

-- IR layer definitions
CREATE TABLE IF NOT EXISTS ir_layers (
    id INTEGER PRIMARY KEY,
    layer_num INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    schema_json TEXT  -- JSON Schema for this layer
);

-- Pre-populate IR layers
INSERT OR IGNORE INTO ir_layers (layer_num, name, description) VALUES
    (0, 'Expression IR', 'Full AST representation, operator semantics, literal values'),
    (1, 'Data Flow IR', 'Variable bindings, lifetimes, data transformations, side effects'),
    (2, 'Control Flow IR', 'Function signatures, control patterns, effects, concurrency'),
    (3, 'Type IR', 'Type definitions, relationships, generics, constraints'),
    (4, 'Structural IR', 'Modules, packages, visibility, imports/exports');

-- ============================================================================
-- Views
-- ============================================================================

-- View: Languages with their families
CREATE VIEW IF NOT EXISTS v_language_families AS
SELECT
    l.name as language,
    l.tier,
    GROUP_CONCAT(f.name, ', ') as families
FROM languages l
LEFT JOIN language_families lf ON l.id = lf.language_id
LEFT JOIN families f ON lf.family_id = f.id
GROUP BY l.id;

-- View: Skill coverage matrix
CREATE VIEW IF NOT EXISTS v_skill_coverage AS
SELECT
    sl.name as source_lang,
    tl.name as target_lang,
    sc.skill_name,
    sc.is_bidirectional
FROM skill_coverage sc
JOIN languages sl ON sc.source_lang_id = sl.id
JOIN languages tl ON sc.target_lang_id = tl.id;

-- View: Family conversion difficulty matrix
CREATE VIEW IF NOT EXISTS v_family_difficulty AS
SELECT
    ff.name as from_family,
    tf.name as to_family,
    fcd.difficulty,
    fcd.notes
FROM family_conversion_difficulty fcd
JOIN families ff ON fcd.from_family_id = ff.id
JOIN families tf ON fcd.to_family_id = tf.id;

-- ============================================================================
-- Triggers for FTS
-- ============================================================================

-- Triggers to keep FTS in sync with ir_patterns
CREATE TRIGGER IF NOT EXISTS ir_patterns_ai AFTER INSERT ON ir_patterns BEGIN
    INSERT INTO patterns_fts(rowid, source_pattern, target_pattern, notes)
    VALUES (new.id, new.source_pattern, new.target_pattern, new.notes);
END;

CREATE TRIGGER IF NOT EXISTS ir_patterns_ad AFTER DELETE ON ir_patterns BEGIN
    INSERT INTO patterns_fts(patterns_fts, rowid, source_pattern, target_pattern, notes)
    VALUES ('delete', old.id, old.source_pattern, old.target_pattern, old.notes);
END;

CREATE TRIGGER IF NOT EXISTS ir_patterns_au AFTER UPDATE ON ir_patterns BEGIN
    INSERT INTO patterns_fts(patterns_fts, rowid, source_pattern, target_pattern, notes)
    VALUES ('delete', old.id, old.source_pattern, old.target_pattern, old.notes);
    INSERT INTO patterns_fts(rowid, source_pattern, target_pattern, notes)
    VALUES (new.id, new.source_pattern, new.target_pattern, new.notes);
END;
