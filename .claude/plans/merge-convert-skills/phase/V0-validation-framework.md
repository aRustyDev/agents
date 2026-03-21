# Phase V0: Validation Framework

**ID:** V0
**Status:** pending
**Beads:** ai-x3e.14

## Objective

Build the test infrastructure for validating the tiered IR architecture. Three complementary validation approaches: round-trip tests (resilience), benchmark projects (real-world quality), and per-step preservation tracking (granular per-layer quality). This framework is used by all subsequent community and bridge phases.

## Dependencies

- phase-5.1 (Tech Debt Cleanup) — complete

## Success Criteria

- [ ] Round-trip test harness operational (A -> IR -> B -> IR -> A' -> compare)
- [ ] Benchmark project corpus selected (10-20 projects, scoped to 1-2 languages initially)
- [ ] Per-step preservation measurement implemented (measure after each layer conversion)
- [ ] Preservation level (0-3) computed automatically for each measurement point
- [ ] Information loss catalog format defined and tooled
- [ ] Decision point tracking integrated with Phase 3 decision points
- [ ] CI-ready: all tests runnable via `just validate-*` recipes

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Round-trip harness | tools/ir-roundtrip/ | Extended with per-layer measurement |
| Benchmark corpus | data/benchmarks/ | Selected projects with expected outputs |
| Preservation tracker | tools/ir-validate/preservation.py | Per-step L0-L3 measurement |
| Loss catalog | tools/ir-validate/loss_catalog.py | Structured information loss tracking |
| Test recipes | justfile (validate-* group) | CI-ready validation commands |
| Framework docs | docs/src/validation/framework.md | How to use the validation framework |

## Files

**Create:**
- tools/ir-validate/preservation.py
- tools/ir-validate/loss_catalog.py
- data/benchmarks/README.md
- data/benchmarks/corpus.json (project list with metadata)
- docs/src/validation/framework.md
- docs/src/validation/preservation-levels.md (updated from existing)

**Modify:**
- tools/ir-roundtrip/ — Add per-layer measurement hooks
- tools/ir-validate/ — Add preservation tracking
- justfile — Add validate-* recipes

## Approach

1. Extend ir-roundtrip with measurement hooks after each layer conversion step
2. Define preservation level computation: L0 (syntax valid), L1 (semantic equiv), L2 (idiomatic), L3 (optimized)
3. Build loss catalog: structured format for "what was lost, at which layer, why, mitigation"
4. Select benchmark corpus: 10-20 projects per language (start with Python + one FP language)
5. Integrate Phase 3 decision point tracking — log which decision points are hit during each conversion
6. Wire everything to justfile recipes for CI
7. Document the framework so community/bridge phases know how to use it

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Preservation level computation is subjective | Medium | Medium | Define concrete criteria per level; automate L0-L1, semi-automate L2, manual-verify L3 |
| Benchmark project selection bias | Medium | Low | Select projects covering diverse patterns; document selection criteria |
| Framework overhead slows community phases | Low | Medium | Keep framework lightweight; measurement should be < 5% of conversion time |
