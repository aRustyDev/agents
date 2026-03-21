# Phase 6: Cluster A — FP Internal Merge

**ID:** phase-6
**Status:** pending
**Beads:** ai-x3e.8

## Objective

Merge 28 FP-internal convert-* skills into a single `meta-convert-cluster-fp-dev` skill. These skills convert between languages within the functional programming family (Erlang, Elixir, Clojure, Elm, Haskell, Roc, F#, Scala, Gleam) and have the highest average similarity (0.935), making them the easiest cluster to merge.

## Dependencies

- phase-5.1 (Tech Debt Cleanup) — complete

## Success Criteria

- [ ] Single `meta-convert-cluster-fp-dev/SKILL.md` covers all 28 source skills
- [ ] SKILL.md < 200 lines (progressive disclosure; details in reference/)
- [ ] Each original skill's unique patterns preserved in reference docs
- [ ] Direction-specific sections kept where similarity < 0.90
- [ ] Round-trip validation passes for representative conversions
- [ ] No regression in conversion quality vs individual skills

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Cluster skill | `context/skills/meta-convert-cluster-fp-dev/SKILL.md` | Merged FP conversion skill |
| Reference docs | `context/skills/meta-convert-cluster-fp-dev/reference/` | Per-pair conversion details |
| Validation report | `analysis/phase6-validation-report.md` | Merge quality assessment |
| Similarity matrix | `analysis/phase6-similarity-matrix.md` | Pairwise similarity scores |

## Files

**Create:**
- `context/skills/meta-convert-cluster-fp-dev/SKILL.md`
- `context/skills/meta-convert-cluster-fp-dev/reference/beam-family.md` (Erlang↔Elixir)
- `context/skills/meta-convert-cluster-fp-dev/reference/ml-family.md` (Haskell↔F#↔Elm↔Roc)
- `context/skills/meta-convert-cluster-fp-dev/reference/jvm-fp.md` (Scala↔Clojure)
- `context/skills/meta-convert-cluster-fp-dev/reference/cross-family.md` (BEAM↔ML, Lisp↔ML, etc.)
- `analysis/phase6-validation-report.md`
- `analysis/phase6-similarity-matrix.md`

**Modify:**
- `index.md` — Update phase-6 status to complete

## Source Skills (28)

| Sub-family | Skills | Count |
|------------|--------|-------|
| Clojure↔* | clojure-{elixir,elm,erlang,fsharp,haskell,roc,scala} | 7 |
| Elixir↔* | elixir-{elm,erlang,fsharp,haskell,roc,scala} | 6 |
| Elm↔* | elm-{erlang,fsharp,haskell,roc,scala} | 5 |
| Erlang↔* | erlang-{fsharp,haskell,roc,scala} | 4 |
| F#↔* | fsharp-{haskell,roc,scala} | 3 |
| Haskell↔* | haskell-{roc,scala} | 2 |
| Roc↔Scala | roc-scala | 1 |

## Approach

1. **Extract shared patterns** — Identify patterns common across all 28 skills (type system mapping, pattern matching, immutability, ADTs)
2. **Identify sub-family clusters** — Group by runtime family (BEAM, JVM, ML) for reference doc organization
3. **Build progressive disclosure** — SKILL.md has universal patterns; reference/ has family-specific and pair-specific details
4. **Validate against original skills** — Ensure merged skill produces equivalent or better conversion guidance
5. **Run tech debt cleanup** — Apply Phase 5.1 patterns to clean the merged result

## Risks

| Risk | Mitigation |
|------|------------|
| Gleam/Roc instability (pre-1.0) | Document version assumptions; mark as provisional |
| SKILL.md exceeds 200 lines | Move more content to reference/ docs |
| Loss of pair-specific nuances | Keep direction-specific sections for pairs with similarity < 0.90 |
