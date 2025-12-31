# Graph Data Pattern (JSON + KuzuDB)

When a project needs graph-structured data for analysis, follow this pattern.

## Overview

```
Store data in JSON → Import to KuzuDB → Analyze with Cypher queries
```

**JSON** is the source of truth. **KuzuDB** is the query engine. **Justfile** is the interface.

## Directory Structure

```
<project>/graphs/
├── data/
│   └── <domain>.json       # Source of truth
├── schema.cypher           # KuzuDB table definitions
├── queries.cypher          # Reusable analysis queries
├── import.py               # JSON → KuzuDB loader (implements recipes)
└── README.md               # Documentation
```

For skills, this lives at `components/skills/<skill>/graphs/`.
For other projects, place at project root or appropriate subdirectory.

---

## Recipe API

Projects using this pattern **must** implement these justfile recipes:

### Required Recipes

| Recipe | Description | Example |
|--------|-------------|---------|
| `kuzu-import` | Import JSON data into KuzuDB | `just kuzu-import` |
| `kuzu-reset` | Drop and recreate database | `just kuzu-reset` |
| `kuzu-status` | Show database info (node/rel counts) | `just kuzu-status` |

### Optional Recipes

| Recipe | Description | Example |
|--------|-------------|---------|
| `kuzu-query <cypher>` | Run ad-hoc Cypher query | `just kuzu-query "MATCH (n) RETURN n LIMIT 5"` |
| `kuzu-query -f <file>` | Run Cypher from file | `just kuzu-query -f queries.cypher` |
| `kuzu-shell` | Open interactive Cypher shell | `just kuzu-shell` |
| `kuzu-export` | Export data back to JSON | `just kuzu-export` |

### Recipe Flags

All recipes should support these flags via environment variables:

| Env Var | Description | Default |
|---------|-------------|---------|
| `KUZU_DB` | Explicit database path | - |
| `KUZU_GLOBAL_DB` | Global database root directory | - |
| `KUZU_NAMESPACE` | Namespace for isolation in global DB | `<project_name>` |

### Database Resolution Order

1. `KUZU_DB` - Explicit path (highest priority)
2. `KUZU_GLOBAL_DB/KUZU_NAMESPACE` - Global with namespace
3. `./graphs/<domain>.kuzu` - Local default

---

## Justfile Module

Include the kuzu module in your project's justfile:

```just
# Import kuzu recipes (local module)
import? "just/kuzu.just"

# Or include from CDN
# mod kuzu "https://just.arusty.dev/modules/kuzu.just"
```

### Reference Implementation

Projects should include a `kuzu.just` file (or equivalent recipes in their main justfile):

```just
# =============================================================================
# KuzuDB Graph Data Recipes
# =============================================================================
# Implements the graph-data-pattern Recipe API
# See: components/rules/graph-data-pattern.md
# =============================================================================

# Configuration (override in parent justfile or via env vars)
graphs_dir := env("KUZU_GRAPHS_DIR", "graphs")
domain := env("KUZU_DOMAIN", "data")
namespace := env("KUZU_NAMESPACE", replace(justfile_directory(), "/", "_"))

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
[group('kuzu')]
kuzu-query *args:
    #!/usr/bin/env python3
    import kuzu, sys
    from pathlib import Path
    args = "{{args}}".split()
    if not args:
        print("Usage: just kuzu-query <query> | -f <file>")
        sys.exit(1)
    if args[0] in ("-f", "--file"):
        query = Path(args[1]).read_text()
    else:
        query = " ".join(args)
    db = kuzu.Database("{{_kuzu_path}}")
    conn = kuzu.Connection(db)
    for stmt in [s.strip() for s in query.split(';') if s.strip()]:
        lines = [l for l in stmt.split('\n') if l.strip() and not l.strip().startswith('//')]
        if lines:
            result = conn.execute('\n'.join(lines))
            while result.has_next():
                print(result.get_next())

# Open interactive Python shell with database connection
[group('kuzu')]
kuzu-shell:
    python -i -c "import kuzu; db=kuzu.Database('{{_kuzu_path}}'); conn=kuzu.Connection(db); print('KuzuDB connected. Use conn.execute(query) to run queries.')"

# Show current configuration
[group('kuzu')]
kuzu-config:
    @echo "graphs_dir:  {{graphs_dir}}"
    @echo "domain:      {{domain}}"
    @echo "namespace:   {{namespace}}"
    @echo "db_path:     {{_kuzu_path}}"
    @echo ""
    @echo "Environment:"
    @echo "  KUZU_DB:         ${KUZU_DB:-<not set>}"
    @echo "  KUZU_GLOBAL_DB:  ${KUZU_GLOBAL_DB:-<not set>}"
    @echo "  KUZU_NAMESPACE:  ${KUZU_NAMESPACE:-<not set>}"
```

---

## Principles

1. **JSON is source of truth** - All data lives in `data/*.json`
2. **Schema is separate** - Node/relationship tables in `schema.cypher`
3. **Queries are reusable** - Named queries in `queries.cypher` with IDs
4. **Import is idempotent** - `just kuzu-reset` recreates the database
5. **Interface is consistent** - Same recipes work across all projects

---

## JSON Schema

The JSON source of truth should follow one of these structures:

### Generic Structure

```json
{
  "nodes": {
    "<NodeType>": [
      {"<primaryKey>": "...", "<property>": "..."}
    ]
  },
  "relationships": [
    {
      "type": "<REL_TYPE>",
      "from": "<NodeType>",
      "to": "<NodeType>",
      "data": [
        {"source": "...", "target": "...", "<property>": "..."}
      ]
    }
  ]
}
```

### Domain-Specific Structure

Use a domain-specific structure that maps cleanly to your graph model.
Document the mapping in your README.

---

## Schema File (schema.cypher)

```cypher
// Node tables with PRIMARY KEY
CREATE NODE TABLE <NodeType> (
    <primaryKey> STRING,
    <property> <TYPE>,
    PRIMARY KEY (<primaryKey>)
);

// Relationship tables
CREATE REL TABLE <REL_TYPE> (
    FROM <NodeType> TO <NodeType>,
    <property> <TYPE>
);
```

---

## Queries File (queries.cypher)

Use consistent naming:

```cypher
// --- <CATEGORY> ---

// Q<NN>_<QUERY_NAME>
// Brief description
MATCH ...
RETURN ...;
```

**Categories**: `BASIC`, `ANALYSIS`, `STATISTICS`, `EXPORT`

---

## Import Script (import.py)

Required CLI interface:

```
python import.py [--db <path>] [--reset] [--namespace <name>]

Options:
  --db <path>        Database directory path
  --reset            Drop and recreate tables
  --namespace <name> Namespace prefix (for global DB)

Environment:
  KUZU_DB            Explicit database path
  KUZU_GLOBAL_DB     Global database root
  KUZU_NAMESPACE     Namespace for isolation
```

### Template

```python
#!/usr/bin/env python3
"""Import <domain>.json into KuzuDB."""
import argparse
import os
from pathlib import Path

DEFAULT_NAMESPACE = "<project_name>"

def get_db_path(args) -> tuple[Path, str]:
    """Resolve database path from args/environment."""
    if args.db:
        return Path(args.db), "explicit"
    if kuzu_db := os.environ.get("KUZU_DB"):
        return Path(kuzu_db), "explicit"
    if global_db := os.environ.get("KUZU_GLOBAL_DB"):
        namespace = args.namespace or os.environ.get("KUZU_NAMESPACE", DEFAULT_NAMESPACE)
        return Path(global_db) / namespace, "global"
    return Path(__file__).parent / "<domain>.kuzu", "local"
```

---

## When to Use This Pattern

**Use when:**
- Data has natural graph relationships
- Queries involve path traversal or pattern matching
- Need to analyze from multiple perspectives
- Relationships are as important as entities

**Don't use when:**
- Data is simple key-value or tabular
- No relationships between entities
- Single-purpose lookups only

---

## Examples

### Skills with Graph Data

```
components/skills/meta-convert-guide/graphs/
├── data/difficulty.json
├── schema.cypher
├── queries.cypher
├── import.py
└── kuzu.just          # or recipes in skill's justfile
```

### Standalone Projects

```
my-project/
├── graphs/
│   ├── data/entities.json
│   ├── schema.cypher
│   ├── queries.cypher
│   └── import.py
├── just/
│   └── kuzu.just      # recipe module
├── justfile           # imports just/kuzu.just
└── ...
```

### Multi-Graph Projects

```
my-project/
├── graphs/
│   ├── users/
│   │   ├── data/users.json
│   │   └── import.py
│   └── products/
│       ├── data/products.json
│       └── import.py
└── justfile
```

With namespace-prefixed recipes:

```just
# Override domain for each graph
kuzu-import-users: (kuzu-import domain="users")
kuzu-import-products: (kuzu-import domain="products")

kuzu-reset-users: (kuzu-reset domain="users")
kuzu-reset-products: (kuzu-reset domain="products")

kuzu-import-all: kuzu-import-users kuzu-import-products
kuzu-reset-all: kuzu-reset-users kuzu-reset-products
```
