# Phase 0: Pattern Extraction

Extract patterns from existing 49 convert-* skills to ground IR design in real conversion knowledge.

## Goal

Mine the existing convert-* skills for implicit IR patterns before designing the formal schema.

## Rationale

We already have 49 convert-* skills with embedded conversion knowledge:
- Type mappings (source type → target type)
- Idiom translations (source pattern → target pattern)
- Semantic gaps (what cannot be directly translated)
- Error handling patterns
- Concurrency patterns

This knowledge should inform the IR design rather than designing from first principles.

## Dependencies

None — can start immediately.

## Deliverables

- [ ] `analysis/pattern-extraction.md` - Summary of extracted patterns
- [ ] `data/patterns.sql` - SQL dump of all extracted patterns
- [ ] Pattern clustering analysis (universal vs family-specific vs language-specific)

## Tasks

### 0.1 Pattern Extraction

For each of the 49 convert-* skills, extract:

```yaml
skill: convert-{source}-{target}
patterns:
  type_mappings:
    - source: "{source_type}"
      target: "{target_type}"
      notes: "..."
      lossy: true|false

  idiom_translations:
    - source_pattern: "..."
      target_pattern: "..."
      category: "error-handling|concurrency|data-structure|control-flow|..."

  semantic_gaps:
    - concept: "..."
      severity: "impossible|lossy|structural|idiomatic"
      mitigation: "..."

  error_handling:
    - source_approach: "exceptions|result|option|..."
      target_approach: "..."
      translation_rule: "..."

  concurrency:
    - source_model: "threads|actors|async|..."
      target_model: "..."
      translation_rule: "..."
```

### 0.2 Pattern Clustering

Analyze extracted patterns to identify:

| Cluster | Definition | Example |
|---------|------------|---------|
| Universal | Applies to all/most conversions | Function signatures, basic types |
| Family-specific | Applies within a language family | Pattern matching in ML-FP family |
| Language-specific | Unique to a language pair | F# type providers → Roc |

### 0.3 Gap Analysis

From extracted patterns, identify:

1. **Lossy conversions** - What information is lost?
2. **Human decisions** - What requires manual choice?
3. **Impossible conversions** - What cannot be translated?

## SQL Schema for Patterns

```sql
-- IR patterns extracted from convert-* skills
CREATE TABLE ir_patterns (
    id INTEGER PRIMARY KEY,
    skill_name TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    pattern_type TEXT NOT NULL,  -- type_mapping, idiom, gap, error, concurrency
    category TEXT,               -- subcategory within type
    source_pattern TEXT NOT NULL,
    target_pattern TEXT,
    is_lossy BOOLEAN DEFAULT FALSE,
    severity TEXT,               -- for gaps: impossible, lossy, structural, idiomatic
    mitigation TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patterns_skill ON ir_patterns(skill_name);
CREATE INDEX idx_patterns_type ON ir_patterns(pattern_type);
CREATE INDEX idx_patterns_langs ON ir_patterns(source_lang, target_lang);

-- FTS for searching patterns
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    source_pattern, target_pattern, notes,
    content='ir_patterns'
);
```

## Extraction Script Approach

```python
# Pseudocode for pattern extraction
for skill_path in glob("context/skills/convert-*/SKILL.md"):
    content = read(skill_path)

    # Extract type mappings from tables
    type_tables = find_markdown_tables(content, header_contains=["source", "target"])
    for table in type_tables:
        for row in table.rows:
            insert_pattern(type="type_mapping", ...)

    # Extract idiom translations from code blocks
    code_blocks = find_paired_code_blocks(content)  # Before/After pairs
    for source_block, target_block in code_blocks:
        insert_pattern(type="idiom", ...)

    # Extract gaps from "Does NOT Cover" or "Limitations" sections
    gaps = find_section(content, ["limitation", "gap", "not cover", "pitfall"])
    for gap in gaps:
        insert_pattern(type="gap", ...)
```

## Success Criteria

- [ ] All 49 convert-* skills processed
- [ ] At least 500 patterns extracted
- [ ] Patterns classified into universal/family/language-specific
- [ ] Top 10 most common patterns identified
- [ ] Semantic gaps documented with severity ratings

## Effort Estimate

2-3 days

## Output Files

| File | Description |
|------|-------------|
| `analysis/pattern-extraction.md` | Summary and insights |
| `data/patterns.sql` | SQL dump of extracted patterns |
| `data/pattern-clusters.json` | Clustering analysis results |
