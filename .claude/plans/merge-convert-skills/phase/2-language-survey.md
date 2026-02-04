# Phase 2: Language Survey

Catalog languages with family classification and detailed feature profiles.

## Goal

Create comprehensive profiles for all languages in the conversion ecosystem, enabling accurate IR extraction and synthesis.

## Dependencies

- Phase 1: Language Families (for classification)

## Deliverables

- [ ] `docs/src/languages/{language}.md` - Per-language profiles
- [ ] `data/languages.sql` - SQL dump of language data
- [ ] `analysis/coverage-gaps.md` - Convert-* skill coverage analysis

## Tasks

### 2.1 Language Prioritization

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

### 2.2 Per-Language Profile Template

For each Tier 1-2 language, create a profile:

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

syntax:
  function_def: "fn name(params) -> ReturnType { body }"
  type_def: "struct Name { fields } | enum Name { variants }"
  module_def: "mod name { ... }"
  import: "use crate::path::item;"

semantic_gaps:
  - "No runtime reflection"
  - "No exceptions (must use Result)"
  - "Ownership rules may require restructuring"
  - "No inheritance (trait-based polymorphism)"
```

### 2.3 Convert-* Skill Coverage

Map existing skills to languages:

| Language | As Source | As Target | Missing Pairs |
|----------|-----------|-----------|---------------|
| python | 11 skills | 1 skill | No ruby→python, no js→python |
| rust | 0 skills | 6 skills | No rust→anything |
| scala | 0 skills | 8 skills | No scala→anything |
| roc | 0 skills | 6 skills | No roc→anything |
| ... | ... | ... | ... |

### 2.4 Language Documentation Template

```markdown
# {Language Name}

## Overview
Brief description of the language and its primary use cases.

## Family Classification
| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Paradigm | ... | ... |
| Typing | ... | ... |
| Memory | ... | ... |
| Execution | ... | ... |
| Effects | ... | ... |
| Concurrency | ... | ... |

## Feature Profile

### Type System
- Strength: ...
- Inference: ...
- Generics: ...
- Nullability: ...

### Memory Model
- Management: ...
- Mutability: ...
- Allocation: ...

### Control Flow
- Structured control: ...
- Effects: ...
- Async model: ...

### Data Types
- Primitives: ...
- Composites: ...
- Collections: ...
- Abstraction: ...

### Metaprogramming
- Macros: ...
- Reflection: ...
- Code generation: ...

## Syntax Patterns
Key syntax patterns for IR extraction.

## Semantic Gaps
What concepts are missing or different.

## Convert-* Coverage
| Direction | Skills | Notes |
|-----------|--------|-------|
| As Source | ... | ... |
| As Target | ... | ... |

## Idiomatic Patterns
Common patterns in this language.

## See Also
- Related languages
- Family documentation
```

## SQL Schema for Languages

```sql
-- Languages
CREATE TABLE languages (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    version TEXT,
    tier INTEGER NOT NULL,  -- 1, 2, or 3
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Language-family relationships (many-to-many)
CREATE TABLE language_families (
    language_id INTEGER REFERENCES languages(id),
    family_id INTEGER REFERENCES families(id),
    is_primary BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (language_id, family_id)
);

-- Language features (EAV for flexibility)
CREATE TABLE language_features (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    dimension TEXT NOT NULL,  -- typing, memory, control, data, meta
    feature TEXT NOT NULL,
    value TEXT NOT NULL,
    notes TEXT
);

-- Language syntax patterns
CREATE TABLE language_syntax (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    pattern_name TEXT NOT NULL,  -- function_def, type_def, etc.
    pattern TEXT NOT NULL,
    notes TEXT
);

-- Language semantic gaps
CREATE TABLE language_gaps (
    id INTEGER PRIMARY KEY,
    language_id INTEGER REFERENCES languages(id),
    gap_description TEXT NOT NULL,
    severity TEXT,  -- minor, moderate, major
    workaround TEXT
);

-- Convert-* skill coverage
CREATE TABLE skill_coverage (
    id INTEGER PRIMARY KEY,
    source_lang_id INTEGER REFERENCES languages(id),
    target_lang_id INTEGER REFERENCES languages(id),
    skill_name TEXT,  -- NULL if no skill exists
    skill_path TEXT,
    notes TEXT,
    UNIQUE(source_lang_id, target_lang_id)
);
```

## Languages to Profile

### Tier 1 (from existing convert-* skills)
- [ ] python
- [ ] typescript
- [ ] java
- [ ] c
- [ ] cpp
- [ ] golang
- [ ] rust
- [ ] haskell
- [ ] elm
- [ ] roc
- [ ] fsharp
- [ ] scala
- [ ] erlang
- [ ] elixir
- [ ] clojure
- [ ] objc
- [ ] swift

### Tier 2 (high priority additions)
- [ ] kotlin
- [ ] ruby
- [ ] gleam
- [ ] zig

## Success Criteria

- [ ] All Tier 1 languages profiled
- [ ] At least 5 Tier 2 languages profiled
- [ ] Coverage gap analysis complete
- [ ] Each profile follows consistent template
- [ ] SQL data matches documentation

## Effort Estimate

5-7 days

## Output Files

| File | Description |
|------|-------------|
| `docs/src/languages/{language}.md` | Per-language profiles |
| `data/languages.sql` | SQL dump of language data |
| `analysis/coverage-gaps.md` | Skill coverage analysis |
