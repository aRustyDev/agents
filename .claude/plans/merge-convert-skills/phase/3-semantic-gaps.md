# Phase 3: Semantic Gap Analysis

Identify and classify conversion challenges between language families.

## Goal

Create a comprehensive catalog of semantic gaps that inform IR design and help users understand conversion limitations.

## Dependencies

- Phase 0: Pattern Extraction (extracted gaps from skills)
- Phase 1: Language Families (family classifications)
- Phase 2: Language Survey (language features)

## Deliverables

- [ ] `analysis/semantic-gaps.md` - Comprehensive gap analysis
- [ ] `data/gaps.sql` - SQL dump of gap data
- [ ] Gap severity classification guide

## Tasks

### 3.1 Gap Categories

| Category | Description | Example | Severity |
|----------|-------------|---------|----------|
| **Impossible** | Cannot be translated | Dependent types → simple types | Critical |
| **Lossy** | Information lost | Dynamic → static typing | High |
| **Structural** | Requires restructuring | Exceptions → Results | Medium |
| **Idiomatic** | Style difference | Loops → recursion | Low |
| **Runtime** | Different execution model | GC → manual memory | High |
| **Semantic** | Meaning changes | Null → Option | Medium |

### 3.2 Family Pair Analysis

For each meaningful family pair, document:

```yaml
gap_analysis:
  from_family: "ml-fp"
  to_family: "systems"

  impossible:
    - concept: "Higher-kinded types"
      reason: "No HKT support in target"
      mitigation: "Monomorphize or use trait objects"

  lossy:
    - concept: "Type inference"
      loss: "Must add explicit type annotations"
      automation: "Partial - can infer many cases"

  structural:
    - concept: "Algebraic data types"
      translation: "ADT → struct + enum"
      complexity: "Medium"

  runtime:
    - concept: "Garbage collection"
      translation: "GC → ownership/borrowing"
      complexity: "High - may require redesign"
```

### 3.3 Gap Severity Matrix

Create a matrix of conversion difficulty:

```
FROM → TO       | ML-FP | BEAM | LISP | Systems | Managed | Dynamic |
----------------|-------|------|------|---------|---------|---------|
ML-FP           | -     | 2    | 2    | 4       | 2       | 1       |
BEAM            | 2     | -    | 2    | 4       | 2       | 2       |
LISP            | 2     | 2    | -    | 4       | 2       | 1       |
Systems         | 3     | 4    | 3    | -       | 2       | 3       |
Managed         | 2     | 3    | 2    | 3       | -       | 2       |
Dynamic         | 2     | 2    | 1    | 4       | 2       | -       |

Legend: 1=Easy, 2=Moderate, 3=Hard, 4=Very Hard
```

### 3.4 Common Gap Patterns

Document recurring gap patterns:

#### Type System Gaps

| Gap | From | To | Mitigation |
|-----|------|----|-----------|
| Dynamic → Static | Python, JS | Rust, Java | Type inference + annotations |
| Nullable → Non-null | Java, C# | Rust, Kotlin | Wrap in Option/Optional |
| HKT → No HKT | Haskell, Scala | Go, Rust | Monomorphize or code generation |
| Gradual → Static | TypeScript | Java | Resolve `any` to concrete types |

#### Memory Model Gaps

| Gap | From | To | Mitigation |
|-----|------|----|-----------|
| GC → Manual | Java | C | Add explicit free() calls |
| GC → Ownership | Python | Rust | Restructure for borrowing |
| Shared → Linear | Java | Rust | Clone or restructure |
| Mutable → Immutable | Python | Haskell | Transform to pure functions |

#### Effect System Gaps

| Gap | From | To | Mitigation |
|-----|------|----|-----------|
| Exceptions → Results | Java | Rust | Wrap in Result, propagate with ? |
| Null → Option | Java | Rust | Map null checks to Option |
| Callbacks → Async | JS | Rust | Transform callback chains |
| Monads → Direct | Haskell | Go | Inline monadic operations |

#### Concurrency Gaps

| Gap | From | To | Mitigation |
|-----|------|----|-----------|
| Actors → Threads | Erlang | Java | Use thread pools + queues |
| Threads → Actors | Java | Erlang | Restructure around processes |
| Green → OS threads | Go | C | May need thread pool library |
| CSP → Async | Go | JS | Transform channels to promises |

### 3.5 Semantic Preservation Levels

Define what "correct conversion" means at each level:

```
Level 0: Syntactically valid
  - Code compiles/parses in target language
  - May not run correctly

Level 1: Semantically equivalent
  - Same observable behavior
  - Same inputs produce same outputs
  - May not be idiomatic

Level 2: Idiomatically correct
  - Follows target language conventions
  - Uses appropriate patterns
  - Readable by target language developers

Level 3: Optimized
  - Efficient in target language
  - Uses target's strengths
  - Production-ready performance
```

### 3.6 Human Decision Points

Catalog where human intervention is required:

| Decision Point | Options | Guidance |
|----------------|---------|----------|
| Error handling strategy | Exceptions vs Results | Match target idioms |
| Null handling | Option, assertion, default | Based on semantics |
| Concurrency model | Threads, async, actors | Based on use case |
| Memory management | Clone, borrow, arc | Based on ownership patterns |
| Generic instantiation | Concrete types for HKT | Case-by-case |

## SQL Schema for Gaps

```sql
-- Semantic gaps between families
CREATE TABLE semantic_gaps (
    id INTEGER PRIMARY KEY,
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    gap_category TEXT NOT NULL,  -- impossible, lossy, structural, idiomatic, runtime, semantic
    concept TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL,  -- critical, high, medium, low
    mitigation TEXT,
    automation_level TEXT,  -- none, partial, full
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gap patterns (reusable across family pairs)
CREATE TABLE gap_patterns (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- type_system, memory, effects, concurrency
    description TEXT,
    from_concept TEXT NOT NULL,
    to_concept TEXT NOT NULL,
    mitigation_strategy TEXT,
    example_from TEXT,
    example_to TEXT
);

-- Pattern applications to family pairs
CREATE TABLE gap_pattern_applications (
    id INTEGER PRIMARY KEY,
    pattern_id INTEGER REFERENCES gap_patterns(id),
    from_family_id INTEGER REFERENCES families(id),
    to_family_id INTEGER REFERENCES families(id),
    severity TEXT NOT NULL,
    notes TEXT
);

-- Human decision points
CREATE TABLE decision_points (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    options TEXT NOT NULL,  -- JSON array of options
    guidance TEXT,
    applicable_gaps TEXT  -- JSON array of gap IDs
);

-- Indexes
CREATE INDEX idx_gaps_families ON semantic_gaps(from_family_id, to_family_id);
CREATE INDEX idx_gaps_category ON semantic_gaps(gap_category);
CREATE INDEX idx_gaps_severity ON semantic_gaps(severity);
```

## Success Criteria

- [ ] All family pairs analyzed (at least top 6 families = 30 pairs)
- [ ] Gap severity matrix complete
- [ ] At least 50 gap patterns documented
- [ ] Human decision points cataloged
- [ ] Semantic preservation levels defined

## Effort Estimate

2-3 days

## Output Files

| File | Description |
|------|-------------|
| `analysis/semantic-gaps.md` | Comprehensive gap analysis |
| `data/gaps.sql` | SQL dump of gap data |
| `docs/src/ir-schema/preservation-levels.md` | Preservation level definitions |
