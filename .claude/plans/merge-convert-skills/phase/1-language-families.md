# Phase 1: Language Family Research

Comprehensive taxonomy of language families with feature analysis.

## Goal

Create a structured understanding of programming language families to inform IR design and conversion strategies. Documentation serves both AI consumption (skill grounding) and human reference (progressive disclosure).

## Dependencies

- Phase 0: Pattern Extraction (must complete first to inform family validation)

## Deliverables

- [ ] `docs/src/language-families/overview.md` - Comparison matrices
- [ ] `docs/src/language-families/{family}.md` - Per-family documentation (13 families)
- [ ] `data/families.sql` - SQL dump of family data
- [ ] `analysis/family-taxonomy.md` - Taxonomy analysis with Phase 0 cross-references

## Tasks

### 1.0 Family Prioritization

Analyze existing convert-* skills to prioritize family documentation order.

**Input**: Post-merge state (49 skills), Phase 0 pattern clusters

**Process**:
1. Count skills per source/target language
2. Map languages to families
3. Rank families by:
   - Number of skills involving the family
   - Conversion frequency (as source and target)
   - Semantic complexity

**Expected Priority Order** (based on post-merge-state.md):
| Priority | Family | Rationale |
|----------|--------|-----------|
| 1 | Dynamic | Python is source for 11 skills |
| 2 | ML-FP | Target for 8+ skills (Scala, Haskell, F#, Roc, etc.) |
| 3 | Systems | Rust is target for 6 skills; C/C++ conversions |
| 4 | BEAM | Erlang/Elixir/Gleam - 6 skills |
| 5 | Managed-OOP | Java/Kotlin/C# - source languages |
| 6 | LISP | Clojure - 3 skills |
| 7 | Gradual-Typing | TypeScript - cross-cutting concern |
| 8 | Ownership | Rust - cross-cutting concern |
| 9 | Actors | BEAM languages - cross-cutting concern |
| 10 | Logic | No current skills, but future coverage |
| 11 | Array | No current skills, specialized |
| 12 | Dependent-Types | No current skills, research interest |
| 13 | Apple | Objective-C/Swift - 1 skill |

**Output**: `analysis/family-priority.md`

### 1.1 Family Identification

Survey and identify all meaningful language family clusters across multiple dimensions:

| Category | Families | Description |
|----------|----------|-------------|
| **Paradigm** | functional, oop, procedural, logic, array, concatenative | Primary programming model |
| **Typing** | static, dynamic, gradual, dependent, untyped | Type system approach |
| **Memory** | manual, gc, rc, ownership, region-based | Memory management strategy |
| **Execution** | compiled, interpreted, jit, transpiled | How code runs |
| **Effects** | exceptions, results, monadic, algebraic, none | Error/effect handling |
| **Concurrency** | threads, actors, csp, async, green-threads, none | Parallel execution model |
| **Evaluation** | strict, lazy, partial | When expressions evaluate |

### 1.2 Feature Dimensions

For each family, document these dimensions:

```yaml
family:
  name: "{family_name}"
  category: "{paradigm|typing|memory|...}"
  description: "..."
  subtypes: []  # For families with variants (e.g., ML-FP: pure, hybrid)

  characteristics:
    typing:
      strength: dynamic | gradual | static | dependent
      inference: none | local | global | bidirectional
      generics: none | parametric | bounded | higher-kinded
      nullability: nullable | optional | non-null

    memory:
      model: manual | gc | rc | ownership | region-based
      mutability: default-mutable | default-immutable | linear
      allocation: stack | heap | arena | automatic

    control:
      structured: [if-else, loops, match, guards]
      effects: exceptions | result-types | algebraic-effects | monads
      async: callbacks | promises | async-await | green-threads | actors

    data:
      primitives: [int, float, string, bool, ...]
      composites: [arrays, lists, records, tuples, unions, classes]
      abstraction: modules | classes | traits | typeclasses | protocols

    meta:
      macros: none | text | syntactic | hygienic | procedural
      reflection: none | runtime | compile-time | reified-generics
      codegen: none | templates | type-providers | derive

  sources:  # Attribution for characteristics
    - url: "..."
      description: "..."

  examples:
    - language: "..."
      subtype: "..."  # For family variants
      notes: "..."
```

### 1.3 Family Comparison Matrix

Create matrices for cross-family analysis using graduated scale:
- `none` | `limited` | `partial` | `full` | `native`

**Feature × Family Matrix:**

```
                | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
----------------|-------|------|------|---------|---------|---------|-------|
Typing          | full  | none | none | full    | full    | none    | full  |
Type Inference  | full  | none | none | partial | partial | none    | partial|
Memory Safety   | full  | full | full | partial*| full    | full    | full  |
Immutability    | native| native| native| none   | none    | none    | none  |
Pattern Match   | native| native| partial| limited| limited| none    | partial|
First-Class Fn  | native| native| native| full   | partial | native  | full  |
Concurrency     | varies| native| partial| full  | full    | partial | full  |
Macros          | varies| full | native| partial| none    | none    | none  |
```

*partial = Rust has ownership safety, C/C++ do not

**Conversion Difficulty Matrix** (Expert judgment, to be refined after Phase 2-3):

```
FROM → TO       | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
----------------|-------|------|------|---------|---------|---------|-------|
ML-FP           | Easy  | Med  | Med  | Hard    | Med     | Easy    | Med   |
BEAM            | Med   | Easy | Med  | Hard    | Med     | Med     | Hard  |
LISP            | Med   | Med  | Easy | Hard    | Med     | Easy    | Hard  |
Systems         | Hard  | Hard | Hard | Med     | Med     | Hard    | Med   |
Managed         | Med   | Med  | Med  | Med     | Easy    | Med     | Med   |
Dynamic         | Med   | Med  | Easy | Hard    | Med     | Easy    | Med   |
Apple           | Med   | Hard | Hard | Med     | Med     | Med     | Easy  |
```

**Note**: Difficulty ratings are initial expert judgment. Will be updated after:
1. Semantic gap analysis (Phase 3)
2. IR validation (Phase 5)

### 1.4 Family Documentation

For each family, create documentation following progressive disclosure:

```markdown
# {Family Name}

> One-line summary for quick scanning

## Overview
Brief description of the family's core philosophy (2-3 paragraphs).

## Subtypes (if applicable)
| Subtype | Description | Examples |
|---------|-------------|----------|
| pure | ... | Haskell, Elm |
| hybrid | ... | Scala, F# |

## Key Characteristics
<!-- Quick reference for AI grounding -->
- Defining features (bullet list)
- Common patterns
- Typical use cases

## Languages in Family
| Language | Subtype | Notes |
|----------|---------|-------|
| ... | ... | ... |

## Type System
<!-- Detailed for human reference -->
How types work in this family.

## Memory Model
How memory is managed.

## Concurrency Model
How parallelism is handled.

## Common Patterns
Idiomatic patterns in this family.

## Conversion Considerations

### Converting FROM this family
- What's easy to preserve
- What's hard to translate
- Common pitfalls
- Semantic gaps to watch for

### Converting TO this family
- What maps naturally
- What requires restructuring
- Idiomatic patterns to target
- Anti-patterns to avoid

## Cross-References
<!-- Links to Phase 0 patterns -->
- Related pattern clusters from Phase 0
- Relevant convert-* skills

## Sources
- [Source 1](url) - Description
- [Source 2](url) - Description

## See Also
- Related families
- Relevant skills
```

### 1.5 Cross-Reference with Phase 0

After Phase 0 completes, validate family characteristics against extracted patterns.

**Process**:
1. For each pattern cluster from Phase 0:
   - Identify which family characteristics it relates to
   - Note any patterns that don't fit current family definitions
2. For each family:
   - List pattern clusters that validate characteristics
   - Identify gaps where no patterns exist
3. Adjust family definitions based on observed patterns

**Output**: Section in `analysis/family-taxonomy.md`

### 1.6 Validation Sampling

For each documented family, verify accuracy against representative skills.

**Process**:
1. Select 2-3 convert-* skills involving each family
2. Review skill content against family documentation
3. Verify:
   - Type system characteristics match skill type mappings
   - Memory model matches skill ownership/lifetime patterns
   - Conversion difficulty aligns with skill complexity
4. Document discrepancies and adjust

**Validation Matrix**:
| Family | Skills Reviewed | Characteristics Verified | Adjustments |
|--------|-----------------|-------------------------|-------------|
| ML-FP | convert-python-haskell, convert-python-fsharp | ... | ... |
| BEAM | convert-elixir-erlang, convert-python-erlang | ... | ... |
| ... | ... | ... | ... |

**Output**: Section in `analysis/family-taxonomy.md`

## Families to Document

### By Paradigm (7 families)
- [ ] `ml-fp.md` - ML family with subtypes:
  - **pure**: Haskell, Elm, PureScript, Idris
  - **hybrid**: F#, Scala, OCaml, ReasonML, Roc
- [ ] `beam.md` - Erlang, Elixir, Gleam
- [ ] `lisp.md` - Clojure, Common Lisp, Scheme, Racket
- [ ] `systems.md` - Rust, C, C++, Zig
- [ ] `managed-oop.md` - Java, C#, Kotlin
- [ ] `dynamic.md` - Python, Ruby, JavaScript/TypeScript
- [ ] `apple.md` - Objective-C, Swift

### By Notable Feature (4 families)
- [ ] `ownership.md` - Languages with ownership/borrowing (Rust, linear types)
- [ ] `actors.md` - Languages with actor model (BEAM, Akka)
- [ ] `dependent-types.md` - Idris, Agda, Coq
- [ ] `gradual-typing.md` - TypeScript, Python (typed), Hack

### Specialized (2 families)
- [ ] `logic.md` - Prolog, Datalog, Mercury
- [ ] `array.md` - APL, J, K, BQN

## SQL Schema for Families

```sql
-- Language families
CREATE TABLE families (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- paradigm, typing, memory, etc.
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Family subtypes (e.g., ML-FP: pure, hybrid)
CREATE TABLE family_subtypes (
    id INTEGER PRIMARY KEY,
    family_id INTEGER REFERENCES families(id),
    name TEXT NOT NULL,
    description TEXT,
    UNIQUE(family_id, name)
);

-- Family characteristics
CREATE TABLE family_characteristics (
    id INTEGER PRIMARY KEY,
    family_id INTEGER REFERENCES families(id),
    dimension TEXT NOT NULL,  -- typing, memory, control, data, meta
    characteristic TEXT NOT NULL,
    value TEXT NOT NULL,  -- none, limited, partial, full, native
    notes TEXT,
    source_url TEXT,
    source_description TEXT
);

-- Languages (reference table)
CREATE TABLE languages (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Language-family membership (many-to-many)
CREATE TABLE language_families (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    family_id INTEGER REFERENCES families(id),
    subtype_id INTEGER REFERENCES family_subtypes(id),
    is_primary BOOLEAN DEFAULT FALSE,
    notes TEXT,
    UNIQUE(language_id, family_id)
);

-- Family relationships (e.g., "influenced by", "similar to")
CREATE TABLE family_relationships (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    relationship_type TEXT NOT NULL,  -- influenced_by, similar_to, subset_of
    notes TEXT
);

-- Conversion difficulty between families
CREATE TABLE family_conversion_difficulty (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    difficulty TEXT NOT NULL,  -- easy, medium, hard, very_hard
    confidence TEXT NOT NULL,  -- expert_judgment, pattern_analysis, validated
    notes TEXT,
    semantic_gaps TEXT,  -- JSON array of gap descriptions
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cross-reference to Phase 0 pattern clusters
CREATE TABLE family_pattern_clusters (
    id INTEGER PRIMARY KEY,
    family_id INTEGER REFERENCES families(id),
    pattern_cluster_id TEXT NOT NULL,  -- Reference to Phase 0 cluster
    relationship TEXT NOT NULL,  -- validates, contradicts, extends
    notes TEXT
);
```

## Success Criteria

- [ ] All 13 families documented with consistent template
- [ ] Feature matrices created for all dimensions (graduated scale)
- [ ] Conversion difficulty rated for all 49 family pairs (7×7)
- [ ] Each family has 2+ example languages with subtype classification
- [ ] Documentation follows progressive disclosure (AI summary + human detail)
- [ ] Families cover 100% of languages in existing 49 convert-* skills
- [ ] Cross-referenced with Phase 0 pattern clusters
- [ ] Validation sampling completed for high-priority families (top 6)
- [ ] Source attribution for all characteristics

## Effort Estimate

5-7 days:
- Task 1.0 (Prioritization): 0.5 days
- Task 1.1-1.2 (Identification & Dimensions): 1 day
- Task 1.3 (Matrices): 0.5 days
- Task 1.4 (Documentation - 13 families): 3 days
- Task 1.5 (Cross-reference): 0.5 days
- Task 1.6 (Validation): 1 day
- Buffer: 0.5 days

## Output Files

| File | Description |
|------|-------------|
| `analysis/family-priority.md` | Prioritized family list with rationale |
| `docs/src/language-families/overview.md` | Comparison matrices |
| `docs/src/language-families/{family}.md` | Per-family docs (13 files) |
| `data/families.sql` | SQL dump with full schema |
| `analysis/family-taxonomy.md` | Taxonomy analysis with Phase 0 cross-refs |

## Notes

- Conversion difficulty ratings are **expert judgment** initially
- Ratings will be updated after:
  - Phase 3: Semantic Gap Analysis
  - Phase 5: IR Validation
- ML-FP is documented as **one family with subtypes** (pure, hybrid) rather than separate families
- Feature matrices use **graduated scale** (none → limited → partial → full → native)
