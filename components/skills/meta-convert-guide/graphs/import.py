#!/usr/bin/env python3
"""
Import difficulty.json into KuzuDB.

Usage:
    python import.py [--db <path>] [--reset]

Options:
    --db <path>   Path to KuzuDB database directory (default: ./difficulty.kuzu)
    --reset       Drop and recreate tables before importing

Requirements:
    pip install kuzu

Example:
    python import.py --reset
    python import.py --db /tmp/difficulty.kuzu
"""

import argparse
import json
import shutil
from pathlib import Path

try:
    import kuzu
except ImportError:
    print("Error: kuzu not installed. Run: pip install kuzu")
    exit(1)


def load_json(json_path: Path) -> dict:
    """Load and parse the difficulty.json file."""
    with open(json_path) as f:
        return json.load(f)


def execute_schema(conn: kuzu.Connection, schema_path: Path) -> None:
    """Execute the schema.cypher file to create tables."""
    with open(schema_path) as f:
        schema = f.read()

    # Split by semicolons and execute each statement
    for statement in schema.split(";"):
        statement = statement.strip()
        # Skip empty statements and comments
        if statement and not statement.startswith("//"):
            try:
                conn.execute(statement)
            except Exception as e:
                # Ignore "table already exists" errors
                if "already exists" not in str(e).lower():
                    print(f"Warning: {e}")


def import_languages(conn: kuzu.Connection, languages: list) -> None:
    """Import language nodes."""
    print(f"Importing {len(languages)} languages...")
    for lang in languages:
        conn.execute(
            """
            CREATE (l:Language {
                name: $name,
                family: $family,
                typeSystem: $typeSystem,
                paradigm: $paradigm,
                memory: $memory,
                concurrency: $concurrency,
                platform: $platform,
                replCentric: $replCentric
            })
            """,
            {
                "name": lang["name"],
                "family": lang["family"],
                "typeSystem": lang["typeSystem"],
                "paradigm": lang["paradigm"],
                "memory": lang["memory"],
                "concurrency": lang["concurrency"],
                "platform": lang["platform"],
                "replCentric": lang.get("replCentric", False),
            },
        )


def import_platforms(conn: kuzu.Connection, platforms: list) -> None:
    """Import platform nodes."""
    print(f"Importing {len(platforms)} platforms...")
    for plat in platforms:
        conn.execute(
            """
            CREATE (p:Platform {
                name: $name,
                description: $description
            })
            """,
            {"name": plat["name"], "description": plat["description"]},
        )


def import_difficulty_levels(conn: kuzu.Connection, levels: list) -> None:
    """Import difficulty level nodes."""
    print(f"Importing {len(levels)} difficulty levels...")
    for level in levels:
        conn.execute(
            """
            CREATE (d:DifficultyLevel {
                name: $name,
                minScore: $minScore,
                maxScore: $maxScore,
                expectedSkillSize: $expectedSkillSize
            })
            """,
            {
                "name": level["name"],
                "minScore": level["minScore"],
                "maxScore": level["maxScore"],
                "expectedSkillSize": level["expectedSkillSize"],
            },
        )


def import_runs_on_relationships(conn: kuzu.Connection, languages: list) -> None:
    """Create RUNS_ON relationships between languages and platforms."""
    print("Creating RUNS_ON relationships...")
    for lang in languages:
        conn.execute(
            """
            MATCH (l:Language {name: $langName}), (p:Platform {name: $platName})
            CREATE (l)-[:RUNS_ON]->(p)
            """,
            {"langName": lang["name"], "platName": lang["platform"]},
        )


def import_conversions(conn: kuzu.Connection, conversions: list) -> None:
    """Import conversion relationships and challenges."""
    print(f"Importing {len(conversions)} conversions...")

    challenge_id = 0
    for conv in conversions:
        source = conv["source"]
        target = conv["target"]
        scores = conv["scores"]

        # Create score relationships
        for rel_type, score_key in [
            ("TYPE_DIFF", "type"),
            ("PARADIGM_DIFF", "paradigm"),
            ("MEMORY_DIFF", "memory"),
            ("CONCURRENCY_DIFF", "concurrency"),
            ("PLATFORM_DIFF", "platform"),
        ]:
            conn.execute(
                f"""
                MATCH (s:Language {{name: $source}}), (t:Language {{name: $target}})
                CREATE (s)-[:{rel_type} {{score: $score}}]->(t)
                """,
                {"source": source, "target": target, "score": scores[score_key]},
            )

        # Create challenges (Mini-Hub pattern)
        for challenge in conv.get("challenges", []):
            challenge_id += 1
            cid = f"{source.lower()}-{target.lower()}-{challenge_id}"

            # Create challenge node
            conn.execute(
                """
                CREATE (c:Challenge {
                    id: $id,
                    text: $text,
                    category: $category
                })
                """,
                {"id": cid, "text": challenge["text"], "category": challenge["category"]},
            )

            # Link source -> challenge -> target
            conn.execute(
                """
                MATCH (s:Language {name: $source}), (c:Challenge {id: $cid})
                CREATE (s)-[:HAS_CHALLENGE]->(c)
                """,
                {"source": source, "cid": cid},
            )
            conn.execute(
                """
                MATCH (c:Challenge {id: $cid}), (t:Language {name: $target})
                CREATE (c)-[:WHEN_CONVERTING_TO]->(t)
                """,
                {"cid": cid, "target": target},
            )


def reset_database(db_path: Path) -> None:
    """Remove the database directory to start fresh."""
    if db_path.exists():
        print(f"Removing existing database at {db_path}...")
        shutil.rmtree(db_path)


def main():
    parser = argparse.ArgumentParser(description="Import difficulty.json into KuzuDB")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).parent / "difficulty.kuzu",
        help="Path to KuzuDB database directory",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate tables before importing",
    )
    args = parser.parse_args()

    # Paths
    script_dir = Path(__file__).parent
    json_path = script_dir / "data" / "difficulty.json"
    schema_path = script_dir / "schema.cypher"

    # Validate files exist
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        exit(1)
    if not schema_path.exists():
        print(f"Error: {schema_path} not found")
        exit(1)

    # Reset database if requested
    if args.reset:
        reset_database(args.db)

    # Connect to KuzuDB
    print(f"Connecting to KuzuDB at {args.db}...")
    db = kuzu.Database(str(args.db))
    conn = kuzu.Connection(db)

    # Load JSON data
    data = load_json(json_path)

    # Execute schema
    print("Creating schema...")
    execute_schema(conn, schema_path)

    # Import data
    import_languages(conn, data["languages"])
    import_platforms(conn, data["platforms"])
    import_difficulty_levels(conn, data["difficultyLevels"])
    import_runs_on_relationships(conn, data["languages"])
    import_conversions(conn, data["conversions"])

    # Summary
    result = conn.execute("MATCH (n) RETURN count(n) AS nodeCount")
    node_count = result.get_next()[0]
    result = conn.execute("MATCH ()-[r]->() RETURN count(r) AS relCount")
    rel_count = result.get_next()[0]

    print(f"\nImport complete!")
    print(f"  Nodes: {node_count}")
    print(f"  Relationships: {rel_count}")
    print(f"  Database: {args.db}")


if __name__ == "__main__":
    main()
