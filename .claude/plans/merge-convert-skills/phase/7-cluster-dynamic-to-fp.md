# Phase 7: Cluster B — Dynamic→FP Merge

**ID:** phase-7
**Status:** pending
**Beads:** ai-x3e.9

## Objective

Merge 8 Dynamic→FP convert-* skills into a single `meta-convert-cluster-dynamic-fp-dev` skill. These skills convert from Python to FP family targets (Clojure, Elixir, Elm, Erlang, F#, Haskell, Roc, Scala) and share high similarity (avg 0.915) due to consistent source language patterns.

## Dependencies

- phase-6 (Cluster A: FP Internal) — establishes merge pattern and FP family reference docs

## Success Criteria

- [ ] Single `meta-convert-cluster-dynamic-fp-dev/SKILL.md` covers all 8 source skills
- [ ] SKILL.md < 200 lines (progressive disclosure)
- [ ] Leverages FP family reference docs from Phase 6
- [ ] Python-specific extraction patterns consolidated
- [ ] Round-trip validation passes for representative conversions

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Cluster skill | `context/skills/meta-convert-cluster-dynamic-fp-dev/SKILL.md` | Merged Dynamic→FP skill |
| Reference docs | `context/skills/meta-convert-cluster-dynamic-fp-dev/reference/` | Per-target conversion details |
| Validation report | `analysis/phase7-validation-report.md` | Merge quality assessment |

## Files

**Create:**
- `context/skills/meta-convert-cluster-dynamic-fp-dev/SKILL.md`
- `context/skills/meta-convert-cluster-dynamic-fp-dev/reference/python-to-beam.md` (→Erlang, →Elixir)
- `context/skills/meta-convert-cluster-dynamic-fp-dev/reference/python-to-ml.md` (→Haskell, →F#, →Elm, →Roc)
- `context/skills/meta-convert-cluster-dynamic-fp-dev/reference/python-to-jvm-fp.md` (→Scala, →Clojure)
- `analysis/phase7-validation-report.md`

**Modify:**
- `index.md` — Update phase-7 status to complete

## Source Skills (8)

| Skill | Source | Target |
|-------|--------|--------|
| convert-python-clojure | Python | Clojure |
| convert-python-elixir | Python | Elixir |
| convert-python-elm | Python | Elm |
| convert-python-erlang | Python | Erlang |
| convert-python-fsharp | Python | F# |
| convert-python-haskell | Python | Haskell |
| convert-python-roc | Python | Roc |
| convert-python-scala | Python | Scala |

## Approach

1. **Consolidate Python extraction patterns** — All 8 skills share the same source language; extract common Python→FP migration patterns
2. **Reference Phase 6 FP docs** — Target-side patterns already documented in Cluster A reference/
3. **Focus on source-side patterns** — Dynamic typing → static typing, imperative → functional, mutable → immutable
4. **Organize by target family** — BEAM targets, ML targets, JVM-FP targets
