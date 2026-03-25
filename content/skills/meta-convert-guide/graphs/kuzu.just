# =============================================================================
# KuzuDB Graph Data Recipes
# =============================================================================
# Implements the graph-data-pattern Recipe API
# See: content/rules/graph-data-pattern.md
# =============================================================================

# Configuration
graphs_dir := justfile_directory()
domain := "difficulty"
namespace := env("KUZU_NAMESPACE", "meta_convert_guide")

# Database path resolution
_kuzu_explicit := env("KUZU_DB", "")
_kuzu_global := env("KUZU_GLOBAL_DB", "")
_kuzu_local := graphs_dir / domain + ".kuzu"
_kuzu_path := if _kuzu_explicit != "" {
    _kuzu_explicit
} else if _kuzu_global != "" {
    _kuzu_global / namespace
} else {
    _kuzu_local
}

# -----------------------------------------------------------------------------
# Required Recipes
# -----------------------------------------------------------------------------

# Import JSON data into KuzuDB
[group('kuzu')]
kuzu-import:
    python {{graphs_dir}}/import.py --db "{{_kuzu_path}}"

# Drop and recreate database, then import
[group('kuzu')]
kuzu-reset:
    python {{graphs_dir}}/import.py --db "{{_kuzu_path}}" --reset

# Show database status (node/relationship counts)
[group('kuzu')]
kuzu-status:
    #!/usr/bin/env python3
    import kuzu
    from pathlib import Path
    db_path = Path("{{_kuzu_path}}")
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        print("Run: just kuzu-reset")
        exit(1)
    db = kuzu.Database(str(db_path))
    conn = kuzu.Connection(db)
    nodes = conn.execute("MATCH (n) RETURN count(n)").get_next()[0]
    rels = conn.execute("MATCH ()-[r]->() RETURN count(r)").get_next()[0]
    print(f"Database: {db_path}")
    print(f"Nodes: {nodes}")
    print(f"Relationships: {rels}")

# -----------------------------------------------------------------------------
# Optional Recipes
# -----------------------------------------------------------------------------

# Run Cypher query (string or file)
# Usage: just kuzu-query "MATCH (n) RETURN n"
#        just kuzu-query -f queries.cypher
#        just kuzu-query --file queries.cypher
[group('kuzu')]
kuzu-query *args:
    #!/usr/bin/env python3
    import kuzu
    import sys
    from pathlib import Path

    args = "{{args}}".split()
    if not args:
        print("Usage: just kuzu-query <query>")
        print("       just kuzu-query -f <file>")
        print("       just kuzu-query --file <file>")
        sys.exit(1)

    # Check for file flag
    if args[0] in ("-f", "--file"):
        if len(args) < 2:
            print("Error: -f/--file requires a filename")
            sys.exit(1)
        file_path = Path(args[1])
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        query = file_path.read_text()
    else:
        query = " ".join(args)

    db = kuzu.Database("{{_kuzu_path}}")
    conn = kuzu.Connection(db)

    # Split by semicolons for multiple statements
    statements = [s.strip() for s in query.split(';') if s.strip()]

    for stmt in statements:
        # Skip comment-only statements
        lines = [l for l in stmt.split('\n') if l.strip() and not l.strip().startswith('//')]
        if not lines:
            continue

        clean_stmt = '\n'.join(lines)
        try:
            result = conn.execute(clean_stmt)
            while result.has_next():
                print(result.get_next())
        except Exception as e:
            print(f"Error: {e}")

# Open interactive Python shell with database connection
[group('kuzu')]
kuzu-shell:
    python -i -c "import kuzu; db=kuzu.Database('{{_kuzu_path}}'); conn=kuzu.Connection(db); print('KuzuDB connected. Use conn.execute(query) to run queries.')"

# Show current configuration
[group('kuzu')]
kuzu-config:
    @echo "Configuration:"
    @echo "  graphs_dir:  {{graphs_dir}}"
    @echo "  domain:      {{domain}}"
    @echo "  namespace:   {{namespace}}"
    @echo "  db_path:     {{_kuzu_path}}"
    @echo ""
    @echo "Environment:"
    @echo "  KUZU_DB:         ${KUZU_DB:-<not set>}"
    @echo "  KUZU_GLOBAL_DB:  ${KUZU_GLOBAL_DB:-<not set>}"
    @echo "  KUZU_NAMESPACE:  ${KUZU_NAMESPACE:-<not set>}"

# -----------------------------------------------------------------------------
# Analysis Recipes (domain-specific)
# -----------------------------------------------------------------------------

# Find easiest conversions
[group('kuzu')]
kuzu-easy-conversions:
    #!/usr/bin/env python3
    import kuzu
    db = kuzu.Database("{{_kuzu_path}}")
    conn = kuzu.Connection(db)
    result = conn.execute("""
        MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
              (s)-[p:PARADIGM_DIFF]->(e),
              (s)-[m:MEMORY_DIFF]->(e),
              (s)-[c:CONCURRENCY_DIFF]->(e),
              (s)-[pl:PLATFORM_DIFF]->(e)
        WITH s.name AS source, e.name AS target,
             t.score + p.score + m.score + c.score + pl.score AS total
        WHERE total <= 2
        RETURN source, target, total
        ORDER BY total, source, target
    """)
    print("Easy Conversions (score <= 2):")
    print("-" * 40)
    while result.has_next():
        row = result.get_next()
        print(f"  {row[0]} → {row[1]} (score: {row[2]})")

# Find hardest conversions
[group('kuzu')]
kuzu-hard-conversions:
    #!/usr/bin/env python3
    import kuzu
    db = kuzu.Database("{{_kuzu_path}}")
    conn = kuzu.Connection(db)
    result = conn.execute("""
        MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
              (s)-[p:PARADIGM_DIFF]->(e),
              (s)-[m:MEMORY_DIFF]->(e),
              (s)-[c:CONCURRENCY_DIFF]->(e),
              (s)-[pl:PLATFORM_DIFF]->(e)
        WITH s.name AS source, e.name AS target,
             t.score + p.score + m.score + c.score + pl.score AS total
        WHERE total >= 6
        RETURN source, target, total
        ORDER BY total DESC
    """)
    print("Hard Conversions (score >= 6):")
    print("-" * 40)
    while result.has_next():
        row = result.get_next()
        print(f"  {row[0]} → {row[1]} (score: {row[2]})")

# Get conversion details for a specific pair
[group('kuzu')]
kuzu-conversion source target:
    #!/usr/bin/env python3
    import kuzu
    db = kuzu.Database("{{_kuzu_path}}")
    conn = kuzu.Connection(db)
    result = conn.execute("""
        MATCH (s:Language {name: $source})-[t:TYPE_DIFF]->(e:Language {name: $target}),
              (s)-[p:PARADIGM_DIFF]->(e),
              (s)-[m:MEMORY_DIFF]->(e),
              (s)-[c:CONCURRENCY_DIFF]->(e),
              (s)-[pl:PLATFORM_DIFF]->(e)
        RETURN t.score, p.score, m.score, c.score, pl.score,
               t.score + p.score + m.score + c.score + pl.score
    """, {"source": "{{source}}", "target": "{{target}}"})
    if result.has_next():
        row = result.get_next()
        print(f"{{source}} → {{target}}")
        print("-" * 40)
        print(f"  Type:        {row[0]}")
        print(f"  Paradigm:    {row[1]}")
        print(f"  Memory:      {row[2]}")
        print(f"  Concurrency: {row[3]}")
        print(f"  Platform:    {row[4]}")
        print(f"  Total:       {row[5]}")
        # Get challenges
        challenges = conn.execute("""
            MATCH (s:Language {name: $source})-[:HAS_CHALLENGE]->(c:Challenge)
                  -[:WHEN_CONVERTING_TO]->(t:Language {name: $target})
            RETURN c.category, c.text
        """, {"source": "{{source}}", "target": "{{target}}"})
        print("\nChallenges:")
        while challenges.has_next():
            ch = challenges.get_next()
            print(f"  [{ch[0]}] {ch[1]}")
    else:
        print(f"No conversion found: {{source}} → {{target}}")
