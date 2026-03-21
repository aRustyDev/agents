# Phase 6: Consolidation

Merge all findings into a unified IR and skill architecture.

## Goal

Synthesize all research and validation into the final IR specification and restructured skill system.

## Dependencies

- Phase 5: Validation & Tooling (all validation must pass)

## Deliverables

- [ ] Final IR specification
- [ ] Updated skill architecture
- [ ] Migration plan for existing convert-* skills
- [ ] Documentation site

## Tasks

### 6.1 Pattern Consolidation

Analyze all findings to categorize patterns:

| Category | Description | Treatment |
|----------|-------------|-----------|
| **Universal** | Applies to all languages | Core IR primitives |
| **Family** | Shared within a family | Family IR extensions |
| **Language** | Unique to a language | Language-specific annotations |

```yaml
consolidated_patterns:
  universal:
    - name: "function_definition"
      ir_construct: "FunctionIR"
      applies_to: "all"

    - name: "type_alias"
      ir_construct: "TypeIR.alias"
      applies_to: "all"

  family:
    ml_fp:
      - name: "pattern_matching"
        ir_construct: "MatchExpression"
        fallback: "switch/if-else chain"

      - name: "algebraic_data_types"
        ir_construct: "TypeIR.enum"
        fallback: "class hierarchy"

    beam:
      - name: "actor_process"
        ir_construct: "ConcurrencyIR.actor"
        fallback: "thread + queue"

  language:
    rust:
      - name: "ownership"
        ir_construct: "OwnershipAnnotation"
        conversion: "must infer or restructure"

    haskell:
      - name: "higher_kinded_types"
        ir_construct: "TypeIR.hkt"
        conversion: "monomorphize"
```

### 6.2 Abstract IR Design

Create the minimal abstract IR that supports all patterns:

```yaml
abstract_ir:
  version: "1.0"

  core:
    # Always present
    - ModuleIR
    - TypeIR (primitive, composite, function)
    - FunctionIR
    - ExpressionIR
    - BindingIR

  extensions:
    # Enabled per-family
    pattern_matching:
      enabled_for: [ml_fp, beam]
      ir_constructs: [MatchExpression, Pattern]

    ownership:
      enabled_for: [systems]
      ir_constructs: [OwnershipAnnotation, Lifetime, BorrowKind]

    actors:
      enabled_for: [beam]
      ir_constructs: [ActorDef, Message, Spawn, Send, Receive]

    effects:
      enabled_for: [ml_fp, beam]
      ir_constructs: [EffectAnnotation, EffectHandler]
```

### 6.3 Final Skill Architecture

```
context/skills/
├── codebase-analysis/
│   ├── SKILL.md                    # Main analysis skill
│   └── reference/
│       ├── ir/
│       │   ├── overview.md         # IR architecture
│       │   ├── schema.md           # Full schema reference
│       │   ├── extraction-guide.md # How to extract IR
│       │   └── tools.md            # Tool usage
│       ├── families/
│       │   ├── overview.md         # Family comparison
│       │   ├── ml-fp.md
│       │   ├── beam.md
│       │   ├── lisp.md
│       │   ├── systems.md
│       │   ├── managed-oop.md
│       │   ├── dynamic.md
│       │   └── ...
│       └── languages/
│           ├── python.md
│           ├── rust.md
│           ├── typescript.md
│           └── ...
│
├── codebase-implement-from-ir/
│   ├── SKILL.md                    # Main synthesis skill
│   └── reference/
│       ├── synthesis-guide.md      # How to synthesize from IR
│       ├── patterns/
│       │   ├── error-handling.md   # Error handling patterns
│       │   ├── concurrency.md      # Concurrency patterns
│       │   ├── data-structures.md  # Data structure mappings
│       │   └── ...
│       └── targets/
│           ├── rust/
│           │   ├── idioms.md
│           │   ├── ownership.md
│           │   └── examples/
│           ├── python/
│           ├── typescript/
│           └── ...
│
├── idiomatic-rust/
│   └── SKILL.md                    # Rust-specific idioms
│
├── idiomatic-python/
│   └── SKILL.md                    # Python-specific idioms
│
└── ...                             # Other idiomatic-* skills
```

### 6.4 Skill Content Templates

#### codebase-analysis SKILL.md

```markdown
---
name: Codebase Analysis
version: 1.0.0
description: Extract IR from source code for cross-language conversion
category: conversion
languages: [python, typescript, rust, java, go, ...]
---

# Codebase Analysis

Extract an Intermediate Representation (IR) from source code to enable
cross-language conversion and analysis.

## Usage

\`\`\`
/codebase-analysis <path> [--language <lang>] [--depth <0-4>]
\`\`\`

## Process

1. **Module Discovery**: Identify all modules and their relationships
2. **Type Extraction**: Extract type definitions and relationships
3. **Function Analysis**: Extract function signatures and control flow
4. **Semantic Annotation**: Infer purity, nullability, effects
5. **Gap Detection**: Mark concepts that may not convert cleanly

## Output

Produces an IR representation at the specified depth level:
- Level 0: Expression-level AST
- Level 1: Data flow graph
- Level 2: Control flow graph
- Level 3: Type relationships
- Level 4: Module structure

## Reference

- [IR Schema](reference/ir/schema.md)
- [Extraction Guide](reference/ir/extraction-guide.md)
- [Language Families](reference/families/overview.md)
```

#### codebase-implement-from-ir SKILL.md

```markdown
---
name: Implement from IR
version: 1.0.0
description: Synthesize target language code from IR
category: conversion
languages: [python, typescript, rust, java, go, ...]
---

# Implement from IR

Generate idiomatic code in a target language from an Intermediate
Representation (IR).

## Usage

\`\`\`
/codebase-implement-from-ir <ir-path> --target <language>
\`\`\`

## Process

1. **Gap Resolution**: Review detected gaps and apply mitigations
2. **Pattern Translation**: Map IR patterns to target idioms
3. **Code Generation**: Generate syntactically correct code
4. **Idiom Application**: Apply target-language conventions
5. **Formatting**: Format code with target's standard tools

## Semantic Preservation

Target levels (in order of priority):
1. **Semantically Equivalent**: Same observable behavior
2. **Idiomatically Correct**: Follows target conventions
3. **Optimized**: Efficient for target platform

## Reference

- [Synthesis Guide](reference/synthesis-guide.md)
- [Pattern Translations](reference/patterns/)
- [Target Languages](reference/targets/)
```

### 6.5 Migration Plan

| Current Skill | Action | New Location |
|---------------|--------|--------------|
| convert-python-rust | Migrate patterns | `codebase-implement-from-ir/reference/targets/rust/` |
| convert-python-scala | Migrate patterns | `codebase-implement-from-ir/reference/targets/scala/` |
| convert-python-* (all 11) | Extract common patterns | `codebase-analysis/reference/languages/python.md` |
| convert-*-rust (all 6) | Extract common patterns | `codebase-implement-from-ir/reference/targets/rust/` |
| ... | ... | ... |

### 6.6 Documentation Site Structure

```
docs/src/
├── index.md                    # Home page
├── getting-started/
│   ├── quick-start.md
│   ├── installation.md
│   └── first-conversion.md
├── concepts/
│   ├── ir-overview.md
│   ├── language-families.md
│   ├── semantic-gaps.md
│   └── preservation-levels.md
├── ir-schema/
│   ├── overview.md
│   ├── layer-0.md
│   ├── layer-1.md
│   ├── layer-2.md
│   ├── layer-3.md
│   └── layer-4.md
├── language-families/
│   ├── overview.md
│   └── {family}.md
├── languages/
│   ├── overview.md
│   └── {language}.md
├── patterns/
│   ├── overview.md
│   ├── type-system.md
│   ├── error-handling.md
│   ├── concurrency.md
│   └── data-structures.md
├── tools/
│   ├── overview.md
│   ├── ir-extract.md
│   ├── ir-synthesize.md
│   └── ir-validate.md
└── reference/
    ├── schema.md
    ├── api.md
    └── faq.md
```

## Success Criteria

- [ ] Final IR specification reviewed and approved
- [ ] Skill architecture implemented
- [ ] All 49 convert-* skills migrated or deprecated
- [ ] Documentation site deployed
- [ ] Migration guide complete

## Effort Estimate

3-5 days

## Output Files

| File | Description |
|------|-------------|
| `docs/src/` | Full documentation site |
| `context/skills/codebase-analysis/` | Analysis skill |
| `context/skills/codebase-implement-from-ir/` | Synthesis skill |
| `context/skills/idiomatic-*/` | Language-specific skills |
| `analysis/migration-report.md` | Migration completion report |
