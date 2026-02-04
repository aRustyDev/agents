# Convert Skills Merge Analysis

Analysis of 78 `convert-<source>-<target>` skills to determine merge potential and architecture for an intermediate representation (IR) approach.

## Executive Summary

- **78 total skills** analyzed
- **29 bidirectional pairs** found (A↔B skills exist for both directions)
- **11 target language groups** with 2+ members
- **Key insight**: Bidirectional pairs average **0.94 similarity** — nearly identical content
- **Recommendation**: Merge bidirectional pairs first, then consolidate by target language family

## 1. Bidirectional Pair Analysis

Skills that exist in both directions (convert-A-B and convert-B-A) share extremely high semantic similarity, indicating substantial content duplication.

### Similarity Thresholds

| Threshold | Interpretation   | Action                         |
| --------- | ---------------- | ------------------------------ |
| > 0.95    | Nearly identical | **Merge immediately**          |
| 0.90–0.95 | Very similar     | Merge with minor adjustments   |
| 0.85–0.90 | Similar          | Share common template          |
| < 0.85    | Distinct enough  | Keep separate or partial merge |

### Bidirectional Pairs (Sorted by Similarity)

| Skill A                   | Skill B                   | Similarity | Recommendation         |
| ------------------------- | ------------------------- | ---------- | ---------------------- |
| convert-fsharp-roc        | convert-roc-fsharp        | **0.994**  | Merge immediately      |
| convert-elm-roc           | convert-roc-elm           | **0.989**  | Merge immediately      |
| convert-clojure-fsharp    | convert-fsharp-clojure    | **0.985**  | Merge immediately      |
| convert-roc-scala         | convert-scala-roc         | **0.985**  | Merge immediately      |
| convert-erlang-roc        | convert-roc-erlang        | **0.974**  | Merge immediately      |
| convert-elixir-erlang     | convert-erlang-elixir     | **0.972**  | Merge immediately      |
| convert-fsharp-scala      | convert-scala-fsharp      | **0.967**  | Merge immediately      |
| convert-elm-scala         | convert-scala-elm         | **0.967**  | Merge immediately      |
| convert-clojure-haskell   | convert-haskell-clojure   | **0.962**  | Merge immediately      |
| convert-haskell-scala     | convert-scala-haskell     | **0.957**  | Merge immediately      |
| convert-clojure-erlang    | convert-erlang-clojure    | 0.947      | Merge with adjustments |
| convert-elm-fsharp        | convert-fsharp-elm        | 0.945      | Merge with adjustments |
| convert-clojure-elm       | convert-elm-clojure       | 0.945      | Merge with adjustments |
| convert-haskell-roc       | convert-roc-haskell       | 0.944      | Merge with adjustments |
| convert-elixir-haskell    | convert-haskell-elixir    | 0.940      | Merge with adjustments |
| convert-clojure-elixir    | convert-elixir-clojure    | 0.936      | Merge with adjustments |
| convert-elixir-elm        | convert-elm-elixir        | 0.935      | Merge with adjustments |
| convert-elixir-scala      | convert-scala-elixir      | 0.934      | Merge with adjustments |
| convert-python-typescript | convert-typescript-python | 0.934      | Merge with adjustments |
| convert-elm-haskell       | convert-haskell-elm       | 0.930      | Merge with adjustments |
| convert-elixir-fsharp     | convert-fsharp-elixir     | 0.926      | Merge with adjustments |
| convert-clojure-roc       | convert-roc-clojure       | 0.925      | Merge with adjustments |
| convert-elixir-roc        | convert-roc-elixir        | 0.924      | Merge with adjustments |
| convert-fsharp-haskell    | convert-haskell-fsharp    | 0.919      | Merge with adjustments |
| convert-erlang-fsharp     | convert-fsharp-erlang     | 0.919      | Merge with adjustments |
| convert-clojure-scala     | convert-scala-clojure     | 0.918      | Merge with adjustments |
| convert-erlang-scala      | convert-scala-erlang      | 0.913      | Merge with adjustments |
| convert-erlang-haskell    | convert-haskell-erlang    | 0.901      | Merge with adjustments |
| convert-elm-erlang        | convert-erlang-elm        | 0.888      | Share common template  |

### Analysis

All 29 bidirectional pairs have similarity > 0.85, with 10 pairs above 0.95. This strongly suggests:

1. **The conversion knowledge is symmetric** — understanding how to convert A→B is nearly identical to B→A
2. **Direction-specific details are minimal** — mostly the same concepts, patterns, and mappings
3. **Merge is safe** — creating a single `convert-A-B` skill that handles both directions will not lose information

## 2. Target Language Group Analysis

Skills grouped by their target language reveal which target ecosystems share conversion patterns.

### Target Group Summary

| Target  | Skills | Avg Similarity | Min   | Max   | Notes                              |
| ------- | ------ | -------------- | ----- | ----- | ---------------------------------- |
| clojure | 8      | **0.852**      | 0.803 | 0.916 | Highest avg — LISP family cohesion |
| erlang  | 8      | **0.838**      | 0.791 | 0.876 | BEAM ecosystem cohesion            |
| cpp     | 2      | 0.829          | —     | —     | Only C and Java sources            |
| golang  | 2      | 0.826          | —     | —     | Only Python and TypeScript sources |
| scala   | 8      | 0.822          | 0.730 | 0.890 | JVM/FP hybrid target               |
| haskell | 8      | 0.819          | 0.743 | 0.896 | Pure FP target                     |
| elixir  | 8      | 0.805          | 0.715 | 0.879 | BEAM ecosystem                     |
| rust    | 6      | 0.802          | 0.657 | 0.908 | Systems language target            |
| elm     | 8      | 0.801          | 0.703 | 0.890 | ML-family web target               |
| roc     | 8      | 0.793          | 0.736 | 0.856 | New ML-family language             |
| fsharp  | 8      | 0.752          | 0.656 | 0.844 | .NET ML-family                     |

### Target Group Details

#### clojure (8 skills, avg: 0.852)

| Source             | Similarity to Group   |
| ------------------ | --------------------- |
| Most similar pair  | elixir↔erlang (0.916) |
| Least similar pair | elm↔haskell (0.803)   |

Members: elixir, elm, erlang, fsharp, haskell, python, roc, scala

**Insight**: Clojure's homoiconic/LISP nature creates consistent conversion patterns regardless of source. The high similarity suggests a single "→Clojure" conversion template could work.

#### erlang (8 skills, avg: 0.838)

| Source             | Similarity to Group |
| ------------------ | ------------------- |
| Most similar pair  | python↔roc (0.876)  |
| Least similar pair | roc↔scala (0.791)   |

Members: clojure, elixir, elm, fsharp, haskell, python, roc, scala

**Insight**: BEAM VM targeting creates uniform patterns. Actor model and OTP concepts are the common denominator.

#### rust (6 skills, avg: 0.802)

| Source             | Similarity to Group   |
| ------------------ | --------------------- |
| Most similar pair  | golang↔python (0.908) |
| Least similar pair | c↔typescript (0.657)  |

Members: c, cpp, golang, java, python, typescript

**Insight**: Wider variance (0.657–0.908) indicates source language family matters more for Rust. Systems languages (C, C++) convert differently than managed languages (Python, TypeScript).

#### fsharp (8 skills, avg: 0.752)

| Source             | Similarity to Group   |
| ------------------ | --------------------- |
| Most similar pair  | elixir↔erlang (0.844) |
| Least similar pair | haskell↔roc (0.656)   |

Members: clojure, elixir, elm, erlang, haskell, python, roc, scala

**Insight**: Lowest average similarity. F#'s .NET integration and ML heritage create conversion complexity. Source language family affects conversion strategy more than for other targets.

## 3. Proposed Architecture: Intermediate Representation (IR)

Based on the analysis, an IR-based architecture should capture:

### 3.1 Core IR Components

```asciidoc
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE CODE ANALYSIS                         │
├─────────────────────────────────────────────────────────────────┤
│  Parser → AST → Semantic Analysis → IR Extraction               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 INTERMEDIATE REPRESENTATION                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Data Flow IR   │  Control IR     │  Structural IR              │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • Type schemas  │ • Conditionals  │ • Module boundaries         │
│ • Data shapes   │ • Loops/Recur   │ • Public interfaces         │
│ • Transforms    │ • Error paths   │ • Dependency graph          │
│ • Pipelines     │ • Concurrency   │ • Component hierarchy       │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TARGET CODE SYNTHESIS                         │
├─────────────────────────────────────────────────────────────────┤
│  IR → Target Idioms → Code Generation → Formatting              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 IR Schema (Conceptual)

```yaml
intermediate_representation:
  # Structural Layer
  modules:
    - name: string
      visibility: public | internal
      dependencies: [module_ref]
      exports: [symbol]

  # Type Layer
  types:
    - name: string
      kind: primitive | composite | generic | opaque
      structure:
        fields: [{ name, type, mutability }]
        variants: [{ name, fields }] # for sum types
        constraints: [type_constraint]

  # Data Flow Layer
  data_flows:
    - id: uuid
      inputs: [typed_value]
      transformations: [transform_step]
      outputs: [typed_value]
      side_effects: [effect_descriptor]

  # Control Flow Layer
  control_patterns:
    - kind: sequential | branching | looping | concurrent
      structure: pattern_specific_structure
      error_handling: [error_path]

  # Behavioral Layer
  behaviors:
    - interface: [method_signature]
      implementations: [{ type, methods }]
      invariants: [constraint]
```

### 3.3 Language Family Mappings

Based on similarity analysis, languages cluster into families with shared IR mapping strategies:

| Family           | Languages                | Shared IR Patterns                                            |
| ---------------- | ------------------------ | ------------------------------------------------------------- |
| **ML/FP Pure**   | Haskell, Elm, Roc        | Immutable by default, ADTs, pattern matching, pure functions  |
| **ML/FP Hybrid** | F#, Scala, OCaml         | ML core + OOP escape hatch, modules, type classes             |
| **BEAM**         | Erlang, Elixir           | Actor model, supervision trees, hot code reload, OTP patterns |
| **LISP**         | Clojure, Racket          | Homoiconicity, macros, persistent data structures             |
| **Systems**      | Rust, C, C++             | Manual memory, lifetimes/ownership, low-level control         |
| **Managed OOP**  | Java, C#, Kotlin         | GC, classes, interfaces, exceptions                           |
| **Dynamic**      | Python, TypeScript, Ruby | Duck typing, runtime flexibility, reflection                  |

### 3.4 Cross-Family Conversion Strategy

For conversions between families (e.g., Python→Roc, Scala→Rust):

#### Step 1: Source Analysis

- Extract IR from source language
- Identify patterns that don't map directly to target family
- Flag incompatible idioms (e.g., mutation in source → immutable target)

#### Step 2: Pattern Translation Rules

| Source Pattern | Target Family: ML/FP  | Target Family: Systems  |
| -------------- | --------------------- | ----------------------- |
| Mutable state  | State monad / ST      | Owned mutable / RefCell |
| Exceptions     | Result/Either types   | Result<T, E>            |
| Inheritance    | Type classes / traits | Traits / composition    |
| Null/None      | Option type           | Option<T>               |
| Dynamic typing | Phantom types / GADTs | Generic bounds          |

#### Step 3: Target Synthesis

- Apply target language idioms
- Generate idiomatic code (not literal translation)
- Preserve semantics while embracing target conventions

### 3.5 Merged Skill Architecture

```asciidoc
context/skills/
├── codebase-analysis/                        # Core-skill for building IR of Codebase
│   ├── reference/                            # 
│   │   ├── meta.md                           # Orchestrates the conversion process
│   │   ├── ir/                               # Intermediate representation definition
│   │   │   ├── schema.md                     # IR schema
│   │   │   ├── guidelines.md                 # IR extraction guidelines
│   │   │   └── tools.md                      # IR extraction tools
│   │   ├── families/                         # Source analysis by family
│   │   │   ├── ml-fp/                        # 
│   │   │   │   ├── haskell.md                # 
│   │   │   │   ├── elm.md                    # 
│   │   │   │   ├── roc.md                    # 
│   │   │   │   ├── fsharp.md                 # 
│   │   │   │   └── scala.md                  # 
│   │   │   ├── beam/                         # 
│   │   │   │   ├── erlang.md                 # 
│   │   │   │   └── elixir.md                 # 
│   │   │   ├── lisp/                         # 
│   │   │   │   └── clojure.md                # 
│   │   │   ├── systems/                      # 
│   │   │   │   ├── rust.md                   # 
│   │   │   │   ├── c.md                      # 
│   │   │   │   ├── cpp.md                    # 
│   │   │   │   └── go.md                     # 
│   │   │   └── tools.md                      # 
│   │   └── patterns/                         # Common pattern translations
│   │       ├── error-handling.md             # 
│   │       ├── concurrency.md                # 
│   │       ├── state-management.md           # 
│   │       └── type-mappings.md              #
│   └── SKILL.md                              # Orchestrates the conversion process
│
└── codebase-implement-from-ir/               # How to use IR to synthesize codebase scaffolding for target language; hand off to individual 'idiomatic-<lang>' skill
    ├── reference/
    │   ├── rust/                             # Convert IR -> Rust Scaffolding
    │   │   ├── error-handling.md             # 
    │   │   ├── concurrency.md                # 
    │   │   ├── state-management.md           # 
    │   │   ├── type-mappings.md              # 
    │   │   ├── data-structures.md            # 
    │   │   ├── data-structures.md            # 
    │   │   ├── guidelines.md                 # 
    │   │   └── tools.md                      # 
    │   ├── roc/                              # Convert IR -> Roc Scaffolding
    │   │   ├── error-handling.md             # 
    │   │   ├── concurrency.md                # 
    │   │   ├── state-management.md           # 
    │   │   ├── type-mappings.md              # 
    │   │   ├── data-structures.md            # 
    │   │   ├── data-structures.md            # 
    │   │   ├── guidelines.md                 # 
    │   │   └── tools.md                      # 
    │   ├── elixir/                           # Convert IR -> Elixir Scaffolding
    │   │   ├── error-handling.md             # 
    │   │   ├── concurrency.md                # 
    │   │   ├── state-management.md           # 
    │   │   ├── type-mappings.md              # 
    │   │   ├── data-structures.md            # 
    │   │   ├── data-structures.md            # 
    │   │   ├── guidelines.md                 # 
    │   │   └── tools.md                      # 
    │   └── .../                              # 
    └── SKILL.md                              # Orchestrates the conversion process
```

## 4. Recommended Merge Path

### Phase 1: Merge Bidirectional Pairs (29 → 29 skills)

- Combine A↔B skills into single bidirectional skills
- Reduces 58 skills to 29
- Minimal content loss (>0.88 similarity on all pairs)

### Phase 2: Create Family Analyzers (29 + 5 = 34 skills)

- Extract common source analysis patterns
- Group by language family
- Create 5 family analyzer skills

### Phase 3: Create Target Synthesizers (34 → ~20 skills)

- One skill per target language
- Consolidate from current ~11 target groups
- Include cross-family pattern translations

### Phase 4: Create IR and Meta Skills (20 + 3 = 23 skills)

- `convert-meta`: Orchestration and workflow
- `convert-ir`: IR schema and validation
- `convert-patterns`: Common translation patterns

### Final Count: ~23 skills (down from 78)

- **70% reduction** in skill count
- **Better maintainability** — changes to shared logic propagate
- **Cross-family support** — any source → any target via IR

## 5. Implementation Notes

### Skill Inheritance Pattern

```markdown
## <!-- In convert-synthesize-rust/SKILL.md -->

parent: convert-meta
uses:

- convert-ir
- convert-analyze-\*
- convert-patterns

---

# Rust Code Synthesis

This skill synthesizes Rust code from the intermediate representation.

## Prerequisites

- Ensure IR extraction has completed (see: convert-ir)
- Review source analysis (see: convert-analyze-{source-family})

## Synthesis Rules

...
```

### Cross-Reference Example

For `python → roc` conversion:

1. Load `convert-meta` (orchestration)
2. Load `convert-analyze-dynamic` (Python analysis)
3. Extract IR using `convert-ir` patterns
4. Apply `convert-patterns/type-mappings` (dynamic → static)
5. Synthesize using `convert-synthesize-roc`

## 6. Post-Merge Analysis (49 Skills)

After Phase 1 merge, the landscape changed significantly:

### Skill Distribution by Family

| Family | As Source | As Target | Key Languages |
|--------|-----------|-----------|---------------|
| ML-FP | 5 langs, 12 skills | 5 targets, 29 skills | haskell, elm, roc, fsharp, scala |
| BEAM | 2 langs, 10 skills | 2 targets, 6 skills | erlang, elixir |
| Dynamic | 2 langs, 13 skills | 2 targets, 2 skills | python, typescript |
| Systems | 4 langs, 5 skills | 4 targets, 11 skills | rust, c, cpp, golang |
| LISP | 1 lang, 7 skills | 1 target, 1 skill | clojure |
| JVM-OOP | 1 lang, 3 skills | 0 targets | java |
| Apple | 1 lang, 1 skill | 1 target, 1 skill | objc→swift |

### Target Synthesis Similarity Scores

These scores indicate how similar all "convert-*-{target}" skills are. Higher = more shared template potential.

| Target | Similarity | Sources | Template Potential |
|--------|------------|---------|-------------------|
| clojure | 1.000 | 1 | N/A (single source) |
| erlang | 0.846 | 4 | ★★★ High |
| elm | 0.846 | 3 | ★★★ High |
| haskell | 0.841 | 6 | ★★★ High |
| cpp | 0.829 | 2 | ★★★ High |
| golang | 0.826 | 2 | ★★★ High |
| scala | 0.822 | 8 | ★★★ High |
| rust | 0.802 | 6 | ★★ Medium |
| roc | 0.788 | 7 | ★★ Medium |
| fsharp | 0.780 | 5 | ★★ Medium |
| elixir | 0.722 | 2 | ★ Lower |

### Cross-Family Coverage

```
Within-family conversions: 17
Cross-family conversions:  32

Cross-family breakdown:
  beam → ml-fp:     9 skills (dense coverage)
  lisp → ml-fp:     5 skills
  dynamic → ml-fp:  5 skills
  dynamic → systems: 4 skills
  jvm-oop → systems: 3 skills
  dynamic → beam:   2 skills
  lisp → beam:      2 skills
  dynamic → lisp:   1 skill
  ml-fp → beam:     1 skill
```

### Key Observations

1. **Python is the universal source** — 11 targets, touches all families
2. **Scala is the universal target** — 8 sources, highest cross-family coverage
3. **Rust is the systems-family hub** — 6 sources converge here
4. **ML-FP forms a dense cluster** — High internal connectivity
5. **Gaps exist**: No jvm-oop targets, limited apple coverage

---

## Appendix: Raw Data

### A. All Bidirectional Pairs

```asciidoc
fsharp ↔ roc:     0.994
elm ↔ roc:        0.989
clojure ↔ fsharp: 0.985
roc ↔ scala:      0.985
erlang ↔ roc:     0.974
elixir ↔ erlang:  0.972
fsharp ↔ scala:   0.967
elm ↔ scala:      0.967
clojure ↔ haskell:0.962
haskell ↔ scala:  0.957
clojure ↔ erlang: 0.947
elm ↔ fsharp:     0.945
clojure ↔ elm:    0.945
haskell ↔ roc:    0.944
elixir ↔ haskell: 0.940
clojure ↔ elixir: 0.936
elixir ↔ elm:     0.935
elixir ↔ scala:   0.934
python ↔ typescript: 0.934
elm ↔ haskell:    0.930
elixir ↔ fsharp:  0.926
clojure ↔ roc:    0.925
elixir ↔ roc:     0.924
fsharp ↔ haskell: 0.919
erlang ↔ fsharp:  0.919
clojure ↔ scala:  0.918
erlang ↔ scala:   0.913
erlang ↔ haskell: 0.901
elm ↔ erlang:     0.888
```

### B. Target Group Members

| Target  | Source Languages                                             |
| ------- | ------------------------------------------------------------ |
| clojure | elixir, elm, erlang, fsharp, haskell, python, roc, scala     |
| elixir  | clojure, elm, erlang, fsharp, haskell, python, roc, scala    |
| elm     | clojure, elixir, erlang, fsharp, haskell, python, roc, scala |
| erlang  | clojure, elixir, elm, fsharp, haskell, python, roc, scala    |
| fsharp  | clojure, elixir, elm, erlang, haskell, python, roc, scala    |
| haskell | clojure, elixir, elm, erlang, fsharp, python, roc, scala     |
| roc     | clojure, elixir, elm, erlang, fsharp, haskell, python, scala |
| scala   | clojure, elixir, elm, erlang, fsharp, haskell, python, roc   |
| rust    | c, cpp, golang, java, python, typescript                     |
| cpp     | c, java                                                      |
| golang  | python, typescript                                           |
