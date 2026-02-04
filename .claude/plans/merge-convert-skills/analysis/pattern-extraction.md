# Pattern Extraction Analysis

Summary of patterns extracted from 49 convert-* skills.

## Extraction Overview

| Metric | Value |
|--------|-------|
| Total patterns extracted | 7,195 |
| Skills processed | 49 |
| Skills failed | 0 |
| Bidirectional skills detected | 42 |
| Unique directions | 91 |

## Pattern Type Distribution

| Type | Count | % | Description |
|------|-------|---|-------------|
| type_mapping | 6,026 | 83.8% | Source → target type equivalences |
| tool | 312 | 4.3% | Tooling recommendations |
| guideline | 299 | 4.2% | Process guidance ("When Converting") |
| idiom | 214 | 3.0% | Code pattern translations |
| scope_boundary | 183 | 2.5% | From "Does NOT Cover" sections |
| error | 84 | 1.2% | Error handling patterns |
| concurrency | 48 | 0.7% | Threading/async model translations |
| negative | 29 | 0.4% | Anti-patterns from "Common Pitfalls" |

### Observations

1. **Type mappings dominate** (84%) - Skills are primarily type mapping references
2. **Idiom coverage varies** - 214 idioms extracted vs 8-10 per skill expected (~400+). Many idioms are in code blocks without structured extraction.
3. **Negative patterns underextracted** - Only 29 vs expected ~5-8 per skill (~250+). Pitfall sections vary in structure.

## Top Skills by Pattern Count

| Skill | Patterns | Direction |
|-------|----------|-----------|
| convert-elixir-roc | 257 | BEAM → ML-FP |
| convert-typescript-rust | 244 | Dynamic → Systems |
| convert-python-haskell | 238 | Dynamic → ML-FP |
| convert-java-rust | 235 | Managed → Systems |
| convert-python-rust | 234 | Dynamic → Systems |
| convert-python-elixir | 227 | Dynamic → BEAM |
| convert-objc-swift | 223 | Apple → Apple |
| convert-fsharp-scala | 210 | ML-FP → ML-FP |
| convert-clojure-fsharp | 204 | LISP → ML-FP |
| convert-python-scala | 198 | Dynamic → ML-FP |

## Bidirectional Detection

42 of 49 skills (86%) were detected as bidirectional based on content markers:
- "bidirectional" keyword
- "both directions" phrase
- "↔" symbol
- Reverse direction mentions

**Note**: The bidirectional-merge.md analysis identified 29 pairs. The extraction detected more due to broad keyword matching. This overcount is acceptable for grounding work - patterns extracted in both directions provide more coverage.

## Pattern Categories (Idioms)

| Category | Count | Examples |
|----------|-------|----------|
| general | 89 | Module Definition, Anonymous Functions |
| type | 48 | Type Inference, Generics |
| control-flow | 27 | Pattern Matching, Iteration |
| function | 19 | Closures, Higher-Order Functions |
| data-structure | 15 | List/Map Operations, Records |
| error | 9 | Result Types, Exception Handling |
| memory | 4 | Ownership, Borrowing |
| concurrency | 3 | Async/Await, Actors |

## Extraction Quality Assessment

### High Confidence Extractions
- **Type mappings**: Tables are well-structured, extraction reliable
- **Tool recommendations**: Tables are consistent
- **Scope boundaries**: "Does NOT Cover" sections are consistent

### Medium Confidence Extractions
- **Guidelines**: "When Converting" format varies (numbered vs bulleted)
- **Idioms**: Pattern/Pillar naming varies, code blocks not fully extracted

### Low Confidence / Underextracted
- **Negative patterns**: Pitfall sections have inconsistent structure
- **Error handling**: Not all skills have dedicated sections
- **Concurrency**: Only present in skills with significant async differences

## Gaps Identified

### Structural Gaps
1. **Code examples not extracted**: Before/After code blocks contain valuable patterns but require LLM-assisted extraction
2. **Prose explanations**: "Why this translation" content is truncated
3. **Nested sections**: Type System Mapping subsections partially captured

### Coverage Gaps
1. **meta-convert-dev patterns**: Parent skill patterns not explicitly inherited
2. **Cross-references**: "See Also" links not extracted
3. **Examples section**: Simple/Medium/Complex examples not parsed

## Recommendations for Phase B (LLM-Assisted)

1. **Extract code block pairs**: Find Before/After patterns in Idiom Translation
2. **Parse pitfalls fully**: Use LLM to extract Problem/Solution from varied formats
3. **Inherit parent patterns**: Explicitly extract from meta-convert-dev
4. **Confidence scoring**: Mark LLM-extracted patterns as medium confidence

## Data Files

| File | Size | Description |
|------|------|-------------|
| `patterns.json` | 2.6 MB | Full pattern data as JSON |
| `patterns.db` | 1.2 MB | SQLite database |
| `patterns.sql` | 1.2 MB | SQL dump for version control |
| `extraction-progress/` | - | Per-skill checkpoint files |

## SQL Queries

### Patterns by family transition
```sql
SELECT
  substr(direction, 1, instr(direction, '-to-') - 1) as source,
  substr(direction, instr(direction, '-to-') + 4) as target,
  COUNT(*) as count
FROM patterns
GROUP BY source, target
ORDER BY count DESC
LIMIT 20;
```

### Type mappings for a specific language pair
```sql
SELECT source_pattern, target_pattern, notes
FROM patterns
WHERE pattern_type = 'type_mapping'
  AND direction = 'python-to-rust'
ORDER BY source_pattern;
```

### All negative patterns
```sql
SELECT skill_name, source_pattern, target_pattern, notes
FROM patterns
WHERE pattern_type = 'negative'
ORDER BY skill_name;
```

## Next Steps

1. **Task 0.2 (Pattern Clustering)**: Analyze extracted patterns to identify universal vs family-specific vs language-specific
2. **Task 0.3 (Gap Analysis)**: Use semantic_gaps and negative patterns to identify conversion limitations
3. **Task 0.4 (Validation)**: Sample 10% of patterns for accuracy review
