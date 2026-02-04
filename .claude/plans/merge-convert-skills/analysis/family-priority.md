# Family Prioritization Analysis

Analysis of existing convert-* skills to prioritize family documentation order.

## Data Sources

- **Phase 0 Pattern Extraction**: 7,195 patterns from 49 skills
- **Pattern Clustering**: 173 universal, 417 family-specific, 3,293 language-specific patterns
- **Gap Analysis**: 320 semantic gaps identified

## Language Coverage in Existing Skills

| Language | As Source | As Target | Total Skills | Primary Family |
|----------|-----------|-----------|--------------|----------------|
| Python | 11 | 0 | 11 | Dynamic |
| Clojure | 7 | 1 | 8 | LISP |
| Elixir | 6 | 2 | 8 | BEAM |
| Elm | 5 | 3 | 8 | ML-FP |
| Erlang | 4 | 4 | 8 | BEAM |
| F# | 3 | 5 | 8 | ML-FP |
| Haskell | 2 | 6 | 8 | ML-FP |
| Roc | 1 | 7 | 8 | ML-FP |
| Scala | 0 | 8 | 8 | ML-FP |
| Rust | 0 | 6 | 6 | Systems |
| C | 2 | 1 | 3 | Systems |
| C++ | 1 | 2 | 3 | Systems |
| Go | 1 | 2 | 3 | Systems |
| Java | 3 | 0 | 3 | Managed-OOP |
| TypeScript | 2 | 1 | 3 | Dynamic |
| Objective-C | 1 | 0 | 1 | Apple |
| Swift | 0 | 1 | 1 | Apple |

## Family Statistics

| Family | Skills (Source) | Skills (Target) | Total Skills | Patterns | % of Total |
|--------|-----------------|-----------------|--------------|----------|------------|
| ML-FP | 11 | 29 | 40 | 1,461 | 20.3% |
| Dynamic | 13 | 1 | 14 | 2,267 | 31.5% |
| BEAM | 10 | 6 | 16 | 1,186 | 16.5% |
| LISP | 7 | 1 | 8 | 1,070 | 14.9% |
| Systems | 4 | 11 | 15 | 475 | 6.6% |
| Managed-OOP | 3 | 0 | 3 | 513 | 7.1% |
| Apple | 1 | 1 | 2 | 223 | 3.1% |

### Observations

1. **ML-FP dominates as target** - Most conversions go TO functional languages (Scala, Haskell, F#, Roc, Elm)
2. **Dynamic dominates as source** - Python is the most common source language (11 skills)
3. **BEAM is balanced** - Elixir/Erlang skills exist in both directions
4. **Systems is target-heavy** - Rust is a popular target (6 skills), rarely a source
5. **Managed-OOP is source-only** - Java skills convert TO other languages, never from

## Semantic Complexity Analysis

Gaps indicate conversion difficulty. Higher gap counts = more semantic complexity.

| Family Transition | Total Gaps | Human Decisions | Lossy | Negative |
|-------------------|------------|-----------------|-------|----------|
| ML-FP → ML-FP | 63 | 37 | 20 | 6 |
| Dynamic → ML-FP | 39 | 23 | 14 | 2 |
| BEAM → ML-FP | 36 | 26 | 6 | 4 |
| Dynamic → Systems | 29 | 16 | 10 | 3 |
| LISP → ML-FP | 27 | 18 | 7 | 2 |
| Systems → Systems | 23 | 19 | 0 | 4 |
| Managed-OOP → Systems | 13 | 12 | 0 | 1 |
| LISP → BEAM | 12 | 8 | 3 | 1 |
| ML-FP → Dynamic | 11 | 0 | 11 | 0 |
| ML-FP → BEAM | 10 | 3 | 6 | 1 |

### Key Insights

1. **Intra-family ML-FP has highest complexity** - Different flavors (pure vs hybrid) require careful decisions
2. **Dynamic → typed languages are complex** - Require type inference and structure
3. **Lossy conversions flow downward** - ML-FP → Dynamic loses type guarantees
4. **Human decisions dominate** - 183 of 320 gaps require manual choices

## Prioritization Criteria

Families ranked by weighted score:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Skill Coverage | 40% | Number of skills involving the family |
| Pattern Volume | 30% | Total patterns extracted |
| Semantic Complexity | 20% | Gaps and conversion difficulty |
| Strategic Importance | 10% | Future IR design considerations |

## Final Priority Ranking

| Priority | Family | Score | Rationale |
|----------|--------|-------|-----------|
| **1** | **ML-FP** | 95 | Target for 29 skills, 1,461 patterns, highest gap count (63), critical for IR design |
| **2** | **Dynamic** | 90 | Source for 13 skills, highest pattern volume (2,267), Python dominates conversions |
| **3** | **BEAM** | 75 | Balanced coverage (16 skills), unique actor model, distinct concurrency patterns |
| **4** | **LISP** | 65 | 8 skills, 1,070 patterns, important for understanding homoiconicity |
| **5** | **Systems** | 60 | Target for 11 skills, ownership model (Rust) is unique, critical for memory semantics |
| **6** | **Managed-OOP** | 45 | Only 3 skills, but represents traditional OOP patterns (Java) |
| **7** | **Apple** | 30 | Only 2 skills (Obj-C ↔ Swift), specialized ecosystem |

### Feature Families (Cross-Cutting)

These should be documented as aspects that cross paradigm families:

| Priority | Family | Rationale |
|----------|--------|-----------|
| 8 | Gradual-Typing | TypeScript patterns apply across Dynamic family |
| 9 | Ownership | Rust-specific but influences Systems understanding |
| 10 | Actors | BEAM-specific but applies to Akka (Scala) |
| 11 | Dependent-Types | Future coverage (Idris, Agda) |
| 12 | Logic | No current skills, specialized |
| 13 | Array | No current skills, specialized (APL family) |

## Documentation Order

### Phase 1.4 - Recommended Sequence

1. **ML-FP** - Start here (highest priority, most complex)
   - Document subtypes: pure (Haskell, Elm) vs hybrid (Scala, F#, Roc)
   - Cross-reference with 29 target skills

2. **Dynamic** - Second (most source skills)
   - Python patterns dominate
   - Include TypeScript as gradually-typed variant

3. **BEAM** - Third (unique concurrency model)
   - Actor model documentation
   - Erlang/Elixir relationship

4. **Systems** - Fourth (ownership complexity)
   - Rust ownership model
   - C/C++ memory management contrast

5. **LISP** - Fifth (homoiconicity)
   - Clojure focus (most skills)
   - Macro system patterns

6. **Managed-OOP** - Sixth (traditional OOP)
   - Java patterns as baseline
   - Class-based inheritance

7. **Apple** - Last (specialized)
   - Objective-C → Swift modernization
   - ARC memory model

## Validation Checkpoints

After documenting each family:

- [ ] Cross-reference with Phase 0 pattern clusters
- [ ] Verify type mappings match documented characteristics
- [ ] Validate conversion difficulty against gap analysis
- [ ] Ensure languages in family cover 100% of skills

## Output Files

This analysis informs:

- `docs/src/language-families/overview.md` - Use priority order for presentation
- `docs/src/language-families/{family}.md` - Document in priority order
- `data/families.sql` - Initialize with priority scores

## Notes

- Priority scores are relative (10-100 scale)
- Scores may be adjusted after Phase 0 cross-reference validation
- Feature families (8-13) can be documented in parallel with paradigm families
