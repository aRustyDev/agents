#!/usr/bin/env python3
"""
Migrate YAML/JSON data to SQLite database.

Populates tables defined in schema.sql from:
- families/taxonomy.yaml → families, family_characteristics
- families/dimensions.yaml → family_characteristics
- languages/*.yaml → languages, language_families, language_features, language_syntax, language_gaps
- gap-analysis.json → semantic_gaps
- patterns.db → ir_patterns

Usage:
    python scripts/migrate_to_sqlite.py
"""

import json
import sqlite3
from pathlib import Path
import yaml

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "convert-skills.db"
SCHEMA_PATH = DATA_DIR / "schema.sql"
IR_SCHEMA_PATH = DATA_DIR / "ir-schema.sql"

# Family name normalization
FAMILY_NAMES = {
    "ml-fp": "ML/Functional",
    "beam": "BEAM/Actor",
    "lisp": "Lisp/Symbolic",
    "systems": "Systems",
    "jvm-oop": "JVM/OOP",
    "scripting": "Dynamic/Scripting",
    "gradual-typing": "Gradual Typing",
    "native-compile": "Native Compile",
    "meta-homoiconic": "Meta/Homoiconic",
    "dynamic": "Dynamic",
    "static-oop": "Static OOP",
    "modern-systems": "Modern Systems",
    "legacy": "Legacy",
}


def create_database():
    """Create fresh database with schema."""
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    # Execute base schema
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    # Execute IR schema extensions
    if IR_SCHEMA_PATH.exists():
        with open(IR_SCHEMA_PATH) as f:
            conn.executescript(f.read())

    conn.commit()
    return conn


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def populate_families(conn: sqlite3.Connection):
    """Populate families from taxonomy.yaml."""
    taxonomy = load_yaml(DATA_DIR / "families" / "taxonomy.yaml")

    families = []

    # Paradigm families
    for fid, fdata in taxonomy.get("paradigm_families", {}).items():
        families.append({
            "id": fid,
            "name": fdata.get("name", FAMILY_NAMES.get(fid, fid)),
            "category": "paradigm",
            "description": fdata.get("description", "").strip()
        })

    # Feature families
    for fid, fdata in taxonomy.get("feature_families", {}).items():
        families.append({
            "id": fid,
            "name": fdata.get("name", FAMILY_NAMES.get(fid, fid)),
            "category": "feature",
            "description": fdata.get("description", "").strip()
        })

    # Specialized families
    for fid, fdata in taxonomy.get("specialized_families", {}).items():
        families.append({
            "id": fid,
            "name": fdata.get("name", FAMILY_NAMES.get(fid, fid)),
            "category": "specialized",
            "description": fdata.get("description", "").strip()
        })

    cursor = conn.cursor()
    for fam in families:
        cursor.execute("""
            INSERT OR IGNORE INTO families (name, category, description)
            VALUES (?, ?, ?)
        """, (fam["name"], fam["category"], fam["description"]))

    conn.commit()
    print(f"  Inserted {len(families)} families")
    return {fam["name"]: cursor.lastrowid for fam in families}


def populate_family_characteristics(conn: sqlite3.Connection):
    """Populate family_characteristics from dimensions.yaml."""
    dimensions = load_yaml(DATA_DIR / "families" / "dimensions.yaml")

    cursor = conn.cursor()
    count = 0

    for fid, fdata in dimensions.items():
        if fid == "metadata":
            continue

        # Get family ID
        fname = fdata.get("name", FAMILY_NAMES.get(fid, fid))
        cursor.execute("SELECT id FROM families WHERE name = ?", (fname,))
        row = cursor.fetchone()
        if not row:
            continue
        family_id = row[0]

        # Process each dimension
        for dim in ["typing", "memory", "control", "data", "meta"]:
            if dim not in fdata:
                continue
            dim_data = fdata[dim]

            for key, value in dim_data.items():
                if key == "subtype_variations":
                    continue
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                else:
                    value = str(value)

                cursor.execute("""
                    INSERT OR IGNORE INTO family_characteristics
                    (family_id, dimension, characteristic, value)
                    VALUES (?, ?, ?, ?)
                """, (family_id, dim, key, value))
                count += 1

    conn.commit()
    print(f"  Inserted {count} family characteristics")


def populate_languages(conn: sqlite3.Connection):
    """Populate languages from languages/*.yaml files."""
    lang_dir = DATA_DIR / "languages"
    cursor = conn.cursor()

    lang_count = 0
    feature_count = 0
    syntax_count = 0
    gap_count = 0
    family_link_count = 0

    for yaml_file in sorted(lang_dir.glob("*.yaml")):
        lang = load_yaml(yaml_file)
        if not lang:
            continue

        # Insert language
        popularity = lang.get("popularity") or {}
        so_loved = popularity.get("stackoverflow_loved")
        if so_loved and isinstance(so_loved, str):
            so_loved = so_loved.rstrip("%")
        elif so_loved:
            so_loved = str(so_loved)

        cursor.execute("""
            INSERT OR IGNORE INTO languages
            (name, version, tier, description, popularity_tiobe, popularity_so, github_repos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            lang.get("language", yaml_file.stem),
            lang.get("version"),
            lang.get("tier", 3),
            lang.get("display_name"),
            popularity.get("tiobe_rank"),
            so_loved,
            popularity.get("github_repos"),
        ))
        lang_id = cursor.lastrowid
        lang_count += 1

        # Link to families
        family_info = lang.get("family", {})
        primary = family_info.get("primary")
        if primary:
            fname = FAMILY_NAMES.get(primary, primary)
            cursor.execute("SELECT id FROM families WHERE name = ?", (fname,))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    INSERT OR IGNORE INTO language_families (language_id, family_id, is_primary)
                    VALUES (?, ?, 1)
                """, (lang_id, row[0]))
                family_link_count += 1

        for secondary in family_info.get("secondary", []):
            fname = FAMILY_NAMES.get(secondary, secondary)
            cursor.execute("SELECT id FROM families WHERE name = ?", (fname,))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    INSERT OR IGNORE INTO language_families (language_id, family_id, is_primary)
                    VALUES (?, ?, 0)
                """, (lang_id, row[0]))
                family_link_count += 1

        # Insert features
        features = lang.get("features", {})
        for dim, dim_features in features.items():
            if isinstance(dim_features, dict):
                for feat, val in dim_features.items():
                    if isinstance(val, list):
                        val = ", ".join(str(v) for v in val)
                    elif isinstance(val, bool):
                        val = "true" if val else "false"
                    else:
                        val = str(val)

                    cursor.execute("""
                        INSERT OR IGNORE INTO language_features
                        (language_id, dimension, feature, value)
                        VALUES (?, ?, ?, ?)
                    """, (lang_id, dim, feat, val))
                    feature_count += 1

        # Insert syntax patterns
        syntax = lang.get("syntax", {})
        for pattern_name, pattern_val in syntax.items():
            cursor.execute("""
                INSERT OR IGNORE INTO language_syntax
                (language_id, pattern_name, pattern)
                VALUES (?, ?, ?)
            """, (lang_id, pattern_name, str(pattern_val)))
            syntax_count += 1

        # Insert semantic gaps
        for gap in lang.get("semantic_gaps", []):
            cursor.execute("""
                INSERT INTO language_gaps
                (language_id, gap_description, severity, workaround)
                VALUES (?, ?, ?, ?)
            """, (
                lang_id,
                gap.get("description"),
                gap.get("severity"),
                gap.get("workaround"),
            ))
            gap_count += 1

    conn.commit()
    print(f"  Inserted {lang_count} languages")
    print(f"  Inserted {family_link_count} language-family links")
    print(f"  Inserted {feature_count} language features")
    print(f"  Inserted {syntax_count} syntax patterns")
    print(f"  Inserted {gap_count} language gaps")


def populate_semantic_gaps(conn: sqlite3.Connection):
    """Populate semantic_gaps from gap-analysis.json."""
    gaps_data = load_json(DATA_DIR / "gap-analysis.json")

    cursor = conn.cursor()
    count = 0

    # Map gap types
    gap_type_map = {
        "negative": "structural",
        "human_decision": "semantic",
        "lossy": "lossy",
    }

    for gap in gaps_data.get("gaps", []):
        # Get family IDs for source/target languages
        source_lang = gap.get("source_lang")
        target_lang = gap.get("target_lang")

        # Try to find the language's primary family
        cursor.execute("""
            SELECT f.id FROM families f
            JOIN language_families lf ON f.id = lf.family_id
            JOIN languages l ON l.id = lf.language_id
            WHERE l.name = ? AND lf.is_primary = 1
        """, (source_lang,))
        from_row = cursor.fetchone()

        cursor.execute("""
            SELECT f.id FROM families f
            JOIN language_families lf ON f.id = lf.family_id
            JOIN languages l ON l.id = lf.language_id
            WHERE l.name = ? AND lf.is_primary = 1
        """, (target_lang,))
        to_row = cursor.fetchone()

        from_family_id = from_row[0] if from_row else None
        to_family_id = to_row[0] if to_row else None

        gap_type = gap_type_map.get(gap.get("gap_type"), gap.get("gap_type", "structural"))

        cursor.execute("""
            INSERT INTO semantic_gaps
            (from_family_id, to_family_id, gap_category, concept, description, severity, mitigation, automation_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            from_family_id,
            to_family_id,
            gap_type,
            f"{source_lang} → {target_lang}",
            gap.get("description"),
            gap.get("severity", "medium"),
            gap.get("mitigation"),
            "partial" if gap.get("mitigation") else "none",
        ))
        count += 1

    conn.commit()
    print(f"  Inserted {count} semantic gaps")


def populate_gap_patterns(conn: sqlite3.Connection):
    """Populate gap_patterns with the 54 patterns from Phase 3."""
    patterns = [
        # Type System (16)
        ("TS-001", "type_system", "Dynamic types to static types", "dynamic_type", "static_type"),
        ("TS-002", "type_system", "Nullable to non-null types", "nullable", "option_type"),
        ("TS-003", "type_system", "Higher-kinded types to no HKT", "hkt", "no_hkt"),
        ("TS-004", "type_system", "Structural to nominal typing", "structural_type", "nominal_type"),
        ("TS-005", "type_system", "Duck typing to interfaces", "duck_typing", "interface"),
        ("TS-006", "type_system", "Type inference levels", "no_inference", "full_inference"),
        ("TS-007", "type_system", "Variance handling", "invariant", "covariant"),
        ("TS-008", "type_system", "Generic constraints", "unconstrained", "bounded"),
        ("TS-009", "type_system", "Union types to sealed classes", "union_type", "sealed_class"),
        ("TS-010", "type_system", "Dependent types to runtime checks", "dependent_type", "runtime_check"),
        ("TS-011", "type_system", "Type aliases vs newtypes", "type_alias", "newtype"),
        ("TS-012", "type_system", "Phantom types", "phantom_type", "no_phantom"),
        ("TS-013", "type_system", "GADTs to regular ADTs", "gadt", "adt"),
        ("TS-014", "type_system", "Type families to type params", "type_family", "type_param"),
        ("TS-015", "type_system", "Row polymorphism", "row_poly", "no_row_poly"),
        ("TS-016", "type_system", "Refinement types", "refinement", "no_refinement"),

        # Memory Model (12)
        ("MM-001", "memory", "GC to manual memory", "gc", "manual"),
        ("MM-002", "memory", "GC to ownership", "gc", "ownership"),
        ("MM-003", "memory", "Reference counting to tracing GC", "rc", "tracing_gc"),
        ("MM-004", "memory", "Mutable default to immutable default", "mutable", "immutable"),
        ("MM-005", "memory", "Heap allocation to stack", "heap", "stack"),
        ("MM-006", "memory", "Shared state to message passing", "shared_state", "message_passing"),
        ("MM-007", "memory", "Weak references handling", "weak_ref", "no_weak_ref"),
        ("MM-008", "memory", "Interior mutability", "interior_mut", "no_interior_mut"),
        ("MM-009", "memory", "Copy vs move semantics", "copy", "move"),
        ("MM-010", "memory", "Lifetime annotations", "no_lifetime", "explicit_lifetime"),
        ("MM-011", "memory", "Borrowing rules", "no_borrow", "borrow_checker"),
        ("MM-012", "memory", "Arena allocation", "no_arena", "arena"),

        # Effect System (12)
        ("EF-001", "effects", "Exceptions to Result types", "exception", "result"),
        ("EF-002", "effects", "Implicit effects to explicit", "implicit_effect", "explicit_effect"),
        ("EF-003", "effects", "Algebraic effects to monads", "algebraic_effect", "monad"),
        ("EF-004", "effects", "Monads to direct style", "monad", "direct_style"),
        ("EF-005", "effects", "Effect handlers", "handler", "no_handler"),
        ("EF-006", "effects", "Checked exceptions to unchecked", "checked_exception", "unchecked"),
        ("EF-007", "effects", "IO monad to free IO", "io_monad", "free_io"),
        ("EF-008", "effects", "Continuations", "continuation", "no_continuation"),
        ("EF-009", "effects", "Delimited continuations", "delimited", "no_delimited"),
        ("EF-010", "effects", "Effect rows", "effect_row", "no_effect_row"),
        ("EF-011", "effects", "Resumable exceptions", "resumable", "non_resumable"),
        ("EF-012", "effects", "Effect inference", "effect_inference", "no_effect_inference"),

        # Concurrency (14)
        ("CC-001", "concurrency", "Actors to threads", "actor", "thread"),
        ("CC-002", "concurrency", "Green threads to OS threads", "green_thread", "os_thread"),
        ("CC-003", "concurrency", "CSP channels to queues", "channel", "queue"),
        ("CC-004", "concurrency", "Channels to async/await", "channel", "async_await"),
        ("CC-005", "concurrency", "Supervision trees", "supervisor", "no_supervisor"),
        ("CC-006", "concurrency", "STM to locks", "stm", "lock"),
        ("CC-007", "concurrency", "Async/await to callbacks", "async_await", "callback"),
        ("CC-008", "concurrency", "Futures/Promises models", "future", "promise"),
        ("CC-009", "concurrency", "Parallel collections", "par_collection", "sequential"),
        ("CC-010", "concurrency", "Work stealing", "work_stealing", "no_work_stealing"),
        ("CC-011", "concurrency", "Coroutines to state machines", "coroutine", "state_machine"),
        ("CC-012", "concurrency", "Structured concurrency", "structured", "unstructured"),
        ("CC-013", "concurrency", "Process isolation", "isolated", "shared"),
        ("CC-014", "concurrency", "Message ordering guarantees", "ordered", "unordered"),
    ]

    cursor = conn.cursor()
    for pattern_id, category, description, from_concept, to_concept in patterns:
        cursor.execute("""
            INSERT OR IGNORE INTO gap_patterns
            (name, category, description, from_concept, to_concept)
            VALUES (?, ?, ?, ?, ?)
        """, (pattern_id, category, description, from_concept, to_concept))

    conn.commit()
    print(f"  Inserted {len(patterns)} gap patterns")


def populate_decision_points(conn: sqlite3.Connection):
    """Populate decision_points with the 16 decision points from Phase 3."""
    decision_points = [
        ("DP-001", "Type Annotation Strategy", "How to handle missing type information",
         '["infer_all", "annotate_public", "annotate_all", "use_any"]',
         "Prefer annotate_public for maintainability"),
        ("DP-002", "Generic Constraints", "How to add generic bounds",
         '["minimal_bounds", "maximal_bounds", "infer_bounds"]',
         "Start with minimal bounds, add as needed"),
        ("DP-003", "HKT Elimination", "Strategy for removing higher-kinded types",
         '["defunctionalize", "monomorphize", "use_trait_objects"]',
         "Defunctionalize preserves more type safety"),
        ("DP-004", "Memory Allocation", "Where to allocate data",
         '["stack_prefer", "heap_prefer", "arena", "gc_rely"]',
         "Profile-guided for performance-critical code"),
        ("DP-005", "Lifetime Annotation", "How to annotate lifetimes",
         '["elide_all", "annotate_explicit", "use_owned"]',
         "Start with elision, add explicit as needed"),
        ("DP-006", "Ownership Strategy", "How to handle shared data",
         '["clone_all", "rc_shared", "borrow_prefer", "arena_all"]',
         "Prefer borrowing, clone for simplicity"),
        ("DP-007", "Closure Conversion", "How to convert closures",
         '["box_dyn", "generic_impl", "manual_struct", "fn_pointer"]',
         "Generic impl when possible for performance"),
        ("DP-008", "Macro Expansion", "How to handle macro-heavy code",
         '["expand_inline", "preserve_macro", "convert_to_function", "codegen"]',
         "Expand inline for portability"),
        ("DP-009", "Exception Handling", "How to convert exceptions",
         '["result_type", "panic", "error_code", "option_type"]',
         "Result type for recoverable errors"),
        ("DP-010", "Effect Translation", "How to handle effects",
         '["monad_transform", "direct_io", "effect_handler", "capability"]',
         "Match target language idioms"),
        ("DP-011", "Async Boundary", "Where to place async boundaries",
         '["top_level", "per_io", "manual_annotate", "runtime_decide"]',
         "Top-level async for simplicity"),
        ("DP-012", "Concurrency Model", "Which concurrency model to use",
         '["threads", "async", "actors", "channels"]',
         "Match target language strengths"),
        ("DP-013", "Protocol Adoption", "How to implement protocols/interfaces",
         '["impl_all", "impl_needed", "delegate", "newtype_wrap"]',
         "Implement only what's used"),
        ("DP-014", "Visibility Mapping", "How to map visibility modifiers",
         '["preserve_exact", "widen_to_public", "narrow_to_private", "module_based"]',
         "Preserve exact when possible"),
        ("DP-015", "Package Structure", "How to organize modules",
         '["flat", "nested", "workspace", "single_crate"]',
         "Match source structure initially"),
        ("DP-016", "Build Integration", "How to integrate with build system",
         '["cargo_only", "cmake_integration", "mixed_build", "manual"]',
         "Native build system preferred"),
    ]

    cursor = conn.cursor()
    for dp_id, name, description, options, guidance in decision_points:
        # Store DP-XXX id in the name field with the actual name
        cursor.execute("""
            INSERT OR IGNORE INTO decision_points
            (name, description, options, guidance)
            VALUES (?, ?, ?, ?)
        """, (f"{dp_id}: {name}", description, options, guidance))

    conn.commit()
    print(f"  Inserted {len(decision_points)} decision points")


def populate_ir_patterns(conn: sqlite3.Connection):
    """Migrate patterns from patterns.db to ir_patterns."""
    old_db = DATA_DIR / "patterns.db"
    if not old_db.exists():
        print("  No patterns.db found, skipping ir_patterns migration")
        return

    old_conn = sqlite3.connect(old_db)
    old_cursor = old_conn.cursor()

    cursor = conn.cursor()
    count = 0

    old_cursor.execute("SELECT * FROM patterns")
    for row in old_cursor.fetchall():
        # Parse skill name to get source/target langs
        skill_name = row[1]  # skill_name
        parts = skill_name.replace("convert-", "").split("-")
        if len(parts) >= 2:
            source_lang = parts[0]
            target_lang = parts[1]
        else:
            source_lang = skill_name
            target_lang = "unknown"

        cursor.execute("""
            INSERT INTO ir_patterns
            (skill_name, source_lang, target_lang, pattern_type, category,
             source_pattern, target_pattern, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            skill_name,
            source_lang,
            target_lang,
            row[2],  # pattern_type
            row[6],  # category
            row[3],  # source_pattern
            row[4],  # target_pattern
            row[5],  # notes
        ))
        count += 1

    old_conn.close()
    conn.commit()
    print(f"  Migrated {count} patterns to ir_patterns")


def populate_family_conversion_difficulty(conn: sqlite3.Connection):
    """Populate conversion difficulty matrix."""
    # Difficulty matrix based on Phase 3 severity analysis
    # 1=easy, 2=moderate, 3=hard, 4=very_hard
    difficulties = [
        # (from_family, to_family, difficulty, notes)
        ("ML/Functional", "ML/Functional", 1, "Same family, mostly syntax differences"),
        ("ML/Functional", "BEAM/Actor", 3, "Effect system differences"),
        ("ML/Functional", "Systems", 4, "Memory model fundamental difference"),
        ("ML/Functional", "Dynamic", 2, "Type information lost but structure maps"),
        ("ML/Functional", "JVM/OOP", 3, "Paradigm shift required"),

        ("BEAM/Actor", "ML/Functional", 3, "Need to model actors in pure code"),
        ("BEAM/Actor", "BEAM/Actor", 1, "Same runtime"),
        ("BEAM/Actor", "Systems", 4, "No direct actor support"),
        ("BEAM/Actor", "Dynamic", 2, "Runtime similarities"),

        ("Systems", "ML/Functional", 3, "Memory management abstraction"),
        ("Systems", "Systems", 2, "Similar memory models"),
        ("Systems", "JVM/OOP", 3, "GC transition"),
        ("Systems", "Dynamic", 3, "Memory model hidden"),

        ("Dynamic", "ML/Functional", 3, "Type inference needed"),
        ("Dynamic", "Systems", 4, "Memory management required"),
        ("Dynamic", "Dynamic", 1, "Similar semantics"),
        ("Dynamic", "JVM/OOP", 2, "Add static types"),

        ("JVM/OOP", "ML/Functional", 3, "Paradigm shift"),
        ("JVM/OOP", "Systems", 3, "Memory model change"),
        ("JVM/OOP", "Dynamic", 2, "Remove type constraints"),
        ("JVM/OOP", "JVM/OOP", 1, "Same platform"),
    ]

    cursor = conn.cursor()
    count = 0

    for from_fam, to_fam, difficulty, notes in difficulties:
        cursor.execute("SELECT id FROM families WHERE name = ?", (from_fam,))
        from_row = cursor.fetchone()
        cursor.execute("SELECT id FROM families WHERE name = ?", (to_fam,))
        to_row = cursor.fetchone()

        if from_row and to_row:
            cursor.execute("""
                INSERT OR IGNORE INTO family_conversion_difficulty
                (from_family_id, to_family_id, difficulty, notes)
                VALUES (?, ?, ?, ?)
            """, (from_row[0], to_row[0], difficulty, notes))
            count += 1

    conn.commit()
    print(f"  Inserted {count} conversion difficulty entries")


def print_summary(conn: sqlite3.Connection):
    """Print summary of populated tables."""
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)

    tables = [
        "families", "family_characteristics", "languages", "language_families",
        "language_features", "language_syntax", "language_gaps",
        "semantic_gaps", "gap_patterns", "decision_points",
        "ir_patterns", "family_conversion_difficulty", "ir_layers"
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

    print("="*60)
    print(f"Database created: {DB_PATH}")
    print(f"Size: {DB_PATH.stat().st_size / 1024:.1f} KB")


def main():
    print("Creating database with schema...")
    conn = create_database()

    print("\nPopulating families...")
    populate_families(conn)

    print("\nPopulating family characteristics...")
    populate_family_characteristics(conn)

    print("\nPopulating languages...")
    populate_languages(conn)

    print("\nPopulating semantic gaps...")
    populate_semantic_gaps(conn)

    print("\nPopulating gap patterns...")
    populate_gap_patterns(conn)

    print("\nPopulating decision points...")
    populate_decision_points(conn)

    print("\nPopulating conversion difficulty matrix...")
    populate_family_conversion_difficulty(conn)

    print("\nMigrating patterns from patterns.db...")
    populate_ir_patterns(conn)

    print_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
