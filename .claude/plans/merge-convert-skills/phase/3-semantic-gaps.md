# Phase 3: Semantic Gap Analysis

Identify and classify conversion challenges between language families.

## Goal

Create a comprehensive catalog of semantic gaps that inform IR design and help users understand conversion limitations.

## Dependencies

- Phase 0: Pattern Extraction (extracted gaps from skills)
- Phase 1: Language Families (family classifications)
- Phase 2: Language Survey (language features)

## Input Data Sources

Phase 3 builds on existing extracted data:

| Source | Location | Contents |
|--------|----------|----------|
| Phase 0 Gaps | `analysis/clustering-and-gaps.md` | 320 gaps (29 negative, 183 human_decision, 108 lossy) |
| Pattern Database | `data/patterns.sql` | 7,195 pattern instances across 49 skills |
| Language Profiles | `data/languages/*.yaml` | 29 profiles with `semantic_gaps` fields |
| Base Schema | `data/schema.sql` | Tables: `semantic_gaps`, `gap_patterns`, `decision_points` |
| SQL Extensions | `data/languages.sql` | Language ecosystem and relationship data |

**Key insight**: Phase 0 found 0 "impossible" gaps in existing skills. Phase 3 should validate this finding and identify any impossible gaps not yet documented.

## Deliverables

- [ ] `analysis/semantic-gaps.md` - Comprehensive gap analysis with family pairs
- [ ] `data/gaps.sql` - INSERT statements to populate existing schema tables
- [ ] `docs/src/ir-schema/preservation-levels.md` - Preservation level definitions
- [ ] Gap severity classification guide (in semantic-gaps.md)

## Language Families (from Phase 2)

Phase 3 analyzes gaps between these 9 canonical families:

| Family | Languages | Key Characteristics |
|--------|-----------|---------------------|
| **ML-FP** | Scala, Haskell, F#, Elm, Roc, Gleam | Strong typing, immutability, ADTs |
| **BEAM** | Elixir, Erlang | Actor model, hot code reload |
| **LISP** | Clojure, Common Lisp, Scheme | Homoiconicity, macros |
| **Systems** | Rust, C, C++, Go, Zig | Manual/ownership memory, low-level |
| **Dynamic** | Python, TypeScript, JavaScript, Ruby | Runtime typing, duck typing |
| **Managed-OOP** | Java, Kotlin | GC, class-based OOP, JVM |
| **Apple** | Swift, Objective-C | ARC, protocols/categories |
| **Logic** | Prolog | Unification, backtracking |
| **Procedural** | COBOL, Fortran, Pascal, Ada | Structured, imperative |

## Tasks

### 3.1 Classify Existing Phase 0 Gaps

Reclassify the 320 gaps from Phase 0 into the 6-category system:

| Category | Description | Example | Severity | Phase 0 Source |
|----------|-------------|---------|----------|----------------|
| **Impossible** | Cannot be translated | Dependent types → simple types | Critical | Validate: 0 found |
| **Lossy** | Information lost | Dynamic → static typing | High | 108 lossy gaps |
| **Structural** | Requires restructuring | Exceptions → Results | Medium | Extract from patterns |
| **Idiomatic** | Style difference | Loops → recursion | Low | Extract from patterns |
| **Runtime** | Different execution model | GC → manual memory | High | Extract from patterns |
| **Semantic** | Meaning changes | Null → Option | Medium | 29 negative gaps |

**Human decision gaps** (183): Map to appropriate category + flag `requires_human_decision: true`

### 3.2 Family Pair Analysis

For each of the 72 directed family pairs (9 × 8), document gaps:

```yaml
gap_analysis:
  from_family: "ml-fp"
  to_family: "systems"
  difficulty: 4  # 1-4 scale

  impossible:
    - concept: "Higher-kinded types"
      reason: "No HKT support in target"
      mitigation: "Monomorphize or use trait objects"
      ir_impact: "Layer 2 type abstractions cannot preserve HKT"

  lossy:
    - concept: "Type inference"
      loss: "Must add explicit type annotations"
      automation: "partial"
      source_skills: ["haskell-rust", "scala-rust"]

  structural:
    - concept: "Algebraic data types"
      translation: "ADT → struct + enum"
      complexity: "medium"
      bidirectional: false  # systems → ml-fp is different

  runtime:
    - concept: "Garbage collection"
      translation: "GC → ownership/borrowing"
      complexity: "high"
      requires_redesign: true
```

### 3.3 Gap Severity Matrix

Create 9×9 matrix of conversion difficulty between all families:

```
FROM → TO       | ML-FP | BEAM | LISP | Systems | Dynamic | Managed | Apple | Logic | Proced |
----------------|-------|------|------|---------|---------|---------|-------|-------|--------|
ML-FP           | -     | 2    | 2    | 4       | 1       | 2       | 2     | 4     | 3      |
BEAM            | 2     | -    | 2    | 4       | 2       | 2       | 3     | 3     | 3      |
LISP            | 2     | 2    | -    | 4       | 1       | 2       | 3     | 3     | 3      |
Systems         | 3     | 4    | 3    | -       | 3       | 2       | 2     | 4     | 2      |
Dynamic         | 2     | 2    | 1    | 4       | -       | 2       | 2     | 3     | 2      |
Managed         | 2     | 3    | 2    | 3       | 2       | -       | 2     | 4     | 2      |
Apple           | 2     | 3    | 3    | 2       | 2       | 2       | -     | 4     | 2      |
Logic           | 4     | 3    | 3    | 4       | 3       | 4       | 4     | -     | 4      |
Procedural      | 3     | 3    | 3    | 2       | 2       | 2       | 2     | 4     | -      |

Legend: 1=Easy, 2=Moderate, 3=Hard, 4=Very Hard (requires significant redesign)
```

### 3.4 Bidirectional Gap Analysis

Identify asymmetric gaps where A→B ≠ B→A:

| Gap | A→B | B→A | Asymmetry Reason |
|-----|-----|-----|------------------|
| GC ↔ Ownership | Hard (restructure) | Easy (ignore ownership) | Ownership info lost going to GC |
| Static ↔ Dynamic | Easy (erase types) | Hard (infer types) | Type info lost going to dynamic |
| Actors ↔ Threads | Hard (restructure) | Hard (add message passing) | Different paradigms |
| HKT ↔ No HKT | Lossy (monomorphize) | N/A (can't add) | HKT is strictly more powerful |

### 3.5 Common Gap Patterns

Document recurring gap patterns with from/to examples:

#### Type System Gaps

| Pattern | From | To | Example From | Example To | Mitigation |
|---------|------|----|--------------|------------|------------|
| Dynamic → Static | Python, JS | Rust, Java | `def f(x):` | `fn f(x: T)` | Type inference + annotations |
| Nullable → Non-null | Java, C# | Rust, Kotlin | `String s` | `Option<String>` | Wrap in Option/Optional |
| HKT → No HKT | Haskell, Scala | Go, Rust | `Functor f` | `FunctorInt`, `FunctorString` | Monomorphize |
| Gradual → Static | TypeScript | Java | `any` | `Object` | Resolve to concrete types |

#### Memory Model Gaps

| Pattern | From | To | Example From | Example To | Mitigation |
|---------|------|----|--------------|------------|------------|
| GC → Manual | Java | C | `new Object()` | `malloc(); ... free();` | Add explicit free() |
| GC → Ownership | Python | Rust | `x = obj` | `let x = obj.clone()` | Restructure for borrowing |
| Shared → Linear | Java | Rust | `obj.method()` | `&obj` or `&mut obj` | Clone or restructure |
| Mutable → Immutable | Python | Haskell | `x = x + 1` | `let x' = x + 1` | Transform to pure functions |

#### Effect System Gaps

| Pattern | From | To | Example From | Example To | Mitigation |
|---------|------|----|--------------|------------|------------|
| Exceptions → Results | Java | Rust | `throw new E()` | `Err(E)` | Wrap in Result, use `?` |
| Null → Option | Java | Rust | `if (x != null)` | `if let Some(x)` | Map null checks |
| Callbacks → Async | JS | Rust | `f(x => ...)` | `async { f().await }` | Transform chains |
| Monads → Direct | Haskell | Go | `do { x <- m; ... }` | `x := m(); ...` | Inline operations |

#### Concurrency Gaps

| Pattern | From | To | Example From | Example To | Mitigation |
|---------|------|----|--------------|------------|------------|
| Actors → Threads | Erlang | Java | `Pid ! msg` | `queue.put(msg)` | Thread pools + queues |
| Threads → Actors | Java | Erlang | `synchronized` | `gen_server` | Restructure around processes |
| Green → OS | Go | C | `go f()` | `pthread_create()` | Thread pool library |
| CSP → Async | Go | JS | `ch <- v` | `await promise` | Transform channels to promises |

### 3.6 Semantic Preservation Levels

Define what "correct conversion" means at each level:

```
Level 0: Syntactically valid
  - Code compiles/parses in target language
  - May not run correctly
  - Useful for: syntax exploration, scaffolding

Level 1: Semantically equivalent
  - Same observable behavior for same inputs
  - Same outputs, same side effects
  - May not be idiomatic
  - Useful for: correctness-critical code, formal verification

Level 2: Idiomatically correct
  - Follows target language conventions
  - Uses appropriate patterns and libraries
  - Readable by target language developers
  - Useful for: maintainable production code

Level 3: Optimized
  - Efficient in target language
  - Uses target's strengths (e.g., ownership in Rust)
  - Production-ready performance
  - Useful for: performance-critical code
```

### 3.7 Human Decision Points

Extract from Phase 0's 183 `human_decision` gaps and catalog:

| Decision Point | Options | Guidance | Automation |
|----------------|---------|----------|------------|
| Error handling strategy | Exceptions, Results, Panics | Match target idioms | Partial - can suggest |
| Null handling | Option, assertion, default, sentinel | Based on nullability semantics | Partial - context needed |
| Concurrency model | Threads, async, actors, channels | Based on use case requirements | None - architectural |
| Memory management | Clone, borrow, Arc, raw pointer | Based on ownership patterns | Partial - lifetime analysis |
| Generic instantiation | Concrete types for HKT | Case-by-case monomorphization | Partial - can enumerate |
| Collection choice | Array, Vec, List, Seq | Based on access patterns | Partial - can analyze usage |

### 3.8 Cross-Validate with Phase 2 Profiles

Verify gaps align with `semantic_gaps` from language YAML profiles:

```bash
# Extract all semantic_gaps from YAML profiles
for f in data/languages/*.yaml; do
  yq '.semantic_gaps[]?.description' "$f"
done | sort | uniq -c | sort -rn
```

Expected alignment:
- Each language's `semantic_gaps` should map to family-level gaps
- Language-specific gaps should be documented in gap patterns
- Severity ratings should be consistent

### 3.9 IR Design Implications

Document how each gap category affects IR layer design:

| Gap Category | IR Layer Impact | Design Consideration |
|--------------|-----------------|----------------------|
| Impossible | Layer 2-3 | Cannot represent; must reject or lossy-convert |
| Lossy | Layer 2 annotations | Track lost information for warnings |
| Structural | Layer 1-2 | IR must support both representations |
| Idiomatic | Layer 3 | Style transforms in target-specific lowering |
| Runtime | Layer 0-1 | May require runtime shims or redesign |
| Semantic | Layer 2 | Semantic annotations to preserve meaning |

## SQL Data Population

Use existing tables from `data/schema.sql`. Generate INSERT statements:

```sql
-- data/gaps.sql
-- Populates existing tables from schema.sql (lines 131-185)
-- Do NOT recreate tables - they already exist

-- Populate semantic_gaps (family-pair gaps)
INSERT OR REPLACE INTO semantic_gaps
  (from_family_id, to_family_id, gap_category, concept, description, severity, mitigation, automation_level)
VALUES
  -- ML-FP → Systems gaps
  ((SELECT id FROM families WHERE name='ml-fp'),
   (SELECT id FROM families WHERE name='systems'),
   'lossy', 'Higher-kinded types', 'HKT cannot be preserved', 'high',
   'Monomorphize to concrete types', 'partial'),
  -- ... more gaps
;

-- Populate gap_patterns (reusable patterns)
INSERT OR REPLACE INTO gap_patterns
  (name, category, description, from_concept, to_concept, mitigation_strategy, example_from, example_to)
VALUES
  ('gc-to-ownership', 'memory', 'GC to ownership-based memory',
   'Garbage collection', 'Ownership/borrowing', 'Restructure for single owner',
   'x = obj', 'let x = obj;'),
  -- ... more patterns
;

-- Populate decision_points
INSERT OR REPLACE INTO decision_points
  (name, description, options, guidance)
VALUES
  ('error-handling', 'Choose error handling strategy',
   '["exceptions", "results", "panics"]', 'Match target language idioms'),
  -- ... more decision points
;

-- Populate family_conversion_difficulty (9x9 matrix)
INSERT OR REPLACE INTO family_conversion_difficulty
  (from_family_id, to_family_id, difficulty, notes)
SELECT f1.id, f2.id,
  CASE
    WHEN f1.name = 'ml-fp' AND f2.name = 'systems' THEN 4
    WHEN f1.name = 'dynamic' AND f2.name = 'ml-fp' THEN 2
    -- ... matrix values
  END,
  'Generated from Phase 3 analysis'
FROM families f1, families f2
WHERE f1.name != f2.name;
```

## Success Criteria

- [ ] All 320 Phase 0 gaps classified into 6 categories
- [ ] 72 directed family pairs analyzed (9 families × 8 targets)
- [ ] 9×9 gap severity matrix complete with supporting evidence
- [ ] At least 50 gap patterns documented with from/to examples and mitigations
- [ ] All 183 human decision gaps mapped to decision points
- [ ] Semantic preservation levels defined with use cases
- [ ] Cross-validation with Phase 2 YAML `semantic_gaps` complete
- [ ] IR design implications documented for each gap category
- [ ] `data/gaps.sql` populates existing schema tables (no DDL)

## Quality Gates

| Gate | Validation |
|------|------------|
| Gap classification | Each gap has: category, severity, mitigation |
| Pattern completeness | Each pattern has: from/to examples, at least one mitigation |
| Matrix consistency | Difficulty scores justified by gap counts |
| Cross-reference | 90%+ of YAML semantic_gaps map to family gaps |
| SQL validity | `data/gaps.sql` executes without errors on `schema.sql` |

## Effort Estimate

2-3 days

## Output Files

| File | Description |
|------|-------------|
| `analysis/semantic-gaps.md` | Comprehensive gap analysis with all family pairs |
| `data/gaps.sql` | INSERT statements for schema.sql tables |
| `docs/src/ir-schema/preservation-levels.md` | Preservation level definitions and guidance |
