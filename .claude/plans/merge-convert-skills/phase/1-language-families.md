# Phase 1: Language Family Research

Comprehensive taxonomy of language families with feature analysis.

## Goal

Create a structured understanding of programming language families to inform IR design and conversion strategies.

## Dependencies

None — can run in parallel with Phase 0.

## Deliverables

- [ ] `docs/src/language-families/overview.md` - Comparison matrices
- [ ] `docs/src/language-families/{family}.md` - Per-family documentation
- [ ] `data/families.sql` - SQL dump of family data
- [ ] `analysis/family-taxonomy.md` - Taxonomy analysis

## Tasks

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

  examples:
    - language: "..."
      notes: "..."
```

### 1.3 Family Comparison Matrix

Create matrices for cross-family analysis:

Feature × Family Matrix:

```
                | ML-FP | BEAM | LISP | Systems | Managed | Dynamic |
----------------|-------|------|------|---------|---------|---------|
Typing          | static| dyn  | dyn  | static  | static  | dynamic |
Memory          | GC    | GC   | GC   | manual* | GC      | GC      |
Immutability    | yes   | yes  | yes  | no      | no      | no      |
Pattern Match   | yes   | yes  | no   | partial | no      | no      |
First-Class Fn  | yes   | yes  | yes  | yes     | partial | yes     |
Concurrency     | varies| actor| varies| threads| threads | varies  |
```

Conversion Difficulty Matrix:

```
FROM → TO       | ML-FP | BEAM | LISP | Systems | Managed | Dynamic |
----------------|-------|------|------|---------|---------|---------|
ML-FP           | Easy  | Med  | Med  | Hard    | Med     | Easy    |
BEAM            | Med   | Easy | Med  | Hard    | Med     | Med     |
LISP            | Med   | Med  | Easy | Hard    | Med     | Easy    |
Systems         | Hard  | Hard | Hard | Med     | Med     | Hard    |
Managed         | Med   | Med  | Med  | Med     | Easy    | Med     |
Dynamic         | Med   | Med  | Easy | Hard    | Med     | Easy    |
```

### 1.4 Family Documentation Template

For each family, create documentation:

```markdown
# {Family Name}

## Overview
Brief description of the family's core philosophy.

## Key Characteristics
- Defining features
- Common patterns
- Typical use cases

## Languages in Family
| Language | Notes |
|----------|-------|
| ... | ... |

## Type System
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

### Converting TO this family
- What maps naturally
- What requires restructuring
- Idiomatic patterns to target

## See Also
- Related families
- Relevant skills
```

## Families to Document

### By Paradigm
- [ ] `ml-fp-pure.md` - Haskell, Elm, PureScript, Idris
- [ ] `ml-fp-hybrid.md` - F#, Scala, OCaml, ReasonML
- [ ] `beam.md` - Erlang, Elixir, Gleam
- [ ] `lisp.md` - Clojure, Common Lisp, Scheme, Racket
- [ ] `systems.md` - Rust, C, C++, Zig
- [ ] `managed-oop.md` - Java, C#, Kotlin
- [ ] `dynamic.md` - Python, Ruby, JavaScript/TypeScript
- [ ] `logic.md` - Prolog, Datalog, Mercury
- [ ] `array.md` - APL, J, K, BQN

### By Notable Feature
- [ ] `ownership.md` - Languages with ownership/borrowing
- [ ] `actors.md` - Languages with actor model
- [ ] `dependent-types.md` - Idris, Agda, Coq
- [ ] `gradual-typing.md` - TypeScript, Python (typed), Hack

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

-- Family characteristics
CREATE TABLE family_characteristics (
    id INTEGER PRIMARY KEY,
    family_id INTEGER REFERENCES families(id),
    dimension TEXT NOT NULL,  -- typing, memory, control, data, meta
    characteristic TEXT NOT NULL,
    value TEXT NOT NULL,
    notes TEXT
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
    notes TEXT,
    semantic_gaps TEXT  -- JSON array of gap descriptions
);
```

## Success Criteria

- [ ] At least 10 major families documented
- [ ] Feature matrices created for all dimensions
- [ ] Conversion difficulty rated for all family pairs
- [ ] Each family has 2+ example languages
- [ ] Documentation follows consistent template

## Effort Estimate

3-5 days

## Output Files

| File | Description |
|------|-------------|
| `docs/src/language-families/overview.md` | Comparison matrices |
| `docs/src/language-families/{family}.md` | Per-family docs |
| `data/families.sql` | SQL dump |
| `analysis/family-taxonomy.md` | Taxonomy analysis |
