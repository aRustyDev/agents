# Phase 2: Language Survey

Catalog languages with family classification and detailed feature profiles.

## Goal

Create comprehensive profiles for all languages in the conversion ecosystem, enabling accurate IR extraction and synthesis.

## Dependencies

- **Phase 0: Pattern Extraction** (completed)
  - Required: `data/patterns.db` - extract language list from skill names
  - Required: `data/gap-analysis.json` - reference for coverage analysis
- **Phase 1: Language Families** (completed)
  - Required: `data/families/taxonomy.yaml` - family assignments
  - Required: `data/families/dimensions.yaml` - feature dimension templates
  - Required: `docs/src/language-families/*.md` - cross-linking

## Deliverables

- [ ] `docs/src/languages/{language}.md` - Per-language profiles (21 full + Tier 3 minimal)
- [ ] `data/languages.sql` - SQL dump extending Phase 1 schema
- [ ] `data/languages.yaml` - YAML profiles for all languages
- [ ] `analysis/coverage-gaps.md` - Convert-* skill coverage analysis

## Data Consumers

| Consumer | Timeline | Usage |
|----------|----------|-------|
| IR Extraction (Phase 4-5) | Immediate | Type mappings, semantic gaps, syntax patterns |
| Skill Generation | Long-term | Auto-generate convert-* skills for new language pairs |

## Tasks

### 2.0 Extract Languages from Phase 0

Before profiling, extract the authoritative language list from Phase 0 data.

**Process:**

```sql
-- Extract unique languages from patterns.db
SELECT DISTINCT
  CASE
    WHEN INSTR(SUBSTR(skill_name, 9), '-') > 0
    THEN SUBSTR(skill_name, 9, INSTR(SUBSTR(skill_name, 9), '-') - 1)
    ELSE SUBSTR(skill_name, 9)
  END as language
FROM patterns
UNION
SELECT DISTINCT
  SUBSTR(skill_name, 9 + INSTR(SUBSTR(skill_name, 9), '-')) as language
FROM patterns
WHERE INSTR(SUBSTR(skill_name, 9), '-') > 0
ORDER BY language;
```

**Output:** Verified language list for Tier 1

### 2.1 Language Prioritization

```
Tier 1 (Must Have): Languages in existing convert-* skills (18 languages)
  Source languages: python, typescript, javascript, java, c, cpp, golang
  Target languages: rust, haskell, elm, roc, fsharp, scala
  BEAM family: erlang, elixir
  LISP family: clojure
  Apple family: objc, swift

Tier 2 (Should Have): High-value additions (4 languages)
  - kotlin (Managed-OOP, Android)
  - gleam (BEAM, typed)
  - zig (Systems, modern)
  - ruby (Dynamic, Rails ecosystem)

Tier 3 (Minimal Profile): Historically significant
  - cobol, fortran, pascal, ada, lisp, scheme, prolog
  - Minimal profile: name, family, key characteristics only
```

**Note:** JavaScript and TypeScript are **separate profiles** (shared runtime, different type systems).

### 2.2 Version Policy

| Language Category | Version Policy | Examples |
|-------------------|----------------|----------|
| **Major languages** | Include historical versions with breaking changes | Python 2→3, Java 8→21, C89→C23 |
| **Other Tier 1** | Latest stable only | Rust 1.75, Haskell GHC 9.8 |
| **Tier 2** | Latest stable only | Gleam 1.0, Zig 0.13 |
| **Tier 3** | Representative version | COBOL-85, Fortran 2018 |

**Major languages requiring version history:**

- Python (2.7, 3.6+, 3.10+ for pattern matching)
- Java (8, 11, 17, 21 for records/patterns)
- C (C89, C99, C11, C23)
- C++ (C++11, C++17, C++20, C++23)

### 2.3 Data Sources

Each profile field requires authoritative sourcing:

| Field | Primary Source | Secondary Source |
|-------|----------------|------------------|
| Type system | Official language spec | Language reference docs |
| Memory model | Language spec / runtime docs | Implementation notes |
| Syntax patterns | Official grammar / BNF | Parser implementations |
| Popularity | TIOBE Index (monthly) | Stack Overflow Survey (annual) |
| Ecosystem | Official package registry | GitHub statistics |

**Freshness policy:** Popularity metrics are snapshots. Include `last_updated: YYYY-MM` in profiles.

### 2.4 Per-Language Profile Template (Full - Tier 1/2)

```yaml
language: rust
display_name: Rust
version: "1.75"
version_date: "2024-01"
last_updated: "2024-02"

# Cross-reference to Phase 1 taxonomy
family:
  primary: systems
  secondary: [ownership]
  subtype: ownership  # From taxonomy.yaml

# Popularity snapshot
popularity:
  tiobe_rank: 17
  tiobe_date: "2024-01"
  stackoverflow_loved: 87%
  stackoverflow_year: 2023
  github_repos: "2.1M"

# Feature dimensions (aligned with Phase 1 dimensions.yaml)
features:
  typing:
    strength: static
    inference: bidirectional
    generics: bounded
    nullability: non-null  # via Option<T>

  memory:
    model: ownership
    mutability: default-immutable
    allocation: stack-first
    lifetime_tracking: explicit

  control:
    structured: [if-else, match, loops]
    effects: result-types
    async: async-await

  data:
    primitives: [i8-i128, u8-u128, f32, f64, bool, char]
    composites: [arrays, tuples, structs, enums]
    collections: [Vec, HashMap, HashSet, BTreeMap]
    abstraction: [traits, modules]

  meta:
    macros: procedural
    reflection: none
    codegen: derive

# Tooling ecosystem
ecosystem:
  package_manager: cargo
  build_system: cargo
  lsp: rust-analyzer
  formatter: rustfmt
  linter: clippy
  repl: evcxr (third-party)
  test_framework: built-in (cargo test)

# Syntax patterns for IR extraction
syntax:
  function_def: "fn name(params) -> ReturnType { body }"
  type_def: "struct Name { fields } | enum Name { variants }"
  module_def: "mod name { ... }"
  import: "use crate::path::item;"
  error_handling: "Result<T, E> with ? operator"
  async_def: "async fn name() -> T { ... }"

# Semantic gaps for conversion
semantic_gaps:
  - description: "No runtime reflection"
    severity: moderate
    workaround: "Use derive macros for compile-time reflection"
  - description: "No exceptions (must use Result)"
    severity: major
    workaround: "Convert try/catch to Result propagation with ?"
  - description: "Ownership rules may require restructuring"
    severity: major
    workaround: "Analyze ownership patterns, use Rc/Arc for shared ownership"
  - description: "No inheritance (trait-based polymorphism)"
    severity: moderate
    workaround: "Convert class hierarchies to trait + composition"

# Data sources for verification
sources:
  - url: "https://doc.rust-lang.org/reference/"
    description: "Official Rust Reference"
  - url: "https://doc.rust-lang.org/book/"
    description: "The Rust Programming Language"
```

### 2.5 Minimal Profile Template (Tier 3)

```yaml
language: cobol
display_name: COBOL
version: "COBOL-85"
tier: 3

family:
  primary: procedural

characteristics:
  typing: static
  memory: manual
  execution: compiled
  paradigm: procedural

notes: |
  Historically significant for business/financial systems.
  Conversion considerations: Fixed-width records, PICTURE clauses,
  division structure (IDENTIFICATION, ENVIRONMENT, DATA, PROCEDURE).

see_also:
  - family: procedural
```

### 2.6 Convert-* Skill Coverage Analysis

Leverage Phase 0 data instead of recreating:

**Process:**

1. Query `data/patterns.db` for all skill names
2. Parse source/target languages from skill names
3. Cross-reference with `data/gap-analysis.json` for semantic gaps
4. Build coverage matrix

**Output format:**

| Language | As Source | As Target | Bidirectional | Missing High-Value Pairs |
|----------|-----------|-----------|---------------|--------------------------|
| python | 11 | 1 | 1 (typescript) | ruby→python, javascript→python |
| rust | 0 | 6 | 0 | rust→python, rust→typescript |
| scala | 0 | 8 | 0 | scala→kotlin, scala→java |
| javascript | 0 | 0 | 0 | javascript→typescript, python→javascript |

### 2.7 Language Documentation Template

```markdown
# {Language Name}

> One-line summary for quick reference.

## Overview

Brief description (2-3 paragraphs): history, primary use cases, notable features.

## Family Classification

From Phase 1 taxonomy:

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | {from taxonomy.yaml} | |
| Subtype | {if applicable} | |
| Secondary Families | {if applicable} | |

See: [Family Documentation](../language-families/{family}.md)

## Version History (Major Languages Only)

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| ... | ... | ... |

## Feature Profile

### Type System

- **Strength:** static | dynamic | gradual
- **Inference:** none | local | global | bidirectional
- **Generics:** none | parametric | bounded | higher-kinded
- **Nullability:** nullable | optional | non-null

### Memory Model

- **Management:** manual | gc | rc | ownership
- **Mutability:** default-mutable | default-immutable
- **Allocation:** stack | heap | automatic

### Control Flow

- **Structured:** if-else, loops, match, guards
- **Effects:** exceptions | result-types | monadic | algebraic
- **Async:** callbacks | promises | async-await | actors

### Data Types

- **Primitives:** ...
- **Composites:** arrays, tuples, structs, enums, classes
- **Collections:** ...
- **Abstraction:** modules | classes | traits | typeclasses

### Metaprogramming

- **Macros:** none | text | syntactic | hygienic | procedural
- **Reflection:** none | runtime | compile-time
- **Code generation:** none | templates | derive

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | ... | |
| Build System | ... | |
| LSP | ... | |
| Formatter | ... | |
| Linter | ... | |
| REPL | ... | |

## Syntax Patterns

Key patterns for IR extraction:

```{language}
// Function definition
...

// Type definition
...

// Error handling
...
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| ... | minor/moderate/major | ... |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | N | convert-{lang}-X, ... |
| As Target | N | convert-X-{lang}, ... |

**Missing high-value pairs:** ...

## Idiomatic Patterns

Common patterns and their IR representation.

## Related Languages

- **Influenced by:** ...
- **Influenced:** ...
- **Compiles to:** ... (if applicable)
- **FFI compatible:** ...

## Sources

- [Official Documentation](url)
- [Language Specification](url)

## See Also

- [Family: {family}](../language-families/{family}.md)
- Related language profiles
```

## SQL Schema Extension

Extend Phase 1 schema rather than duplicating:

```sql
-- Extend Phase 1 languages table
ALTER TABLE languages ADD COLUMN version TEXT;
ALTER TABLE languages ADD COLUMN version_date TEXT;
ALTER TABLE languages ADD COLUMN tier INTEGER NOT NULL DEFAULT 3;
ALTER TABLE languages ADD COLUMN last_updated TEXT;

-- Language version history (major languages only)
CREATE TABLE language_versions (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    version TEXT NOT NULL,
    release_date TEXT,
    key_changes TEXT,  -- JSON array of conversion-relevant changes
    is_current BOOLEAN DEFAULT FALSE,
    UNIQUE(language_id, version)
);

-- Language ecosystem/tooling
CREATE TABLE language_ecosystem (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    tool_type TEXT NOT NULL,  -- package_manager, build_system, lsp, formatter, linter, repl
    tool_name TEXT NOT NULL,
    is_official BOOLEAN DEFAULT TRUE,
    notes TEXT,
    UNIQUE(language_id, tool_type, tool_name)
);

-- Language popularity snapshots
CREATE TABLE language_popularity (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    source TEXT NOT NULL,  -- tiobe, stackoverflow, github
    metric TEXT NOT NULL,  -- rank, loved_pct, repo_count
    value TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    UNIQUE(language_id, source, metric, snapshot_date)
);

-- Language relationships
CREATE TABLE language_relationships (
    id INTEGER PRIMARY KEY,
    from_language_id INTEGER REFERENCES languages(id),
    to_language_id INTEGER REFERENCES languages(id),
    relationship_type TEXT NOT NULL,  -- influenced_by, compiles_to, ffi_compatible
    notes TEXT,
    UNIQUE(from_language_id, to_language_id, relationship_type)
);

-- Reuse Phase 1 tables:
-- - language_families (already exists)
-- - language_features (EAV, already exists)
-- - language_gaps (already exists)
-- - language_syntax (already exists)
```

## Languages to Profile

### Tier 1: Full Profiles (18 languages)

**Dynamic Family:**

- [ ] python (+ version history: 2.7, 3.6, 3.10)
- [ ] javascript
- [ ] typescript

**ML-FP Family:**

- [ ] haskell
- [ ] elm
- [ ] roc
- [ ] fsharp
- [ ] scala

**Systems Family:**

- [ ] rust
- [ ] c (+ version history: C89, C99, C11, C23)
- [ ] cpp (+ version history: C++11, C++17, C++20)
- [ ] golang

**BEAM Family:**

- [ ] erlang
- [ ] elixir

**LISP Family:**

- [ ] clojure

**Managed-OOP Family:**

- [ ] java (+ version history: 8, 11, 17, 21)

**Apple Family:**

- [ ] objc
- [ ] swift

### Tier 2: Full Profiles (4 languages)

- [ ] kotlin
- [ ] gleam
- [ ] zig
- [ ] ruby

### Tier 3: Minimal Profiles

- [ ] cobol
- [ ] fortran
- [ ] pascal
- [ ] ada
- [ ] lisp (Common Lisp)
- [ ] scheme
- [ ] prolog

## Success Criteria

- [ ] All 18 Tier 1 languages profiled with full template
- [ ] All 4 Tier 2 languages profiled with full template
- [ ] All 7 Tier 3 languages profiled with minimal template
- [ ] Version history documented for major languages (Python, Java, C, C++)
- [ ] Coverage gap analysis complete (referencing Phase 0 data)
- [ ] Each profile cross-references Phase 1 family taxonomy
- [ ] SQL data extends Phase 1 schema (no duplication)
- [ ] Ecosystem/tooling documented for Tier 1-2

## Effort Estimate

**10-14 days** (extended from 5-7 to accommodate 22 full + 7 minimal profiles)

| Task | Effort | Notes |
|------|--------|-------|
| 2.0 Extract languages | 0.5 days | SQL queries on patterns.db |
| 2.1-2.3 Setup & data sources | 1 day | Establish templates, sources |
| 2.4 Tier 1 profiles (18) | 6 days | ~3 profiles/day |
| 2.5 Tier 2 profiles (4) | 1.5 days | ~3 profiles/day |
| 2.6 Tier 3 minimal (7) | 1 day | ~7 minimal/day |
| 2.7 Coverage analysis | 1 day | Query Phase 0, build matrix |
| SQL schema & data load | 1 day | Extend schema, populate |
| Review & cross-reference | 1 day | Verify Phase 1 alignment |
| Buffer | 1 day | |

**Parallelization:** Tier 1 profiles can be done in parallel by family grouping.

## Output Files

| File | Description |
|------|-------------|
| `docs/src/languages/{language}.md` | Per-language profiles (22 full + 7 minimal) |
| `data/languages.yaml` | YAML profiles for programmatic access |
| `data/languages.sql` | SQL dump extending Phase 1 schema |
| `analysis/coverage-gaps.md` | Skill coverage analysis |

## Quality Gates

| Gate | Criteria |
|------|----------|
| Profile completeness | All required fields populated |
| Family alignment | Primary family matches taxonomy.yaml |
| Source attribution | At least 2 authoritative sources per profile |
| Cross-reference | Links to family docs valid |
| SQL consistency | Data matches markdown docs |

## Notes

- JavaScript and TypeScript are **separate profiles** despite shared runtime
- Popularity metrics are **snapshots** with explicit dates
- Version history is limited to **conversion-relevant changes** (not exhaustive changelog)
- Ecosystem tooling focuses on **developer workflow** tools, not libraries
- SQL schema **extends** Phase 1, tables are additive not replacing
