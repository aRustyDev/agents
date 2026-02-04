# IR Schema Research Plan

Multi-phase research plan for designing the Intermediate Representation (IR) schema to support cross-language codebase conversion.

## Goals

1. **Primary**: Design an IR that captures enough semantic information to convert between any supported language pair with high fidelity
2. **Secondary**: Support incremental analysis (partial codebases, evolving code)
3. **Tertiary**: Enable tooling ecosystem (extraction, synthesis, diffing, validation)

## Success Criteria

- [ ] IR can represent 80%+ of patterns in existing convert-* skills
- [ ] Round-trip conversion preserves semantics (same behavior, not same syntax)
- [ ] Cross-family conversions identify and document information loss
- [ ] Incremental updates don't require full re-analysis

---

## Phase 0: Extract Patterns from Existing Skills

**Goal**: Mine the 49 existing convert-* skills for implicit IR patterns

### 0.1 Pattern Extraction
- [ ] For each convert-* skill, extract:
  - Type mappings (source type → target type)
  - Idiom translations (source pattern → target pattern)
  - Semantic gaps (what cannot be directly translated)
  - Error handling mappings
  - Concurrency pattern mappings

### 0.2 Pattern Clustering
- [ ] Cluster extracted patterns by:
  - Universal (applies to all conversions)
  - Family-specific (applies within a family)
  - Language-specific (unique to a language pair)

### 0.3 Gap Analysis
- [ ] Identify conversions marked as "lossy" or "approximate"
- [ ] Identify patterns that require human decision (multiple valid targets)
- [ ] Document "impossible" conversions (semantic gaps)

**Output**: `phase-0-pattern-extraction.md`

---

## Phase 1: Language Family Research

**Goal**: Comprehensive taxonomy of language families with feature analysis

### 1.1 Family Identification

Survey and identify all meaningful language family clusters:

| Category | Families | Key Characteristics |
|----------|----------|---------------------|
| Paradigm | Functional, OOP, Procedural, Logic, Array | Primary programming model |
| Typing | Static, Dynamic, Gradual, Dependent | Type system approach |
| Memory | Manual, GC, RC, Ownership | Memory management |
| Execution | Compiled, Interpreted, JIT, Transpiled | How code runs |
| Effects | Exceptions, Results, Monadic, Algebraic | Error/effect handling |
| Concurrency | Threads, Actors, CSP, Async, None | Parallel execution model |

### 1.2 Feature Dimensions

For each family, analyze:

```yaml
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
  structured: if/else, loops, match/switch
  effects: exceptions | result-types | algebraic-effects | monads
  async: callbacks | promises | async-await | green-threads | actors

data:
  primitives: [list of primitive types]
  composites: arrays | lists | records | tuples | unions | classes
  abstraction: modules | classes | traits | typeclasses | protocols

meta:
  macros: none | text | syntactic | hygienic | procedural
  reflection: none | runtime | compile-time | reified-generics
  codegen: none | templates | type-providers | derive
```

### 1.3 Family Comparison Matrix

Create comparison matrices for:
- [ ] Family × Feature grid
- [ ] Family × Family semantic distance
- [ ] Conversion difficulty heatmap (which family pairs are hard?)

**Output**:
- `docs/src/language-families/overview.md`
- `docs/src/language-families/{family-name}.md` for each family
- `phase-1-family-taxonomy.md`

---

## Phase 2: Language Survey

**Goal**: Catalog languages with family classification and feature profiles

### 2.1 Prioritization

```
Tier 1 (Must Have): Languages in existing convert-* skills
  - python, typescript, java, c, cpp, golang, rust
  - haskell, elm, roc, fsharp, scala
  - erlang, elixir, clojure
  - objc, swift

Tier 2 (Should Have): Top 20 by popularity + emerging
  - kotlin, ruby, php, perl, r, julia, lua
  - zig, gleam, mojo, nim, crystal, v

Tier 3 (Nice to Have): Historically significant
  - cobol, fortran, pascal, ada, lisp, scheme, prolog
```

### 2.2 Per-Language Profile

For each Tier 1-2 language, create profile:

```yaml
language: rust
version: "1.75"  # version this analysis targets
family:
  paradigm: [systems, functional]
  typing: static
  memory: ownership
  execution: compiled
  effects: result-types
  concurrency: [threads, async]

popularity:
  tiobe_rank: 17
  stackoverflow_loved: 87%
  github_repos: 2.1M

features:
  typing:
    strength: static
    inference: bidirectional
    generics: bounded
    nullability: non-null (Option)
  # ... (full feature breakdown)

syntax:
  function_def: "fn name(params) -> ReturnType { body }"
  type_def: "struct Name { fields } | enum Name { variants }"
  # ... (syntax patterns for IR extraction)

semantic_gaps:
  - "No runtime reflection"
  - "No exceptions (must use Result)"
  - "Ownership rules may require restructuring"
```

### 2.3 Convert-* Skill Coverage

Map existing skills to languages:

| Language | As Source | As Target | Gaps |
|----------|-----------|-----------|------|
| python | 11 skills | 1 skill | No ruby→python, no js→python |
| rust | 0 skills | 6 skills | No rust→anything |
| ... | ... | ... | ... |

**Output**:
- `docs/src/languages/{language}.md` for each language
- `phase-2-language-profiles.md`
- `phase-2-coverage-gaps.md`

---

## Phase 3: Semantic Gap Analysis

**Goal**: Identify and classify conversion challenges

### 3.1 Gap Categories

| Category | Example | Severity | Mitigation |
|----------|---------|----------|------------|
| **Impossible** | Dependent types → simple types | Cannot convert | Document limitation |
| **Lossy** | Dynamic → static typing | Info loss | Infer types + annotate unknowns |
| **Structural** | Exceptions → Results | Restructure | Pattern transformation |
| **Idiomatic** | Loops → recursion | Style diff | Multiple valid outputs |
| **Runtime** | GC → manual memory | Different model | Add explicit management |

### 3.2 Family Pair Analysis

For each family pair, analyze:
- What concepts exist in source but not target?
- What concepts require translation (not 1:1)?
- What information is lost?
- What human decisions are needed?

### 3.3 Semantic Preservation Levels

Define what "correct conversion" means:

```
Level 0: Syntactically valid (compiles/runs)
Level 1: Semantically equivalent (same behavior)
Level 2: Idiomatically correct (follows target conventions)
Level 3: Optimized (efficient in target language)
```

**Output**: `phase-3-semantic-gaps.md`

---

## Phase 4: IR Schema Design

**Goal**: Design the multi-layer IR architecture

### 4.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTRACTION (Source → IR)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 4: Structural IR                                         │
│  ├── Modules, packages, namespaces                              │
│  ├── Public/private boundaries                                  │
│  ├── Import/export dependencies                                 │
│  └── Build/compilation units                                    │
│                                                                 │
│  Layer 3: Type IR                                               │
│  ├── Type definitions (ADTs, classes, interfaces)               │
│  ├── Type relationships (subtyping, implements, extends)        │
│  ├── Generic/parametric types                                   │
│  └── Type constraints and bounds                                │
│                                                                 │
│  Layer 2: Control Flow IR                                       │
│  ├── Function/method signatures                                 │
│  ├── Control patterns (branch, loop, match, try)                │
│  ├── Effect annotations (pure, throws, async)                   │
│  └── Concurrency patterns (spawn, await, channel)               │
│                                                                 │
│  Layer 1: Data Flow IR                                          │
│  ├── Variable bindings and lifetimes                            │
│  ├── Data transformations (map, filter, fold)                   │
│  ├── Side effect tracking                                       │
│  └── Dependency graph between expressions                       │
│                                                                 │
│  Layer 0: Expression IR (optional, for deep analysis)           │
│  ├── Full AST representation                                    │
│  ├── Operator semantics                                         │
│  └── Literal values and constants                               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    SYNTHESIS (IR → Target)                       │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 IR Schema Definition

Define schemas for each layer:

```yaml
# Layer 4: Structural
module:
  id: ModuleId
  name: string
  path: string[]
  visibility: public | internal | private
  imports: Import[]
  exports: Export[]
  definitions: Definition[]

# Layer 3: Type
type_def:
  id: TypeId
  name: string
  kind: struct | enum | class | interface | alias | opaque
  params: TypeParam[]  # generics
  constraints: Constraint[]
  body: TypeBody

# Layer 2: Control Flow
function:
  id: FunctionId
  name: string
  params: Param[]
  return_type: TypeRef
  effects: Effect[]  # pure, throws, async, etc.
  body: ControlFlowGraph

# Layer 1: Data Flow
binding:
  id: BindingId
  name: string
  type: TypeRef
  mutability: mutable | immutable | linear
  lifetime: Lifetime
  value: Expression | None
```

### 4.3 Format Specifications

| Use Case | Format | Rationale |
|----------|--------|-----------|
| Human review | YAML/JSON | Readable, diffable |
| Tool interop | Protobuf | Fast, typed, versioned |
| Storage | SQLite | Queryable, incremental |
| Transport | MessagePack | Compact, fast |

### 4.4 Incremental IR Design

```yaml
incremental_unit:
  id: UnitId
  hash: ContentHash  # for change detection
  layer: 0-4
  dependencies: UnitId[]  # what this depends on
  dependents: UnitId[]  # what depends on this
  content: LayerContent

change_set:
  base_version: VersionId
  changes:
    - unit_id: UnitId
      change_type: add | modify | delete
      old_hash: ContentHash | None
      new_hash: ContentHash | None
```

**Output**:
- `docs/src/ir-schema/overview.md`
- `docs/src/ir-schema/layer-{n}.md` for each layer
- `schemas/ir-v1.proto` (Protobuf definitions)
- `schemas/ir-v1.json` (JSON Schema)

---

## Phase 5: Validation & Tooling

**Goal**: Verify IR design and build extraction/synthesis tools

### 5.1 Validation Criteria

- [ ] **Completeness**: Can represent all patterns from Phase 0
- [ ] **Round-trip**: Source → IR → Source' is semantically equivalent
- [ ] **Cross-family**: IR supports family-to-family conversion
- [ ] **Incrementality**: Partial updates work correctly

### 5.2 Prototype Tools

```
tools/
├── ir-extract/       # Source code → IR
│   ├── python/
│   ├── typescript/
│   └── rust/
├── ir-synthesize/    # IR → Target code
│   ├── python/
│   ├── typescript/
│   └── rust/
├── ir-diff/          # Compare two IRs
├── ir-validate/      # Check IR consistency
└── ir-visualize/     # Generate diagrams
```

### 5.3 Test Suite

- Unit tests: Individual IR layer correctness
- Integration tests: Full extraction → synthesis pipeline
- Regression tests: Known convert-* skill examples
- Property tests: Random valid IR generation

**Output**:
- `tools/` directory with prototypes
- `tests/` directory with test suite
- `phase-5-validation-report.md`

---

## Phase 6: Consolidation

**Goal**: Merge per-language insights into unified IR

### 6.1 Pattern Consolidation

Analyze all per-language IRs to identify:
- Universal patterns (all languages)
- Family patterns (shared within family)
- Language-specific extensions

### 6.2 Abstract IR Design

Create the minimal abstract IR that can:
- Represent any source language (with extensions)
- Generate any target language (with synthesis rules)
- Identify semantic gaps explicitly

### 6.3 Skill Architecture Redesign

Based on consolidated IR, redesign skill structure:

```
context/skills/
├── codebase-analysis/
│   ├── SKILL.md
│   └── reference/
│       ├── ir/
│       │   ├── schema.md
│       │   ├── extraction-guide.md
│       │   └── tools.md
│       ├── families/
│       │   ├── ml-fp.md
│       │   ├── beam.md
│       │   └── ...
│       └── languages/
│           ├── python.md
│           ├── rust.md
│           └── ...
│
├── codebase-implement-from-ir/
│   ├── SKILL.md
│   └── reference/
│       ├── synthesis-guide.md
│       ├── patterns/
│       │   ├── error-handling.md
│       │   ├── concurrency.md
│       │   └── ...
│       └── targets/
│           ├── rust/
│           ├── roc/
│           └── ...
│
└── idiomatic-{lang}/
    └── SKILL.md  # Language-specific idioms
```

**Output**:
- `phase-6-consolidated-ir.md`
- Updated skill architecture
- Migration plan for existing convert-* skills

---

## SQLite Schema for Analysis

```sql
-- Language families
CREATE TABLE families (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- paradigm, typing, memory, etc.
    description TEXT
);

-- Languages
CREATE TABLE languages (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    version TEXT,
    tier INTEGER NOT NULL,  -- 1, 2, or 3
    popularity_tiobe INTEGER,
    popularity_so REAL
);

-- Language-Family relationships (many-to-many)
CREATE TABLE language_families (
    language_id INTEGER REFERENCES languages(id),
    family_id INTEGER REFERENCES families(id),
    PRIMARY KEY (language_id, family_id)
);

-- Language features
CREATE TABLE language_features (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    dimension TEXT NOT NULL,  -- typing, memory, control, etc.
    feature TEXT NOT NULL,
    value TEXT NOT NULL,
    notes TEXT
);

-- IR patterns extracted from convert-* skills
CREATE TABLE ir_patterns (
    id INTEGER PRIMARY KEY,
    source_skill TEXT NOT NULL,
    pattern_type TEXT NOT NULL,  -- type_mapping, idiom, gap, etc.
    source_lang TEXT,
    target_lang TEXT,
    source_pattern TEXT NOT NULL,
    target_pattern TEXT,
    is_lossy BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Semantic gaps
CREATE TABLE semantic_gaps (
    id INTEGER PRIMARY KEY,
    source_family TEXT,
    target_family TEXT,
    source_concept TEXT NOT NULL,
    severity TEXT NOT NULL,  -- impossible, lossy, structural, idiomatic
    mitigation TEXT,
    notes TEXT
);

-- IR layer definitions
CREATE TABLE ir_layers (
    id INTEGER PRIMARY KEY,
    layer_num INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    schema_json TEXT  -- JSON Schema for this layer
);

-- Convert-* skill coverage
CREATE TABLE skill_coverage (
    id INTEGER PRIMARY KEY,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    skill_name TEXT,  -- NULL if no skill exists
    similarity_score REAL,
    notes TEXT
);

-- FTS for searching
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    source_pattern, target_pattern, notes,
    content='ir_patterns'
);
```

---

## Timeline Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 0 | 2-3 days | None |
| Phase 1 | 3-5 days | None (parallel with 0) |
| Phase 2 | 5-7 days | Phase 1 |
| Phase 3 | 2-3 days | Phase 0, 1, 2 |
| Phase 4 | 5-7 days | Phase 3 |
| Phase 5 | 7-10 days | Phase 4 |
| Phase 6 | 3-5 days | Phase 5 |

**Total: ~4-6 weeks** with focused effort

---

## Next Actions

1. [ ] Create `docs/src/language-families/` directory structure
2. [ ] Create SQLite schema and initialize database
3. [ ] Start Phase 0: Extract patterns from existing convert-* skills
4. [ ] Start Phase 1 (parallel): Research language families
