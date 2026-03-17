# Migration Plan: convert-* Skills to IR-Based Architecture

## Overview

This plan describes how to migrate the existing 49 `convert-*` skills to the new IR-based architecture with two central skills:
- `codebase-analysis` - Extract IR from source
- `codebase-implement-from-ir` - Synthesize target code

## Current State

### Existing Skills

| Prefix | Count | Examples |
|--------|-------|----------|
| `convert-python-*` | 11 | rust, go, typescript, scala, java, etc. |
| `convert-*-rust` | 6 | python, go, typescript, java, etc. |
| `convert-*-python` | 5 | rust, go, typescript, java, etc. |
| `convert-*-go` | 4 | python, rust, typescript, etc. |
| `convert-*-typescript` | 4 | python, rust, go, etc. |
| `convert-*-*` (other) | 19 | various pairs |

**Total: 49 skills**

### Problems with Current Structure

1. **Quadratic Growth**: N languages requires N×(N-1) skills
2. **Duplication**: Same patterns repeated in multiple skills
3. **Inconsistency**: Different approaches for same concept
4. **Maintenance**: Updates must be applied to multiple files

## Target State

### New Architecture

```
context/skills/
├── codebase-analysis/           # Single extraction skill
│   ├── SKILL.md
│   └── reference/
│       ├── ir/                  # IR specification
│       ├── families/            # Family documentation
│       └── languages/           # Language-specific extraction
│
├── codebase-implement-from-ir/  # Single synthesis skill
│   ├── SKILL.md
│   └── reference/
│       ├── synthesis-guide.md
│       ├── patterns/            # Pattern translations
│       └── targets/             # Target-specific idioms
│
└── idiomatic-*/                 # Language-specific idiom skills
    └── SKILL.md
```

### Benefits

1. **Linear Growth**: N languages requires 2N components (N extractors + N synthesizers)
2. **Single Source**: Patterns documented once
3. **Consistency**: Shared IR ensures uniform treatment
4. **Maintainability**: Updates in one place

## Migration Strategy

### Phase 1: Parallel Operation

Run new and old skills in parallel:

1. Keep existing `convert-*` skills unchanged
2. Deploy new IR-based skills
3. Compare outputs for test cases
4. Gather feedback on new approach

**Duration**: 2-4 weeks

### Phase 2: Pattern Extraction

Extract patterns from existing skills into reference docs:

| Source Skill | Extract To | Content |
|--------------|------------|---------|
| `convert-python-rust` | `targets/rust/from-python.md` | Python→Rust patterns |
| `convert-python-go` | `targets/go/from-python.md` | Python→Go patterns |
| `convert-rust-python` | `targets/python/from-rust.md` | Rust→Python patterns |
| ... | ... | ... |

**Work per skill**:
1. Identify unique patterns
2. Document in target reference
3. Verify coverage in IR tools

**Duration**: 1-2 weeks

### Phase 3: Deprecation

Deprecate old skills with migration guide:

```markdown
---
deprecated: true
replacement: codebase-analysis + codebase-implement-from-ir
---

# convert-python-rust (DEPRECATED)

This skill has been replaced by the IR-based conversion workflow.

## Migration

Instead of:
\`\`\`
/convert-python-rust src/main.py
\`\`\`

Use:
\`\`\`
/codebase-analysis src/main.py
/codebase-implement-from-ir output/main.ir.json --target rust
\`\`\`
```

**Duration**: 1 week

### Phase 4: Removal

After deprecation period, remove old skills:

1. Archive skill content (git history preserved)
2. Remove skill files
3. Update documentation
4. Update indexes

**Duration**: 1 week

## Pattern Migration Table

### Python Source Patterns

| Pattern | Current Location | New Location |
|---------|------------------|--------------|
| Decorator handling | `convert-python-*.md` | `languages/python.md` |
| Type hint extraction | `convert-python-*.md` | `languages/python.md` |
| Dataclass → struct | `convert-python-rust.md` | `targets/rust/idioms.md` |
| Exception → Result | `convert-python-rust.md` | `patterns/error-handling.md` |
| Generator → Iterator | `convert-python-rust.md` | `patterns/iteration.md` |

### Rust Source Patterns

| Pattern | Current Location | New Location |
|---------|------------------|--------------|
| Ownership semantics | `convert-rust-*.md` | `languages/rust.md` |
| Lifetime handling | `convert-rust-*.md` | `languages/rust.md` |
| Result → Exception | `convert-rust-python.md` | `targets/python/idioms.md` |
| Enum → ADT | `convert-rust-*.md` | `patterns/data-structures.md` |
| Trait → Interface | `convert-rust-*.md` | `patterns/type-system.md` |

### TypeScript Source Patterns

| Pattern | Current Location | New Location |
|---------|------------------|--------------|
| Union types | `convert-typescript-*.md` | `languages/typescript.md` |
| Type guards | `convert-typescript-*.md` | `languages/typescript.md` |
| Interface → trait | `convert-typescript-rust.md` | `targets/rust/idioms.md` |
| null handling | `convert-typescript-*.md` | `patterns/nullability.md` |

### Go Source Patterns

| Pattern | Current Location | New Location |
|---------|------------------|--------------|
| Error returns | `convert-go-*.md` | `languages/go.md` |
| Interface satisfaction | `convert-go-*.md` | `languages/go.md` |
| Goroutines | `convert-go-*.md` | `patterns/concurrency.md` |
| Channels | `convert-go-*.md` | `patterns/concurrency.md` |

## Tooling Migration

### Extractor Tools

| Language | Tool Package | Status |
|----------|--------------|--------|
| Python | `ir-extract-python` | ✅ Complete |
| Rust | `ir-extract-rust` | ✅ Complete |
| TypeScript | `ir-extract-typescript` | ✅ Complete |
| Go | `ir-extract-go` | ✅ Complete |
| Scala | `ir-extract-scala` | ✅ Complete |
| Roc | `ir-extract-roc` | ✅ Complete |

### Synthesizer Tools

| Language | Tool Package | Status |
|----------|--------------|--------|
| Python | `ir-synthesize-python` | ✅ Complete |
| Rust | `ir-synthesize-rust` | ✅ Complete |
| TypeScript | `ir-synthesize-typescript` | ✅ Complete |
| Go | `ir-synthesize-go` | ✅ Complete |
| Scala | `ir-synthesize-scala` | ✅ Complete |
| Roc | `ir-synthesize-roc` | ✅ Complete |

## Rollback Plan

If issues arise during migration:

1. **Phase 1**: Simply continue using old skills
2. **Phase 2**: Patterns already extracted, no rollback needed
3. **Phase 3**: Remove deprecation notice, restore skill
4. **Phase 4**: Restore from git history

## Success Metrics

| Metric | Target |
|--------|--------|
| Skills reduced | 49 → 2 main + 6 idiomatic |
| Pattern coverage | 100% of documented patterns |
| Test pass rate | ≥95% |
| User adoption | ≥80% using new workflow after 30 days |
| Support tickets | ≤10% increase during transition |

## Timeline

| Week | Phase | Activities |
|------|-------|------------|
| 1-2 | Phase 1 | Deploy new skills, parallel testing |
| 3-4 | Phase 1 | Gather feedback, iterate |
| 5-6 | Phase 2 | Extract patterns from 25 skills |
| 7-8 | Phase 2 | Extract remaining patterns |
| 9 | Phase 3 | Add deprecation notices |
| 10 | Phase 4 | Remove old skills |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pattern loss | Medium | High | Thorough extraction, test coverage |
| User confusion | Medium | Medium | Clear migration docs, examples |
| Tool bugs | Medium | Medium | Parallel operation period |
| Performance regression | Low | Medium | Benchmark before/after |

## Appendix: Full Skill List

### To Be Deprecated

```
convert-python-rust
convert-python-go
convert-python-typescript
convert-python-java
convert-python-kotlin
convert-python-swift
convert-python-scala
convert-python-csharp
convert-python-cpp
convert-python-ruby
convert-python-elixir

convert-rust-python
convert-rust-go
convert-rust-typescript
convert-rust-java
convert-rust-kotlin
convert-rust-cpp

convert-go-python
convert-go-rust
convert-go-typescript
convert-go-java

convert-typescript-python
convert-typescript-rust
convert-typescript-go
convert-typescript-java

convert-java-python
convert-java-rust
convert-java-go
convert-java-typescript
convert-java-kotlin

convert-kotlin-python
convert-kotlin-java
convert-kotlin-swift

convert-swift-python
convert-swift-kotlin

convert-scala-python
convert-scala-java

convert-csharp-python
convert-csharp-java

convert-cpp-python
convert-cpp-rust

convert-ruby-python

convert-elixir-python

convert-haskell-python
convert-haskell-scala

convert-ocaml-python
convert-ocaml-rust

convert-fsharp-csharp
convert-fsharp-python
```

### New Skills

```
codebase-analysis
codebase-implement-from-ir
idiomatic-python
idiomatic-rust
idiomatic-typescript
idiomatic-go
idiomatic-scala
idiomatic-roc
```
