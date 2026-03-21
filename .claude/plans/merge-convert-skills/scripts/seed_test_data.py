#!/usr/bin/env python3
"""
Seed test data for Phase 5 validation tooling.

Parses the 10 validated IR patterns from ir-validation.md and inserts them into
the database as sample IR units, linking gap markers to gap_patterns. Verifies
that all Phase 4 views work correctly.

Usage:
    python scripts/seed_test_data.py [--dry-run] [--force] [--verbose]

Options:
    --dry-run   Parse patterns and show what would be created, without database writes
    --force     Clear existing test data before seeding (recommended for clean state)
    --verbose   Enable debug logging

Exit codes:
    0 - Success
    1 - Database error
    2 - Parse error
    3 - View verification failed

Example:
    # First run or re-seed with clean state
    python scripts/seed_test_data.py --force

    # Verify parsing without database changes
    python scripts/seed_test_data.py --dry-run --verbose
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, TypeAlias

# Type aliases
JsonDict: TypeAlias = dict[str, Any]
JsonList: TypeAlias = list[Any]

# Paths
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
DB_PATH = DATA_DIR / "convert-skills.db"
ANALYSIS_DIR = PROJECT_DIR / "analysis"
IR_VALIDATION_PATH = ANALYSIS_DIR / "ir-validation.md"

# Logger setup
logger = logging.getLogger(__name__)


class ExitCode(Enum):
    """Exit codes for the script."""

    SUCCESS = 0
    DATABASE_ERROR = 1
    PARSE_ERROR = 2
    VIEW_VERIFICATION_FAILED = 3


class GapType(Enum):
    """Gap type classification."""

    IMPOSSIBLE = "impossible"
    LOSSY = "lossy"
    STRUCTURAL = "structural"
    IDIOMATIC = "idiomatic"
    RUNTIME = "runtime"
    SEMANTIC = "semantic"


class Severity(Enum):
    """Gap severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AutomationLevel(Enum):
    """Automation level for gap resolution."""

    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


@dataclass
class PatternData:
    """Parsed pattern data from ir-validation.md."""

    pattern_id: str
    category: str
    source_lang: str
    target_lang: str | None
    layers: list[int]
    annotation_kind: str
    gap_type: GapType
    preservation_level: int
    source_code: str
    ir_yaml: dict[str, str]  # layer_name -> yaml content
    annotation_json: JsonDict
    gap_marker_json: JsonDict


@dataclass
class SeededData:
    """Summary of seeded data."""

    ir_versions_created: int = 0
    ir_units_created: int = 0
    gap_markers_created: int = 0
    preservation_statuses_created: int = 0
    decision_resolutions_created: int = 0
    errors: list[str] = field(default_factory=list)


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def parse_yaml_block(block: str) -> str:
    """Extract YAML content from a markdown code block."""
    lines = block.strip().split("\n")
    # Remove ```yaml and ``` markers if present
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1] == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def parse_json_block(block: str) -> JsonDict:
    """Extract and parse JSON content from a markdown code block."""
    lines = block.strip().split("\n")
    # Remove ```json and ``` markers if present
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1] == "```":
        lines = lines[:-1]
    content = "\n".join(lines)
    return json.loads(content)


def extract_code_blocks(text: str, language: str) -> list[str]:
    """Extract all code blocks of a specific language from markdown text."""
    pattern = rf"```{language}\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def parse_pattern_section(section: str) -> PatternData | None:
    """
    Parse a single pattern section from ir-validation.md.

    Args:
        section: The markdown content for one pattern (Pattern N: ...)

    Returns:
        PatternData if parsing succeeds, None otherwise.
    """
    # Extract pattern header
    header_match = re.search(r"## Pattern \d+: (\S+) (.+)", section)
    if not header_match:
        logger.warning("Could not parse pattern header from section")
        return None

    pattern_id = header_match.group(1)
    pattern_name = header_match.group(2)

    # Determine category from pattern ID prefix
    category_map = {
        "TS": "type_system",
        "MM": "memory",
        "EF": "effects",
        "CC": "concurrency",
    }
    prefix = pattern_id.split("-")[0]
    category = category_map.get(prefix, "unknown")

    # Extract source code block
    source_code_match = re.search(
        r"### Source Code \((\w+)\)\n\n```\w+\n(.*?)```",
        section,
        re.DOTALL,
    )
    if not source_code_match:
        logger.warning(f"Could not find source code for pattern {pattern_id}")
        return None

    source_lang = source_code_match.group(1).lower()
    source_code = source_code_match.group(2).strip()

    # Determine target language from pattern description
    target_lang_map = {
        "TS-001": "rust",
        "TS-002": "rust",
        "TS-003": "go",
        "MM-001": "c",
        "MM-002": "rust",
        "MM-004": "elixir",
        "EF-001": "rust",
        "EF-004": "python",
        "CC-001": "java",
        "CC-004": "javascript",
    }
    target_lang = target_lang_map.get(pattern_id)

    # Extract YAML IR blocks
    ir_yaml: dict[str, str] = {}
    yaml_blocks = extract_code_blocks(section, "yaml")
    layer_names = ["layer4", "layer3", "layer2", "layer1", "layer0"]

    for i, block in enumerate(yaml_blocks):
        if i < len(layer_names):
            ir_yaml[layer_names[i]] = block

    # Extract annotation JSON
    annotation_blocks = extract_code_blocks(section, "json")
    annotation_json: JsonDict = {}
    gap_marker_json: JsonDict = {}

    for block in annotation_blocks:
        try:
            parsed = json.loads(block)
            block_id = parsed.get("id", "")
            # Annotations have 'kind' and start with 'ann-'
            if block_id.startswith("ann-"):
                annotation_json = parsed
            # Gap markers have 'gap_type' and start with 'gap-'
            elif block_id.startswith("gap-") or "gap_type" in parsed:
                gap_marker_json = parsed
        except json.JSONDecodeError:
            continue

    # Determine gap type and preservation level from gap marker
    gap_type_str = gap_marker_json.get("gap_type", "structural")
    try:
        gap_type = GapType(gap_type_str)
    except ValueError:
        gap_type = GapType.STRUCTURAL

    preservation_level = gap_marker_json.get("preservation_level", 2)

    # Determine layers from table or content
    layer_info = {
        "TS-001": [1, 2, 3],
        "TS-002": [1, 3],
        "TS-003": [2, 3],
        "MM-001": [1, 2],
        "MM-002": [1, 2],
        "MM-004": [1],
        "EF-001": [2],
        "EF-004": [2],
        "CC-001": [2, 4],
        "CC-004": [2],
    }
    layers = layer_info.get(pattern_id, [2])

    return PatternData(
        pattern_id=pattern_id,
        category=category,
        source_lang=source_lang,
        target_lang=target_lang,
        layers=layers,
        annotation_kind=annotation_json.get("kind", "unknown"),
        gap_type=gap_type,
        preservation_level=preservation_level,
        source_code=source_code,
        ir_yaml=ir_yaml,
        annotation_json=annotation_json,
        gap_marker_json=gap_marker_json,
    )


def parse_ir_validation_md(path: Path) -> list[PatternData]:
    """
    Parse all patterns from ir-validation.md.

    Args:
        path: Path to the ir-validation.md file.

    Returns:
        List of parsed PatternData objects.
    """
    logger.info(f"Parsing patterns from {path}")

    content = path.read_text(encoding="utf-8")

    # Split by pattern sections
    pattern_sections = re.split(r"(?=## Pattern \d+:)", content)

    patterns: list[PatternData] = []
    for section in pattern_sections:
        if not section.strip() or not section.strip().startswith("## Pattern"):
            continue

        pattern = parse_pattern_section(section)
        if pattern:
            patterns.append(pattern)
            logger.debug(f"Parsed pattern: {pattern.pattern_id}")
        else:
            logger.warning("Failed to parse pattern section")

    logger.info(f"Successfully parsed {len(patterns)} patterns")
    return patterns


def seed_ir_version(
    conn: sqlite3.Connection,
    pattern: PatternData,
    dry_run: bool = False,
) -> int:
    """
    Create an IR version record for a pattern.

    Args:
        conn: SQLite connection.
        pattern: Pattern data to seed.
        dry_run: If True, don't actually insert.

    Returns:
        The ID of the created IR version (or simulated ID in dry-run).
    """
    source_path = f"ir-validation.md#{pattern.pattern_id}"
    notes = f"Test pattern {pattern.pattern_id}: {pattern.category}"

    if dry_run:
        logger.info(f"[DRY-RUN] Would create ir_version for {pattern.pattern_id}")
        return 0

    cursor = conn.execute(
        """
        INSERT INTO ir_versions (source_language, source_path, extraction_tool_version, notes)
        VALUES (?, ?, ?, ?)
        """,
        (
            pattern.source_lang,
            source_path,
            "seed_test_data.py/1.0",
            notes,
        ),
    )
    return cursor.lastrowid or 0


def seed_ir_units(
    conn: sqlite3.Connection,
    version_id: int,
    pattern: PatternData,
    dry_run: bool = False,
) -> list[int]:
    """
    Create IR unit records for a pattern.

    Args:
        conn: SQLite connection.
        version_id: The IR version ID.
        pattern: Pattern data containing IR YAML.
        dry_run: If True, don't actually insert.

    Returns:
        List of created IR unit IDs.
    """
    unit_ids: list[int] = []
    layer_mapping = {
        "layer0": 0,
        "layer1": 1,
        "layer2": 2,
        "layer3": 3,
        "layer4": 4,
    }
    type_mapping = {
        "layer0": "expression",
        "layer1": "binding",
        "layer2": "function",
        "layer3": "type",
        "layer4": "module",
    }

    for layer_name, yaml_content in pattern.ir_yaml.items():
        if not yaml_content.strip():
            continue

        layer_num = layer_mapping.get(layer_name, 2)
        unit_type = type_mapping.get(layer_name, "function")

        # Create JSON representation
        content_json = json.dumps(
            {
                "pattern_id": pattern.pattern_id,
                "layer": layer_name,
                "yaml": yaml_content,
                "source_lang": pattern.source_lang,
                "target_lang": pattern.target_lang,
            },
            indent=2,
        )
        content_hash = compute_content_hash(content_json)

        if dry_run:
            logger.info(
                f"[DRY-RUN] Would create ir_unit for {pattern.pattern_id}/{layer_name}"
            )
            unit_ids.append(0)
            continue

        try:
            cursor = conn.execute(
                """
                INSERT INTO ir_units (version_id, layer, unit_type, content_hash, content_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (version_id, layer_num, unit_type, content_hash, content_json),
            )
            unit_ids.append(cursor.lastrowid or 0)
        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate unit for {pattern.pattern_id}/{layer_name}: {e}")

    return unit_ids


def seed_gap_marker(
    conn: sqlite3.Connection,
    unit_id: int,
    pattern: PatternData,
    dry_run: bool = False,
) -> int:
    """
    Create a gap marker v2 record linked to gap_patterns.

    Args:
        conn: SQLite connection.
        unit_id: The IR unit ID to link.
        pattern: Pattern data containing gap marker JSON.
        dry_run: If True, don't actually insert.

    Returns:
        The ID of the created gap marker.
    """
    gap = pattern.gap_marker_json
    if not gap:
        logger.debug(f"No gap marker JSON for {pattern.pattern_id}")
        return 0

    mitigations = json.dumps(gap.get("suggested_mitigations", []))
    affected_layers = json.dumps(pattern.layers)
    decision_point = gap.get("decision_point_id")

    if dry_run:
        logger.info(f"[DRY-RUN] Would create gap_marker for {pattern.pattern_id}")
        return 1  # Return non-zero to indicate success in dry-run

    logger.debug(
        f"Inserting gap marker: unit_id={unit_id}, gap_type={pattern.gap_type.value}, "
        f"pattern_id={pattern.pattern_id}"
    )

    cursor = conn.execute(
        """
        INSERT INTO ir_gap_markers_v2 (
            unit_id, gap_type, description, source_concept, mitigations,
            gap_pattern_id, severity, target_concept, decision_point_id,
            preservation_level, automation_level, affected_layers
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            unit_id,
            pattern.gap_type.value,
            gap.get("description", ""),
            gap.get("source_concept", ""),
            mitigations,
            pattern.pattern_id,
            gap.get("severity", "medium"),
            gap.get("target_concept", ""),
            decision_point,
            pattern.preservation_level,
            gap.get("automation_level", "partial"),
            affected_layers,
        ),
    )
    return cursor.lastrowid or 0


def seed_preservation_status(
    conn: sqlite3.Connection,
    unit_id: int,
    pattern: PatternData,
    dry_run: bool = False,
) -> int:
    """
    Create a preservation status record for tracking conversion levels.

    Args:
        conn: SQLite connection.
        unit_id: The IR unit ID.
        pattern: Pattern data for preservation info.
        dry_run: If True, don't actually insert.

    Returns:
        The ID of the created preservation status.
    """
    current_level = pattern.preservation_level
    # Max achievable is typically current + 1 unless already at max
    max_level = min(current_level + 1, 3)

    # Determine which levels are achieved
    levels_achieved = {
        "level_0": current_level >= 0,
        "level_1": current_level >= 1,
        "level_2": current_level >= 2,
        "level_3": current_level >= 3,
    }

    # Blocking gaps for lossy patterns
    blocking_gaps: list[str] = []
    if pattern.gap_type == GapType.LOSSY:
        blocking_gaps.append(pattern.pattern_id)

    if dry_run:
        logger.info(f"[DRY-RUN] Would create preservation_status for unit {unit_id}")
        return 0

    cursor = conn.execute(
        """
        INSERT INTO ir_preservation_status (
            unit_id, current_level, max_achievable_level, blocking_gaps,
            level_0_achieved, level_1_achieved, level_2_achieved, level_3_achieved
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            unit_id,
            current_level,
            max_level,
            json.dumps(blocking_gaps) if blocking_gaps else None,
            levels_achieved["level_0"],
            levels_achieved["level_1"],
            levels_achieved["level_2"],
            levels_achieved["level_3"],
        ),
    )
    return cursor.lastrowid or 0


def seed_decision_resolution(
    conn: sqlite3.Connection,
    unit_id: int,
    pattern: PatternData,
    dry_run: bool = False,
) -> int:
    """
    Create a decision resolution record if pattern has a decision point.

    Args:
        conn: SQLite connection.
        unit_id: The IR unit ID.
        pattern: Pattern data with decision point info.
        dry_run: If True, don't actually insert.

    Returns:
        The ID of the created decision resolution, or 0 if none.
    """
    decision_point_id = pattern.gap_marker_json.get("decision_point_id")
    if not decision_point_id:
        return 0

    # Default resolution for test data
    option_mapping = {
        "DP-001": "result_type",  # Exception to Result
        "DP-003": "specialized",  # HKT to specialized
        "DP-006": "caller_frees",  # GC to manual
        "DP-010": "promise",  # Channel to async
        "DP-012": "atomic_state",  # Actor to thread
    }
    chosen_option = option_mapping.get(decision_point_id, "default")

    if dry_run:
        logger.info(
            f"[DRY-RUN] Would create decision_resolution for {decision_point_id}"
        )
        return 0

    cursor = conn.execute(
        """
        INSERT INTO ir_decision_resolutions (
            unit_id, decision_point_id, chosen_option, rationale,
            resolved_by, confidence, overridable
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            unit_id,
            decision_point_id,
            chosen_option,
            f"Test data default for {pattern.pattern_id}",
            "default",
            0.85,
            True,
        ),
    )
    return cursor.lastrowid or 0


def verify_views(conn: sqlite3.Connection) -> tuple[bool, list[str]]:
    """
    Verify that all Phase 4 views work correctly.

    Args:
        conn: SQLite connection.

    Returns:
        Tuple of (success, list of error messages).

    Note:
        The v_gaps_by_pattern view may fail on SQLite versions < 3.44.0
        due to GROUP_CONCAT(DISTINCT ...) syntax. This is a known limitation
        and is treated as a warning, not an error.
    """
    errors: list[str] = []
    warnings: list[str] = []

    views = [
        ("v_preservation_summary", "SELECT * FROM v_preservation_summary LIMIT 5", False),
        ("v_gaps_by_pattern", "SELECT * FROM v_gaps_by_pattern", True),  # Known issue
        ("v_decision_audit", "SELECT * FROM v_decision_audit", False),
    ]

    for view_name, query, known_issue in views:
        try:
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            logger.info(f"View {view_name}: {len(rows)} rows returned")
            if len(rows) == 0:
                logger.warning(f"View {view_name} returned no rows")
        except sqlite3.Error as e:
            msg = f"View {view_name} failed: {e}"
            if known_issue and "DISTINCT" in str(e):
                # This is a known SQLite version limitation
                warnings.append(msg)
                logger.warning(
                    f"{msg} (known SQLite < 3.44 limitation, not treated as error)"
                )
            else:
                errors.append(msg)
                logger.error(msg)

    return len(errors) == 0, errors


def clear_test_data(conn: sqlite3.Connection) -> None:
    """
    Clear previously seeded test data from the database.

    Args:
        conn: SQLite connection.
    """
    logger.info("Clearing previously seeded test data...")

    # Clear in order to respect foreign key constraints
    conn.execute("DELETE FROM ir_decision_resolutions")
    conn.execute("DELETE FROM ir_preservation_status")
    conn.execute("DELETE FROM ir_gap_markers_v2")
    conn.execute("DELETE FROM ir_units")
    conn.execute("DELETE FROM ir_versions WHERE source_path LIKE '%ir-validation.md%'")

    conn.commit()
    logger.info("Test data cleared")


def print_summary(seeded: SeededData, conn: sqlite3.Connection | None = None) -> None:
    """Print summary of seeded data."""
    print("\n" + "=" * 60)
    print("SEED TEST DATA SUMMARY")
    print("=" * 60)
    print(f"IR Versions created:          {seeded.ir_versions_created}")
    print(f"IR Units created:             {seeded.ir_units_created}")
    print(f"Gap Markers created:          {seeded.gap_markers_created}")
    print(f"Preservation Statuses:        {seeded.preservation_statuses_created}")
    print(f"Decision Resolutions:         {seeded.decision_resolutions_created}")

    if seeded.errors:
        print(f"\nErrors: {len(seeded.errors)}")
        for error in seeded.errors:
            print(f"  - {error}")

    if conn:
        print("\n" + "-" * 60)
        print("DATABASE STATISTICS")
        print("-" * 60)

        stats_queries = [
            ("ir_versions", "SELECT COUNT(*) FROM ir_versions"),
            ("ir_units", "SELECT COUNT(*) FROM ir_units"),
            ("ir_gap_markers_v2", "SELECT COUNT(*) FROM ir_gap_markers_v2"),
            ("ir_preservation_status", "SELECT COUNT(*) FROM ir_preservation_status"),
            ("ir_decision_resolutions", "SELECT COUNT(*) FROM ir_decision_resolutions"),
        ]

        for table_name, query in stats_queries:
            try:
                cursor = conn.execute(query)
                count = cursor.fetchone()[0]
                print(f"{table_name:30} {count:>6} rows")
            except sqlite3.Error:
                print(f"{table_name:30} [ERROR]")

        # Show sample gap markers
        print("\n" + "-" * 60)
        print("SAMPLE GAP MARKERS (first 5)")
        print("-" * 60)
        try:
            cursor = conn.execute(
                """
                SELECT gap_pattern_id, gap_type, severity, preservation_level
                FROM ir_gap_markers_v2 ORDER BY id LIMIT 5
                """
            )
            rows = cursor.fetchall()
            print(f"{'Pattern ID':<12} {'Gap Type':<12} {'Severity':<10} {'Level'}")
            print("-" * 48)
            for row in rows:
                print(f"{row[0]:<12} {row[1]:<12} {row[2]:<10} {row[3]}")
        except sqlite3.Error as e:
            print(f"[ERROR: {e}]")

    print("=" * 60 + "\n")


def main() -> int:
    """
    Main entry point for the seeding script.

    Returns:
        Exit code indicating success or failure type.
    """
    parser = argparse.ArgumentParser(
        description="Seed test data for Phase 5 validation tooling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing to database",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Clear existing test data before seeding (idempotent)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help=f"Path to SQLite database (default: {DB_PATH})",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Validate paths
    if not IR_VALIDATION_PATH.exists():
        logger.error(f"IR validation file not found: {IR_VALIDATION_PATH}")
        return ExitCode.PARSE_ERROR.value

    if not args.dry_run and not args.db_path.exists():
        logger.error(f"Database not found: {args.db_path}")
        logger.info("Run `python scripts/migrate_to_sqlite.py` first to create the database")
        return ExitCode.DATABASE_ERROR.value

    # Parse patterns
    try:
        patterns = parse_ir_validation_md(IR_VALIDATION_PATH)
    except Exception as e:
        logger.error(f"Failed to parse ir-validation.md: {e}")
        return ExitCode.PARSE_ERROR.value

    if len(patterns) < 10:
        logger.warning(f"Expected 10 patterns, found {len(patterns)}")

    # Seed data
    seeded = SeededData()
    conn: sqlite3.Connection | None = None

    try:
        if not args.dry_run:
            conn = sqlite3.connect(args.db_path)
            conn.row_factory = sqlite3.Row

            # Clear existing test data if --force is set
            if args.force:
                clear_test_data(conn)

        for pattern in patterns:
            logger.info(f"Seeding pattern {pattern.pattern_id}")

            if args.dry_run:
                # In dry-run mode, just count what would be created
                seeded.ir_versions_created += 1
                seeded.ir_units_created += len(
                    [v for v in pattern.ir_yaml.values() if v.strip()]
                )
                if pattern.gap_marker_json:
                    seeded.gap_markers_created += 1
                seeded.preservation_statuses_created += 1
                if pattern.gap_marker_json.get("decision_point_id"):
                    seeded.decision_resolutions_created += 1
                continue

            # Create IR version
            assert conn is not None  # Type narrowing for mypy
            version_id = seed_ir_version(conn, pattern, dry_run=False)
            if version_id:
                seeded.ir_versions_created += 1
            else:
                logger.warning(f"Failed to create ir_version for {pattern.pattern_id}")
                continue

            # Create IR units
            unit_ids = seed_ir_units(conn, version_id, pattern, dry_run=False)
            seeded.ir_units_created += len(unit_ids)

            if not unit_ids:
                logger.warning(f"No units created for {pattern.pattern_id}")
                continue

            # Use first unit for linking
            primary_unit_id = unit_ids[0]

            # Create gap marker
            if pattern.gap_marker_json:
                gap_id = seed_gap_marker(conn, primary_unit_id, pattern, dry_run=False)
                if gap_id:
                    seeded.gap_markers_created += 1
                else:
                    logger.warning(
                        f"Failed to create gap_marker for {pattern.pattern_id}"
                    )

            # Create preservation status
            pres_id = seed_preservation_status(
                conn, primary_unit_id, pattern, dry_run=False
            )
            if pres_id:
                seeded.preservation_statuses_created += 1

            # Create decision resolution if applicable
            if pattern.gap_marker_json.get("decision_point_id"):
                dec_id = seed_decision_resolution(
                    conn, primary_unit_id, pattern, dry_run=False
                )
                if dec_id:
                    seeded.decision_resolutions_created += 1

        if conn:
            conn.commit()

        # Verify views
        if conn and not args.dry_run:
            views_ok, view_errors = verify_views(conn)
            if not views_ok:
                seeded.errors.extend(view_errors)

        # Print summary
        print_summary(seeded, conn)

        # Determine exit code
        if seeded.errors:
            return ExitCode.VIEW_VERIFICATION_FAILED.value

        return ExitCode.SUCCESS.value

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        seeded.errors.append(str(e))
        print_summary(seeded, conn)
        return ExitCode.DATABASE_ERROR.value

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
