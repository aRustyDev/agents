"""Pytest fixtures for ir-query tests."""

from __future__ import annotations

import sqlite3
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

# SQL schema for testing
TEST_SCHEMA = """
-- Language families
CREATE TABLE IF NOT EXISTS families (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Family characteristics
CREATE TABLE IF NOT EXISTS family_characteristics (
    id INTEGER PRIMARY KEY,
    family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    dimension TEXT NOT NULL,
    characteristic TEXT NOT NULL,
    value TEXT NOT NULL,
    notes TEXT,
    UNIQUE(family_id, dimension, characteristic)
);

-- Family relationships
CREATE TABLE IF NOT EXISTS family_relationships (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    to_family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    notes TEXT,
    UNIQUE(from_family_id, to_family_id, relationship_type)
);

-- Languages
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    version TEXT,
    tier INTEGER NOT NULL,
    description TEXT,
    popularity_tiobe INTEGER,
    popularity_so REAL,
    github_repos TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Language-family relationships
CREATE TABLE IF NOT EXISTS language_families (
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (language_id, family_id)
);

-- Language features
CREATE TABLE IF NOT EXISTS language_features (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    dimension TEXT NOT NULL,
    feature TEXT NOT NULL,
    value TEXT NOT NULL,
    notes TEXT,
    UNIQUE(language_id, dimension, feature)
);

-- Language syntax patterns
CREATE TABLE IF NOT EXISTS language_syntax (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    pattern_name TEXT NOT NULL,
    pattern TEXT NOT NULL,
    notes TEXT,
    UNIQUE(language_id, pattern_name)
);

-- Language gaps
CREATE TABLE IF NOT EXISTS language_gaps (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE,
    gap_description TEXT NOT NULL,
    severity TEXT,
    workaround TEXT
);

-- IR patterns
CREATE TABLE IF NOT EXISTS ir_patterns (
    id INTEGER PRIMARY KEY,
    skill_name TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    category TEXT,
    source_pattern TEXT NOT NULL,
    target_pattern TEXT,
    is_lossy BOOLEAN DEFAULT FALSE,
    severity TEXT,
    mitigation TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FTS for patterns
CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
    source_pattern, target_pattern, notes,
    content='ir_patterns',
    content_rowid='id'
);

-- Semantic gaps
CREATE TABLE IF NOT EXISTS semantic_gaps (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    gap_category TEXT NOT NULL,
    concept TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL,
    mitigation TEXT,
    automation_level TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gap patterns
CREATE TABLE IF NOT EXISTS gap_patterns (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    from_concept TEXT NOT NULL,
    to_concept TEXT NOT NULL,
    mitigation_strategy TEXT,
    example_from TEXT,
    example_to TEXT
);

-- Decision points
CREATE TABLE IF NOT EXISTS decision_points (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    options TEXT NOT NULL,
    guidance TEXT,
    applicable_gaps TEXT
);

-- Family conversion difficulty
CREATE TABLE IF NOT EXISTS family_conversion_difficulty (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    difficulty INTEGER NOT NULL,
    notes TEXT,
    semantic_gaps TEXT,
    UNIQUE(from_family_id, to_family_id)
);

-- Skill coverage
CREATE TABLE IF NOT EXISTS skill_coverage (
    id INTEGER PRIMARY KEY,
    source_lang_id INTEGER REFERENCES languages(id),
    target_lang_id INTEGER REFERENCES languages(id),
    skill_name TEXT,
    skill_path TEXT,
    is_bidirectional BOOLEAN DEFAULT FALSE,
    notes TEXT,
    UNIQUE(source_lang_id, target_lang_id)
);

-- IR versions
CREATE TABLE IF NOT EXISTS ir_versions (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_language TEXT NOT NULL,
    source_path TEXT,
    extraction_tool_version TEXT,
    notes TEXT
);

-- IR units
CREATE TABLE IF NOT EXISTS ir_units (
    id INTEGER PRIMARY KEY,
    version_id INTEGER REFERENCES ir_versions(id) ON DELETE CASCADE,
    layer INTEGER NOT NULL,
    unit_type TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    content_json TEXT NOT NULL,
    UNIQUE(version_id, content_hash)
);

-- IR dependencies
CREATE TABLE IF NOT EXISTS ir_dependencies (
    from_unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    to_unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    dependency_type TEXT NOT NULL,
    PRIMARY KEY (from_unit_id, to_unit_id, dependency_type)
);

-- IR annotations
CREATE TABLE IF NOT EXISTS ir_annotations (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    annotation_type TEXT NOT NULL,
    annotation_value TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    source TEXT NOT NULL
);

-- IR gap markers (v1)
CREATE TABLE IF NOT EXISTS ir_gap_markers (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    gap_type TEXT NOT NULL,
    description TEXT,
    source_concept TEXT,
    mitigations TEXT
);

-- IR gap markers (v2)
CREATE TABLE IF NOT EXISTS ir_gap_markers_v2 (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    gap_type TEXT NOT NULL,
    description TEXT,
    source_concept TEXT,
    mitigations TEXT,
    gap_pattern_id TEXT,
    severity TEXT,
    target_concept TEXT,
    decision_point_id TEXT,
    preservation_level INTEGER,
    automation_level TEXT,
    affected_layers TEXT
);

-- IR preservation status
CREATE TABLE IF NOT EXISTS ir_preservation_status (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    current_level INTEGER NOT NULL,
    max_achievable_level INTEGER,
    blocking_gaps TEXT,
    level_0_achieved BOOLEAN,
    level_1_achieved BOOLEAN,
    level_2_achieved BOOLEAN,
    level_3_achieved BOOLEAN
);

-- IR decision resolutions
CREATE TABLE IF NOT EXISTS ir_decision_resolutions (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    decision_point_id TEXT NOT NULL,
    chosen_option TEXT NOT NULL,
    rationale TEXT,
    resolved_by TEXT,
    confidence REAL,
    overridable BOOLEAN DEFAULT TRUE
);

-- IR layers
CREATE TABLE IF NOT EXISTS ir_layers (
    id INTEGER PRIMARY KEY,
    layer_num INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    schema_json TEXT
);

-- Pre-populate IR layers
INSERT OR IGNORE INTO ir_layers (layer_num, name, description) VALUES
    (0, 'Expression IR', 'Full AST representation'),
    (1, 'Data Flow IR', 'Variable bindings and lifetimes'),
    (2, 'Control Flow IR', 'Function signatures and control patterns'),
    (3, 'Type IR', 'Type definitions and relationships'),
    (4, 'Structural IR', 'Modules and packages');

-- Triggers for FTS
CREATE TRIGGER IF NOT EXISTS ir_patterns_ai AFTER INSERT ON ir_patterns BEGIN
    INSERT INTO patterns_fts(rowid, source_pattern, target_pattern, notes)
    VALUES (new.id, new.source_pattern, new.target_pattern, new.notes);
END;

CREATE TRIGGER IF NOT EXISTS ir_patterns_ad AFTER DELETE ON ir_patterns BEGIN
    INSERT INTO patterns_fts(patterns_fts, rowid, source_pattern, target_pattern, notes)
    VALUES ('delete', old.id, old.source_pattern, old.target_pattern, old.notes);
END;
"""

# Test data
TEST_DATA = """
-- Insert test families
INSERT INTO families (name, category, description) VALUES
    ('dynamic_typing', 'typing', 'Languages with dynamic type systems'),
    ('static_typing', 'typing', 'Languages with static type systems'),
    ('gc_managed', 'memory', 'Languages with garbage collection'),
    ('ownership', 'memory', 'Languages with ownership semantics');

-- Insert test languages
INSERT INTO languages (name, version, tier, description) VALUES
    ('Python', '3.11', 1, 'Dynamic, interpreted language'),
    ('Rust', '1.75', 1, 'Systems language with ownership'),
    ('TypeScript', '5.0', 1, 'Typed superset of JavaScript'),
    ('Go', '1.21', 1, 'Simple, concurrent language');

-- Link languages to families
INSERT INTO language_families (language_id, family_id, is_primary) VALUES
    (1, 1, TRUE),   -- Python -> dynamic_typing (primary)
    (1, 3, TRUE),   -- Python -> gc_managed (primary)
    (2, 2, TRUE),   -- Rust -> static_typing (primary)
    (2, 4, TRUE),   -- Rust -> ownership (primary)
    (3, 2, TRUE),   -- TypeScript -> static_typing
    (3, 3, TRUE),   -- TypeScript -> gc_managed
    (4, 2, TRUE),   -- Go -> static_typing
    (4, 3, TRUE);   -- Go -> gc_managed

-- Insert test language features
INSERT INTO language_features (language_id, dimension, feature, value) VALUES
    (1, 'typing', 'static', 'no'),
    (1, 'typing', 'gradual', 'yes'),
    (2, 'typing', 'static', 'yes'),
    (2, 'memory', 'ownership', 'yes');

-- Insert test language syntax
INSERT INTO language_syntax (language_id, pattern_name, pattern) VALUES
    (1, 'function_def', 'def name(params): body'),
    (2, 'function_def', 'fn name(params) -> ReturnType { body }');

-- Insert test patterns
INSERT INTO ir_patterns (skill_name, source_lang, target_lang, pattern_type, category, source_pattern, target_pattern, is_lossy, severity, mitigation, notes) VALUES
    ('convert-python-to-rust', 'Python', 'Rust', 'type_mapping', 'type_system', 'list[T]', 'Vec<T>', FALSE, NULL, NULL, 'Standard list conversion'),
    ('convert-python-to-rust', 'Python', 'Rust', 'type_mapping', 'type_system', 'dict[K, V]', 'HashMap<K, V>', FALSE, NULL, NULL, 'Standard dict conversion'),
    ('convert-python-to-rust', 'Python', 'Rust', 'gap', 'memory', 'dynamic allocation', 'ownership', TRUE, 'structural', 'Use Box or Rc', 'GC to ownership gap'),
    ('convert-python-to-rust', 'Python', 'Rust', 'idiom', 'control_flow', 'for item in iterable:', 'for item in iterator {}', FALSE, NULL, NULL, 'Iterator pattern'),
    ('convert-typescript-to-rust', 'TypeScript', 'Rust', 'type_mapping', 'type_system', 'any', 'Box<dyn Any>', TRUE, 'lossy', 'Avoid any where possible', 'Dynamic typing loss');

-- Insert test semantic gaps
INSERT INTO semantic_gaps (from_family_id, to_family_id, gap_category, concept, description, severity, mitigation, automation_level) VALUES
    (3, 4, 'structural', 'garbage collection', 'GC to ownership conversion', 'high', 'Manual lifetime annotation', 'partial'),
    (1, 2, 'lossy', 'dynamic typing', 'Dynamic to static type loss', 'medium', 'Type annotations', 'partial');

-- Insert test gap patterns
INSERT INTO gap_patterns (name, category, description, from_concept, to_concept, mitigation_strategy) VALUES
    ('TS-001', 'type_system', 'Dynamic to static typing', 'dynamic types', 'static types', 'Add type annotations'),
    ('MM-001', 'memory', 'GC to manual memory', 'garbage collection', 'manual allocation', 'Use smart pointers');

-- Insert test decision points
INSERT INTO decision_points (name, description, options, guidance) VALUES
    ('DP-001', 'Exception to Result', '["result_type", "panic", "option"]', 'Prefer Result for recoverable errors'),
    ('DP-002', 'Collection type', '["vec", "slice", "array"]', 'Choose based on ownership requirements');

-- Insert test conversion difficulty
INSERT INTO family_conversion_difficulty (from_family_id, to_family_id, difficulty, notes) VALUES
    (3, 4, 3, 'GC to ownership is hard'),
    (1, 2, 2, 'Dynamic to static is moderate');
"""


@pytest.fixture
def test_db_path() -> Generator[Path, None, None]:
    """Create a temporary test database.

    Yields:
        Path to the temporary database file.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    # Initialize database
    conn = sqlite3.connect(str(db_path))
    conn.executescript(TEST_SCHEMA)
    conn.executescript(TEST_DATA)
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def test_connection(test_db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Create a test database connection.

    Args:
        test_db_path: Path to the test database.

    Yields:
        SQLite connection to the test database.
    """
    conn = sqlite3.connect(str(test_db_path))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def empty_db_path() -> Generator[Path, None, None]:
    """Create an empty temporary database.

    Yields:
        Path to the empty database file.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    # Initialize with schema only
    conn = sqlite3.connect(str(db_path))
    conn.executescript(TEST_SCHEMA)
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()
