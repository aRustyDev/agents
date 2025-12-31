# Graph Data Pattern (JSON + KuzuDB)

When a skill needs graph-structured data for analysis, follow this pattern:

## Structure

```
<skill>/graphs/
├── data/
│   └── <domain>.json       # Source of truth
├── schema.cypher           # KuzuDB table definitions
├── queries.cypher          # Reusable analysis queries
├── import.py               # JSON → KuzuDB loader
├── example.cypher          # Simple query examples (optional)
└── README.md               # Documentation
```

## Principles

1. **JSON is source of truth** - All data lives in `data/*.json`
2. **Schema is separate** - Node/relationship tables defined in `schema.cypher`
3. **Queries are reusable** - Named queries in `queries.cypher` with IDs (Q01, Q02, etc.)
4. **Import is idempotent** - Running `import.py --reset` recreates the database

## KuzuDB Instance

The import script should support both global and local database instances:

| Environment | Database Path |
|-------------|---------------|
| `$KUZU_GLOBAL_DB` set | Use global instance, create namespace for skill |
| `$KUZU_GLOBAL_DB` not set | Use `./graphs/<domain>.kuzu` (project-local) |

### Global Database

When using a global database, the skill should use a namespace prefix to avoid collisions:

```python
# Namespace derived from skill name
namespace = "meta_convert_guide"  # from skill directory name

# Tables become namespaced
# Language → meta_convert_guide_Language
# RUNS_ON → meta_convert_guide_RUNS_ON
```

### Local Database

When `$KUZU_GLOBAL_DB` is not set, create a local database:

```python
db_path = Path(__file__).parent / "<domain>.kuzu"
```

## JSON Schema

The JSON source of truth should follow this general structure:

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

Or a domain-specific structure that maps cleanly to the graph model.

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

## Queries File (queries.cypher)

Use a consistent naming convention:

```cypher
// --- <Category> ---

// Q<NN>_<QUERY_NAME>
// Brief description
MATCH ...
RETURN ...;
```

Categories:
- `BASIC QUERIES` - Simple lookups
- `ANALYSIS` - Domain-specific analysis
- `STATISTICS` - Aggregations and summaries

## Import Script (import.py)

Required features:

```python
#!/usr/bin/env python3
"""
Import <domain>.json into KuzuDB.

Usage:
    python import.py [--db <path>] [--reset] [--namespace <prefix>]

Environment:
    KUZU_GLOBAL_DB    Path to global KuzuDB instance (optional)
"""

import os
from pathlib import Path

def get_db_path(args) -> Path:
    """Determine database path from args or environment."""
    if args.db:
        return args.db
    if global_db := os.environ.get("KUZU_GLOBAL_DB"):
        return Path(global_db)
    return Path(__file__).parent / "<domain>.kuzu"
```

Required CLI flags:
- `--db <path>` - Override database path
- `--reset` - Drop and recreate tables
- `--namespace <prefix>` - Table prefix (for global DB)

## README.md Template

```markdown
# <Domain> Graph

<Brief description>

## Quick Start

\`\`\`bash
pip install kuzu
python import.py --reset
\`\`\`

## Data Model

### Nodes
| Node Type | Properties | Description |
|-----------|------------|-------------|

### Relationships
| Relationship | From | To | Properties |
|--------------|------|-----|------------|

## Example Queries

\`\`\`cypher
<example query>
\`\`\`

## Updating Data

1. Edit \`data/<domain>.json\`
2. Run \`python import.py --reset\`
```

## When to Use This Pattern

Use when:
- Skill data has natural graph relationships
- Queries involve path traversal or pattern matching
- Data needs to be analyzed from multiple perspectives
- Relationships between entities are as important as entities themselves

Don't use when:
- Data is simple key-value or tabular
- No relationships between entities
- Single-purpose lookups only
