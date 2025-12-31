# Language Conversion Difficulty Graph

Graph-based analysis of language conversion difficulty using KuzuDB.

## Structure

```
graphs/
├── data/
│   └── difficulty.json     # Source of truth (17 languages, 77 conversions)
├── schema.cypher           # KuzuDB table definitions
├── queries.cypher          # Reusable analysis queries
├── import.py               # JSON → KuzuDB loader
└── README.md               # This file
```

## Quick Start

```bash
# Install KuzuDB
pip install kuzu

# Import data
python import.py --reset

# Query the database
python -c "
import kuzu
db = kuzu.Database('./difficulty.kuzu')
conn = kuzu.Connection(db)
result = conn.execute('''
    MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language)
    RETURN s.name, e.name, t.score
    LIMIT 5
''')
while result.has_next():
    print(result.get_next())
"
```

## Data Model

### Nodes

| Node Type | Properties | Description |
|-----------|------------|-------------|
| `Language` | name, family, typeSystem, paradigm, memory, concurrency, platform, replCentric | Programming language |
| `Platform` | name, description | Runtime platform |
| `DifficultyLevel` | name, minScore, maxScore, expectedSkillSize | Difficulty category |
| `Challenge` | id, text, category | Specific conversion challenge |

### Relationships

| Relationship | From | To | Properties | Description |
|--------------|------|-----|------------|-------------|
| `RUNS_ON` | Language | Platform | - | Language runs on platform |
| `TYPE_DIFF` | Language | Language | score (0-2) | Type system difficulty |
| `PARADIGM_DIFF` | Language | Language | score (0-2) | Paradigm shift difficulty |
| `MEMORY_DIFF` | Language | Language | score (0-2) | Memory model difficulty |
| `CONCURRENCY_DIFF` | Language | Language | score (0-2) | Concurrency model difficulty |
| `PLATFORM_DIFF` | Language | Language | score (0-2) | Platform migration difficulty |
| `HAS_CHALLENGE` | Language | Challenge | - | Source language has challenge |
| `WHEN_CONVERTING_TO` | Challenge | Language | - | Challenge applies to target |

### Difficulty Calculation

```
totalScore = TYPE + PARADIGM + MEMORY + CONCURRENCY + PLATFORM
           (each 0-2, total 0-10)

Easy:   0-2   (200-400 lines skill)
Medium: 3-5   (400-800 lines skill)
Hard:   6-8   (800-1200 lines skill)
Expert: 9-10  (1200+ lines skill)
```

## Example Queries

### Get all Python conversions

```cypher
MATCH (s:Language {name: 'Python'})-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
RETURN e.name AS target,
       t.score + p.score + m.score + c.score + pl.score AS totalScore
ORDER BY totalScore;
```

### Find hardest conversions

```cypher
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source, e.name AS target,
     t.score + p.score + m.score + c.score + pl.score AS total
WHERE total >= 6
RETURN source, target, total
ORDER BY total DESC;
```

### Get challenges for a conversion

```cypher
MATCH (s:Language {name: 'Python'})-[:HAS_CHALLENGE]->(c:Challenge)
      -[:WHEN_CONVERTING_TO]->(t:Language {name: 'Rust'})
RETURN c.text, c.category;
```

See `queries.cypher` for more examples.

## JSON Schema

The source of truth (`data/difficulty.json`) contains:

- **languages**: Array of language objects with properties
- **platforms**: Array of runtime platforms
- **difficultyLevels**: Difficulty category definitions
- **conversions**: Array of conversion objects with:
  - source/target language names
  - scores object (type, paradigm, memory, concurrency, platform)
  - challenges array (text, category)

## Updating Data

1. Edit `data/difficulty.json`
2. Re-run import: `python import.py --reset`
3. Query updated data

## Dependencies

- Python 3.8+
- KuzuDB (`pip install kuzu`)
