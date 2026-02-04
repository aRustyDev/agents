# Phase 0: Pattern Extraction

Extract patterns from existing 49 convert-* skills to ground IR design in real conversion knowledge.

## Goal

Mine the existing convert-* skills for implicit IR patterns before designing the formal schema. This is grounding work — the patterns extracted here inform later research phases rather than being the final artifact.

## Rationale

We already have 49 convert-* skills with embedded conversion knowledge:

- Type mappings (source type → target type)
- Idiom translations (source pattern → target pattern)
- Semantic gaps (what cannot be directly translated)
- Error handling patterns
- Concurrency patterns
- Negative patterns (what NOT to do)
- Process guidelines (when/how to convert)

This knowledge should inform the IR design rather than designing from first principles.

## Dependencies

None — can start immediately.

## Deliverables

- [ ] `analysis/pattern-extraction.md` - Summary of extracted patterns
- [ ] `data/patterns.sql` - SQL dump of all extracted patterns
- [ ] `data/pattern-clusters.json` - Clustering analysis results
- [ ] Pattern clustering analysis (universal vs family-specific vs language-specific)

## Tasks

### 0.0 Skill Structure Analysis (Preliminary)

Before building extraction tooling, analyze actual skill structures:

1. **Sample 5 representative skills** manually:
   - `convert-python-rust` (Dynamic → Systems)
   - `convert-python-haskell` (Dynamic → ML-FP)
   - `convert-c-cpp` (Systems → Systems)
   - `convert-erlang-elixir` (BEAM → BEAM)
   - `convert-java-kotlin` (Managed → Managed)

2. **Document observed sections**:
   - Quick Reference tables
   - Type System Mapping (nested: Primitives, Collections, etc.)
   - "This Skill Does NOT Cover" (negative patterns)
   - "When Converting" guidelines
   - Error handling sections
   - Async/concurrency sections

3. **Identify parent skill patterns**:
   - Most skills extend `meta-convert-dev`
   - Extract parent patterns as part of each child skill

### 0.1 Pattern Extraction

For each of the 49 convert-* skills, extract patterns including inherited content from `meta-convert-dev`:

```yaml
skill: convert-{source}-{target}
extends: meta-convert-dev  # Track parent skill
is_bidirectional: true|false
direction: "{source}-to-{target}"  # For bidirectional skills, extract twice

patterns:
  type_mappings:
    - source: "{source_type}"
      target: "{target_type}"
      notes: "..."
      lossy: true|false
      confidence: high|medium|low

  idiom_translations:
    - source_pattern: "..."
      target_pattern: "..."
      category: "error-handling|concurrency|data-structure|control-flow|async|memory|..."

  semantic_gaps:
    - concept: "..."
      severity: "impossible|lossy|structural|idiomatic"
      mitigation: "..."

  negative_patterns:  # Things NOT to do
    - antipattern: "..."
      reason: "..."
      instead: "..."  # What to do instead

  guidelines:  # Process guidance
    - when: "..."
      do: "..."
      rationale: "..."

  scope_boundaries:  # From "Does NOT Cover"
    - excluded: "..."
      reason: "..."
      see_instead: "..."  # Reference to other skill

  error_handling:
    - source_approach: "exceptions|result|option|..."
      target_approach: "..."
      translation_rule: "..."

  concurrency:
    - source_model: "threads|actors|async|csp|green-threads|..."
      target_model: "..."
      translation_rule: "..."

  tool_recommendations:
    - tool: "..."
      purpose: "..."
      when_to_use: "..."
```

**Bidirectional Skill Handling**: For skills marked bidirectional (29 of 49), extract patterns twice — once for each direction. Use the `direction` field to distinguish.

### 0.2 Pattern Clustering

Analyze extracted patterns to identify:

| Cluster | Definition | Example |
|---------|------------|---------|
| Universal | Applies to all/most conversions | Function signatures, basic types |
| Family-specific | Applies within a language family | Pattern matching in ML-FP family |
| Language-specific | Unique to a language pair | F# type providers → Roc |
| Inherited | From meta-convert-dev | APTV workflow, testing strategies |

### 0.3 Gap Analysis

From extracted patterns, identify:

1. **Lossy conversions** - What information is lost?
2. **Human decisions** - What requires manual choice?
3. **Impossible conversions** - What cannot be translated?
4. **Negative patterns** - What should explicitly NOT be done?

### 0.4 Validation (Sampling)

Validate extraction quality:

1. Randomly sample 10% of extracted patterns
2. Manual review for accuracy
3. Flag patterns with `confidence: low` for review
4. Document extraction failures or ambiguities

## SQL Schema

Reference the canonical schema at `data/schema.sql`. Key additions for this phase:

```sql
-- Additional fields for pattern extraction
ALTER TABLE ir_patterns ADD COLUMN extends_skill TEXT;  -- parent skill
ALTER TABLE ir_patterns ADD COLUMN is_bidirectional BOOLEAN DEFAULT FALSE;
ALTER TABLE ir_patterns ADD COLUMN direction TEXT;  -- e.g., "python-to-rust"
ALTER TABLE ir_patterns ADD COLUMN confidence TEXT DEFAULT 'high';  -- high, medium, low
```

Extended pattern types:

- `type_mapping` - Type equivalences
- `idiom` - Code pattern translations
- `gap` - Semantic gaps
- `negative` - Anti-patterns (what NOT to do)
- `guideline` - Process guidance
- `scope_boundary` - Explicit exclusions
- `error` - Error handling patterns
- `concurrency` - Concurrency model translations
- `tool` - Tool recommendations

## Extraction Approach

### Hybrid Strategy

Combine structural parsing with LLM-assisted extraction:

**Phase A: Structural Extraction** (automated)

```python
# Parse markdown structure
for skill_path in glob("context/skills/convert-*/SKILL.md"):
    content = read(skill_path)

    # Check if bidirectional
    is_bidirectional = "bidirectional" in content.lower() or
                       "both directions" in content.lower()

    # Extract type mappings from tables
    type_tables = find_markdown_tables(content, header_contains=["Python", "Rust", "source", "target"])
    for table in type_tables:
        for row in table.rows:
            insert_pattern(type="type_mapping", ...)
            if is_bidirectional:
                insert_pattern(type="type_mapping", direction="reverse", ...)

    # Extract negative patterns from "Does NOT Cover"
    not_cover = find_section(content, ["does not cover", "does NOT cover"])
    for item in not_cover.list_items:
        insert_pattern(type="scope_boundary", ...)

    # Extract guidelines from "When Converting"
    guidelines = find_section(content, ["when converting", "conversion tips"])
    for item in guidelines.list_items:
        insert_pattern(type="guideline", ...)
```

**Phase B: LLM-Assisted Extraction** (for prose sections)

For content that can't be structurally parsed:

```
Extract conversion patterns from this skill section.
Output YAML matching this schema:
- pattern_type: type_mapping|idiom|gap|negative|guideline
- source_pattern: ...
- target_pattern: ...
- notes: ...
- confidence: high|medium|low
```

### Progress Tracking

Create checkpoint files to enable incremental extraction:

```
data/extraction-progress/
├── completed.txt      # List of processed skills
├── failed.txt         # Skills with extraction errors
└── {skill-name}.yaml  # Intermediate extraction results
```

## Success Criteria

- [ ] All 49 convert-* skills processed
- [ ] Bidirectional skills extracted for both directions (29 × 2 = 58 direction-specific extractions)
- [ ] Patterns classified into universal/family/language-specific/inherited
- [ ] Negative patterns extracted from "Does NOT Cover" sections
- [ ] 10% sample validated for accuracy
- [ ] Extraction failures documented

## Effort Estimate

4-5 days

- Day 1: Skill structure analysis (Task 0.0)
- Day 2-3: Build extraction tooling and run Phase A
- Day 4: LLM-assisted extraction (Phase B) for prose
- Day 5: Validation, clustering, and documentation

## Output Files

| File | Description |
|------|-------------|
| `analysis/pattern-extraction.md` | Summary and insights |
| `analysis/skill-structure.md` | Observed skill formats |
| `data/patterns.sql` | SQL dump of extracted patterns |
| `data/pattern-clusters.json` | Clustering analysis results |
| `data/extraction-progress/` | Checkpoint files |
