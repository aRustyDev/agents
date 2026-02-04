-- Phase 4: IR Schema Extensions
-- Version: 1.0
-- Purpose: Extended tables for Phase 4 IR schema design
-- Dependencies: Must run AFTER schema.sql
-- Generated: 2026-02-04 | Task: ai-f33.9

-- ============================================================================
-- 1. PRESERVATION LEVEL TRACKING
-- ============================================================================
-- Levels: 0=Syntactic, 1=Semantic, 2=Idiomatic, 3=Optimized

CREATE TABLE IF NOT EXISTS ir_preservation_status (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER NOT NULL REFERENCES ir_units(id) ON DELETE CASCADE,
    current_level INTEGER NOT NULL CHECK(current_level >= 0 AND current_level <= 3),
    max_achievable_level INTEGER NOT NULL CHECK(max_achievable_level >= 0 AND max_achievable_level <= 3),
    blocking_gaps TEXT,  -- JSON array of gap IDs
    level_0_achieved BOOLEAN DEFAULT FALSE,
    level_1_achieved BOOLEAN DEFAULT FALSE,
    level_2_achieved BOOLEAN DEFAULT FALSE,
    level_3_achieved BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK(current_level <= max_achievable_level)
);

-- ============================================================================
-- 2. ASYMMETRY METADATA
-- ============================================================================
-- Bidirectional conversion info (e.g., GC->Ownership is 4:1 asymmetric)

CREATE TABLE IF NOT EXISTS ir_asymmetry_metadata (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    source_family TEXT NOT NULL,
    target_family TEXT NOT NULL,
    direction_difficulty INTEGER CHECK(direction_difficulty >= 1 AND direction_difficulty <= 5),
    reverse_difficulty INTEGER CHECK(reverse_difficulty >= 1 AND reverse_difficulty <= 5),
    asymmetry_ratio REAL,
    preserved_in_reverse BOOLEAN DEFAULT TRUE,
    notes TEXT,
    CHECK(direction_difficulty IS NOT NULL OR reverse_difficulty IS NOT NULL)
);

-- ============================================================================
-- 3. DECISION RESOLUTIONS
-- ============================================================================
-- Human decision logging (references DP-001 through DP-016 from Phase 3)

CREATE TABLE IF NOT EXISTS ir_decision_resolutions (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER NOT NULL REFERENCES ir_units(id) ON DELETE CASCADE,
    decision_point_id TEXT NOT NULL,
    chosen_option TEXT NOT NULL,
    rationale TEXT,
    resolved_by TEXT NOT NULL CHECK(resolved_by IN ('human', 'heuristic', 'default')),
    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence REAL CHECK(confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
    overridable BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- 4. EXTENDED GAP MARKERS (ir_gap_markers_v2)
-- ============================================================================
-- Extends base ir_gap_markers with Phase 4 fields for 54 gap patterns

CREATE TABLE IF NOT EXISTS ir_gap_markers_v2 (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    -- Original columns
    gap_type TEXT NOT NULL CHECK(gap_type IN ('impossible', 'lossy', 'structural', 'idiomatic', 'runtime', 'semantic')),
    description TEXT,
    source_concept TEXT,
    mitigations TEXT,  -- JSON array
    -- Phase 4 extensions
    gap_pattern_id TEXT,  -- TS-001, MM-002, CC-001, EF-001, etc.
    severity TEXT CHECK(severity IN ('critical', 'high', 'medium', 'low')),
    target_concept TEXT,
    decision_point_id TEXT,  -- DP-001 through DP-016
    preservation_level INTEGER CHECK(preservation_level >= 0 AND preservation_level <= 3),
    automation_level TEXT CHECK(automation_level IN ('none', 'partial', 'full')),
    affected_layers TEXT,  -- JSON array [0,1,2,3,4]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migrate existing data if present
INSERT OR IGNORE INTO ir_gap_markers_v2 (id, unit_id, gap_type, description, source_concept, mitigations)
SELECT id, unit_id, gap_type, description, source_concept, mitigations
FROM ir_gap_markers WHERE EXISTS (SELECT 1 FROM ir_gap_markers LIMIT 1);

-- ============================================================================
-- 5. INDEXES
-- ============================================================================

-- Preservation status
CREATE INDEX IF NOT EXISTS idx_preservation_unit ON ir_preservation_status(unit_id);
CREATE INDEX IF NOT EXISTS idx_preservation_level ON ir_preservation_status(current_level);
CREATE INDEX IF NOT EXISTS idx_preservation_max ON ir_preservation_status(max_achievable_level);

-- Asymmetry metadata
CREATE INDEX IF NOT EXISTS idx_asymmetry_unit ON ir_asymmetry_metadata(unit_id);
CREATE INDEX IF NOT EXISTS idx_asymmetry_families ON ir_asymmetry_metadata(source_family, target_family);
CREATE INDEX IF NOT EXISTS idx_asymmetry_ratio ON ir_asymmetry_metadata(asymmetry_ratio);

-- Decision resolutions
CREATE INDEX IF NOT EXISTS idx_decisions_unit ON ir_decision_resolutions(unit_id);
CREATE INDEX IF NOT EXISTS idx_decisions_point ON ir_decision_resolutions(decision_point_id);
CREATE INDEX IF NOT EXISTS idx_decisions_resolved_by ON ir_decision_resolutions(resolved_by);

-- Gap markers v2
CREATE INDEX IF NOT EXISTS idx_gaps_v2_unit ON ir_gap_markers_v2(unit_id);
CREATE INDEX IF NOT EXISTS idx_gaps_v2_type ON ir_gap_markers_v2(gap_type);
CREATE INDEX IF NOT EXISTS idx_gaps_v2_pattern ON ir_gap_markers_v2(gap_pattern_id);
CREATE INDEX IF NOT EXISTS idx_gaps_v2_severity ON ir_gap_markers_v2(severity);
CREATE INDEX IF NOT EXISTS idx_gaps_v2_decision ON ir_gap_markers_v2(decision_point_id);

-- ============================================================================
-- 6. VIEWS
-- ============================================================================

-- View: Preservation summary with unit details
CREATE VIEW IF NOT EXISTS v_preservation_summary AS
SELECT
    ps.id, ps.unit_id, iu.unit_type, iu.layer, iv.source_language,
    ps.current_level, ps.max_achievable_level,
    CASE ps.current_level WHEN 0 THEN 'Syntactic' WHEN 1 THEN 'Semantic'
         WHEN 2 THEN 'Idiomatic' WHEN 3 THEN 'Optimized' END AS current_level_name,
    CASE ps.max_achievable_level WHEN 0 THEN 'Syntactic' WHEN 1 THEN 'Semantic'
         WHEN 2 THEN 'Idiomatic' WHEN 3 THEN 'Optimized' END AS max_level_name,
    ps.blocking_gaps, ps.level_0_achieved, ps.level_1_achieved,
    ps.level_2_achieved, ps.level_3_achieved, ps.updated_at
FROM ir_preservation_status ps
JOIN ir_units iu ON ps.unit_id = iu.id
JOIN ir_versions iv ON iu.version_id = iv.id;

-- View: Gaps grouped by pattern
CREATE VIEW IF NOT EXISTS v_gaps_by_pattern AS
SELECT
    gm.gap_pattern_id, gm.gap_type, gm.severity,
    COUNT(*) AS gap_count,
    GROUP_CONCAT(DISTINCT gm.source_concept, '; ') AS source_concepts,
    GROUP_CONCAT(DISTINCT gm.target_concept, '; ') AS target_concepts,
    AVG(gm.preservation_level) AS avg_preservation_level,
    SUM(CASE WHEN gm.automation_level = 'none' THEN 1 ELSE 0 END) AS manual_count,
    SUM(CASE WHEN gm.automation_level = 'partial' THEN 1 ELSE 0 END) AS partial_count,
    SUM(CASE WHEN gm.automation_level = 'full' THEN 1 ELSE 0 END) AS full_count
FROM ir_gap_markers_v2 gm
WHERE gm.gap_pattern_id IS NOT NULL
GROUP BY gm.gap_pattern_id, gm.gap_type, gm.severity
ORDER BY gap_count DESC;

-- View: Decision audit trail
CREATE VIEW IF NOT EXISTS v_decision_audit AS
SELECT
    dr.id, dr.unit_id, iu.unit_type, iv.source_language,
    dr.decision_point_id, dp.name AS decision_name, dp.description AS decision_description,
    dr.chosen_option, dr.rationale, dr.resolved_by, dr.confidence,
    dr.overridable, dr.resolved_at
FROM ir_decision_resolutions dr
JOIN ir_units iu ON dr.unit_id = iu.id
JOIN ir_versions iv ON iu.version_id = iv.id
LEFT JOIN decision_points dp ON dr.decision_point_id = dp.id;

-- ============================================================================
-- 7. TRIGGERS
-- ============================================================================

-- Auto-update timestamp on preservation status change
CREATE TRIGGER IF NOT EXISTS trg_preservation_updated
AFTER UPDATE ON ir_preservation_status
BEGIN
    UPDATE ir_preservation_status SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Auto-calculate asymmetry_ratio on insert
CREATE TRIGGER IF NOT EXISTS trg_asymmetry_ratio_insert
AFTER INSERT ON ir_asymmetry_metadata
WHEN NEW.direction_difficulty IS NOT NULL AND NEW.reverse_difficulty IS NOT NULL AND NEW.asymmetry_ratio IS NULL
BEGIN
    UPDATE ir_asymmetry_metadata
    SET asymmetry_ratio = CAST(NEW.direction_difficulty AS REAL) / CAST(NEW.reverse_difficulty AS REAL)
    WHERE id = NEW.id;
END;

-- Auto-calculate asymmetry_ratio on update
CREATE TRIGGER IF NOT EXISTS trg_asymmetry_ratio_update
AFTER UPDATE OF direction_difficulty, reverse_difficulty ON ir_asymmetry_metadata
WHEN NEW.direction_difficulty IS NOT NULL AND NEW.reverse_difficulty IS NOT NULL
BEGIN
    UPDATE ir_asymmetry_metadata
    SET asymmetry_ratio = CAST(NEW.direction_difficulty AS REAL) / CAST(NEW.reverse_difficulty AS REAL)
    WHERE id = NEW.id;
END;

-- Validate decision_point_id format
CREATE TRIGGER IF NOT EXISTS trg_decision_validate
BEFORE INSERT ON ir_decision_resolutions
WHEN NEW.decision_point_id NOT LIKE 'DP-%'
BEGIN
    SELECT RAISE(ABORT, 'decision_point_id must follow pattern DP-XXX');
END;

-- ============================================================================
-- 8. VERIFICATION QUERIES
-- ============================================================================

-- Verify tables
SELECT 'ir_preservation_status' AS table_name, COUNT(*) AS rows FROM ir_preservation_status
UNION ALL SELECT 'ir_asymmetry_metadata', COUNT(*) FROM ir_asymmetry_metadata
UNION ALL SELECT 'ir_decision_resolutions', COUNT(*) FROM ir_decision_resolutions
UNION ALL SELECT 'ir_gap_markers_v2', COUNT(*) FROM ir_gap_markers_v2;

-- Verify indexes
SELECT name, tbl_name FROM sqlite_master
WHERE type = 'index' AND (name LIKE 'idx_preservation%' OR name LIKE 'idx_asymmetry%'
    OR name LIKE 'idx_decisions%' OR name LIKE 'idx_gaps_v2%')
ORDER BY tbl_name, name;

-- Verify views
SELECT name FROM sqlite_master
WHERE type = 'view' AND name IN ('v_preservation_summary', 'v_gaps_by_pattern', 'v_decision_audit')
ORDER BY name;

-- Verify triggers
SELECT name, tbl_name FROM sqlite_master
WHERE type = 'trigger' AND (name LIKE 'trg_preservation%' OR name LIKE 'trg_asymmetry%' OR name LIKE 'trg_decision%')
ORDER BY name;

-- Schema summary
SELECT 'Phase 4 IR Schema loaded' AS status,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE 'ir_%') AS ir_tables,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%') AS indexes,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name LIKE 'v_%') AS views,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'trg_%') AS triggers;
