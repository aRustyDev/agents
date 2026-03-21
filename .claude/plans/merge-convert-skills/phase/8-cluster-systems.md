# Phase 8: Cluster C — Systems Convergence

**ID:** phase-8
**Status:** pending
**Beads:** ai-x3e.10

## Objective

Merge 9 systems-oriented convert-* skills into a single `meta-convert-cluster-systems-dev` skill. These skills involve C, C++, Rust, Go as source or target, with lower average similarity (0.802) requiring more careful pattern preservation — particularly around memory management, ownership, and systems-level concerns.

## Dependencies

- phase-6 (Cluster A: FP Internal) — establishes merge pattern

## Success Criteria

- [ ] Single `meta-convert-cluster-systems-dev/SKILL.md` covers all 9 source skills
- [ ] SKILL.md < 200 lines (progressive disclosure)
- [ ] Memory management / ownership patterns preserved with high fidelity
- [ ] Systems-specific concerns (unsafe code, FFI, ABI) documented in reference/
- [ ] Direction-specific sections kept where similarity < 0.80
- [ ] Round-trip validation passes for representative conversions

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Cluster skill | `context/skills/meta-convert-cluster-systems-dev/SKILL.md` | Merged systems conversion skill |
| Reference docs | `context/skills/meta-convert-cluster-systems-dev/reference/` | Per-pair and pattern docs |
| Validation report | `analysis/phase8-validation-report.md` | Merge quality assessment |

## Files

**Create:**
- `context/skills/meta-convert-cluster-systems-dev/SKILL.md`
- `context/skills/meta-convert-cluster-systems-dev/reference/memory-ownership.md` (C/C++/Rust memory patterns)
- `context/skills/meta-convert-cluster-systems-dev/reference/c-family.md` (C↔C++↔Rust)
- `context/skills/meta-convert-cluster-systems-dev/reference/dynamic-to-systems.md` (Python/TS/Java→systems)
- `context/skills/meta-convert-cluster-systems-dev/reference/go-patterns.md` (Go↔Rust, Go-specific)
- `analysis/phase8-validation-report.md`

**Modify:**
- `index.md` — Update phase-8 status to complete

## Source Skills (9)

| Skill | Source | Target | Key Concern |
|-------|--------|--------|-------------|
| convert-c-cpp | C | C++ | C++ superset patterns, RAII |
| convert-c-rust | C | Rust | Manual→ownership memory |
| convert-cpp-rust | C++ | Rust | RAII→ownership, templates→generics |
| convert-golang-rust | Go | Rust | GC→ownership, goroutines→async |
| convert-java-rust | Java | Rust | GC→ownership, exceptions→Result |
| convert-python-golang | Python | Go | Dynamic→static, GIL→goroutines |
| convert-python-rust | Python | Rust | Dynamic→ownership, GC→manual |
| convert-typescript-golang | TypeScript | Go | Async→goroutines, any→interface{} |
| convert-typescript-rust | TypeScript | Rust | Async→futures, any→generics |

## Approach

1. **Map memory management spectrum** — GC (Java/Go) → RC (Swift) → Ownership (Rust) → Manual (C/C++)
2. **Extract shared patterns** — Error handling, concurrency, type system mappings common across skills
3. **Preserve systems-specific detail** — Memory, unsafe code, FFI concerns need high-fidelity preservation
4. **Organize by conversion direction** — "To Rust" patterns are the most common (5 of 9 skills)
