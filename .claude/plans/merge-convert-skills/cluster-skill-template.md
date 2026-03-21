# Community & Bridge Skill Template

Template for Phases C1-C4 (community skills) and B1-B3 (bridge skills). Each skill follows the appropriate template below to ensure consistency across the tiered IR architecture defined in [ADR-010](docs/src/adr/adr-010-tiered-ir-architecture.md).

## Design Principles

1. **Tiered community IR with shared layers** — L0 (Expression) and L4 (Structural) are universal, defined once in phase S0. Each community defines its own L1-L3 with community-specific coupling. Bridge skills transform only the layers that diverge between adjacent communities.

2. **Aggressive progressive disclosure** — SKILL.md is a routing hub and quick-reference. Detailed per-language, per-layer, and per-pair content lives in reference/. A user converting Elixir to Haskell should land in the bridge SKILL.md, find the right reference doc in under 30 seconds, and get pair-specific depth there.

3. **Layer decomposition** — Conversions are composed sub-problems, one per independent layer or coupled-core group. Community skills document within-community layer-by-layer conversion. Bridge skills document cross-community layer transforms. The coupled core for each community is solved as a unit; independent layers are solved separately.

4. **Soft limit: SKILL.md at most 500 lines** — Not a hard cutoff. If the skill needs 520 lines to be complete, that is fine. If it is approaching 800, push content to reference/.

---

## Layer Coupling Quick Reference

Each community has a different coupling pattern for L1-L3. Shared layers L0 and L4 are always independent.

```
Typed-FP:       L0  L1  L2  L3  L4    <- all independent, fully decomposable
Dynamic-FP:     L0  L1  [L2+L3]  L4   <- L2+L3 coupled (dispatch depends on type info)
Object/Managed: L0  L1  [L2+L3]  L4   <- L2+L3 coupled (method dispatch depends on class hierarchy)
Systems:        L0  [L1+L3]  L2  L4   <- L1+L3 coupled (ownership depends on types)
```

A conversion decomposes into sub-problems per layer or coupled-core group. Each sub-problem is solved independently, then the results are merged into the final output.

---

# Part 1: Community Skill Template

For phases C1 (Typed-FP), C2 (Dynamic-FP), C3 (Object/Managed), C4 (Systems).

Community skills cover **within-community** conversion between member languages. All member language pairs should be difficulty 2 or lower.

## Directory Structure

```
context/skills/meta-convert-community-{name}-dev/
├── SKILL.md                    # Hub: routing, quick-ref, universal patterns (~300-500 lines)
├── reference/                  # Deep per-family and per-pair conversion docs
│   ├── layer-coupling.md       # How this community's coupled core works, with examples
│   ├── ir-extraction.md        # How to extract community IR (shared L0+L4 + community L1-L3)
│   ├── ir-annotations.md       # Community-specific annotations (NOT bridge annotations)
│   ├── shared-layers.md        # Notes on L0/L4 usage specific to this community's languages
│   ├── {family-a}.md           # Family-level patterns (e.g., beam-family.md)
│   ├── {family-b}.md           # Family-level patterns (e.g., ml-family.md)
│   ├── {pair-specific}.md      # Direction-specific docs (only where similarity < 0.90)
│   ├── gap-catalog.md          # Semantic gaps relevant to within-community pairs
│   └── decision-points.md      # Human judgment required (from Phase 3's 16 decision points)
├── schemas/                    # Community-specific layer schemas
│   ├── L1-data-flow.json       # Community L1 schema (or part of coupled core)
│   ├── L2-control-flow.json    # Community L2 schema (or part of coupled core)
│   ├── L3-type.json            # Community L3 schema (or part of coupled core)
│   └── coupled-core.json       # Coupled core schema (omitted for Typed-FP; L2+L3 or L1+L3)
├── examples/                   # Full before/after conversion examples
│   ├── {family-a}/             # Examples grouped by family or pair
│   │   ├── basic.md            # Simple conversion (types, functions)
│   │   ├── intermediate.md     # Medium (error handling, concurrency)
│   │   └── advanced.md         # Complex (metaprogramming, FFI, type-level)
│   └── {family-b}/
├── scripts/                    # Automation for this community skill
│   ├── validate-merge.sh       # Validate merged skill covers source skills
│   └── similarity-check.py     # Compare merged output vs original skill output
├── docs/                       # Internal documentation (not user-facing)
│   ├── src/
│   │   ├── adrs/               # Use 'adrs' cli to populate/manage these
│   │   │   └── {category}/
│   │   ├── log/
│   │   │   └── merged.md       # What was merged, what was dropped, why
│   │   ├── data/
│   │   │   └── similarity.md   # Pairwise similarity scores for this community
│   │   ├── source/
│   │   │   └── skills.md       # List of original skills that were merged
│   │   └── SUMMARY.md
│   └── book.toml               # mdbook config
├── .gitignore
└── justfile
```

### What Goes Where

| Directory | Purpose | Audience | When Loaded |
|-----------|---------|----------|-------------|
| `SKILL.md` | Quick reference, routing, universal patterns | Anyone doing a within-community conversion | Always (first thing Claude reads) |
| `reference/` | Deep technical content per family, per pair, and per layer | User mid-conversion needing specific patterns | On demand via SKILL.md routing |
| `schemas/` | Community-specific L1-L3 layer schemas and coupled core | Tooling and validation | On demand by extraction/synthesis tools |
| `examples/` | Complete before/after code conversions | User wanting to see full conversions | On demand when user asks for examples |
| `scripts/` | Validation and quality tooling | Skill maintainer during merge or updates | Never auto-loaded; run manually |
| `docs/` | Merge provenance and internal notes | Skill maintainer | Never auto-loaded; for audit trail |

---

## SKILL.md Structure (Community)

```markdown
---
name: meta-convert-community-{name}-dev
description: {One-line: what languages, what direction, what community}
tags: [meta, convert, community, {community-name}, dev]
---

# {Community Name} Community Conversion

{2-3 sentence overview: what languages are covered, the shared paradigm, the coupled core}

## When to Use

- Converting between {list of member languages}
- All pairs within the {community name} community (difficulty <= 2)
- {Specific use cases}

## This Skill Does NOT Cover

- Cross-community conversions (see bridge skills: meta-convert-bridge-{name}-dev)
- Language-specific idiom polishing (see idiomatic-{lang}-dev skills)
- IR extraction/synthesis tooling (see meta-codebase-analysis-eng)
- Shared layer (L0/L4) definitions (see S0 phase artifacts)

## Language Pair Lookup

> Find your conversion pair below. All pairs use community-internal IR.
> For cross-community pairs, see the appropriate bridge skill.

| Source | Target | Reference | Key Concerns | Difficulty |
|--------|--------|-----------|--------------|------------|
| {Lang A} | {Lang B} | [{family}](reference/{family}.md) | {concerns} | Easy |
| {Lang A} | {Lang C} | [{pair}](reference/{pair}.md) | {concerns} | Medium |
| ... | ... | ... | ... | ... |

## Layer Architecture

This community uses shared L0 + L4 from the universal schema, plus community-specific L1-L3.

### Shared Layers (from S0)

| Layer | Role | Conversion Complexity |
|-------|------|-----------------------|
| L0: Expression | AST, operators, literals | Trivial (syntax mapping) |
| L4: Structural | Modules, imports, exports | Trivial (structural mapping) |

### Community Layers

| Layer | Role | Key Concepts | Independent? |
|-------|------|-------------|-------------|
| L1: Data Flow | {description} | {concepts} | {Yes/Part of coupled core} |
| L2: Control Flow | {description} | {concepts} | {Yes/Part of coupled core} |
| L3: Type | {description} | {concepts} | {Yes/Part of coupled core} |

### Coupled Core

{Description of which layers are coupled and why. For Typed-FP: "None - all layers
are fully decomposable." For others: explain the coupling.}

See [layer-coupling.md](reference/layer-coupling.md) for detailed coupling analysis
with examples.

## IR Extraction Pattern

All languages in this community follow the same extraction flow, using shared L0+L4
plus community-specific L1-L3:

1. **L4 Structural (shared):** Parse modules, imports, exports
2. **L0 Expression (shared):** Parse AST, operators, literals
3. **Community L1-L3:** {Describe extraction order based on coupling}
   {For Typed-FP: extract L1, L2, L3 independently in any order}
   {For Dynamic-FP: extract L1 independently, then [L2+L3] as coupled core}
   {For Object/Managed: extract L1 independently, then [L2+L3] as coupled core}
   {For Systems: extract L2 independently, then [L1+L3] as coupled core}
4. **Annotate:** Apply community-specific annotations (see [ir-annotations.md](reference/ir-annotations.md))

### Community-Specific Annotations

| Annotation | Layer | When to Emit | Example |
|------------|-------|-------------|---------|
| {annotation_id} | {layer} | {condition} | {brief example} |
| ... | ... | ... | ... |

Note: Bridge annotations (cross-cutting, 4+ families) are NOT documented here.
They belong to the relevant bridge skill.

## Universal Conversion Patterns

Patterns shared across ALL within-community pairs.

### Type System Mapping

| Concept | {Lang A} | {Lang B} | {Lang C} | Notes |
|---------|----------|----------|----------|-------|
| ... | ... | ... | ... | ... |

### Idiom Translation

{3-5 most common idiom patterns that apply universally within this community}

### Error Handling

{Universal error handling mapping for this community}

### Concurrency

{If applicable — community-specific concurrency pattern mapping}

## Common Pitfalls

| Pitfall | Languages Affected | Layer | Why It Happens | Fix |
|---------|--------------------|----- -|----------------|-----|
| {pitfall} | {which pairs} | {L1/L2/L3} | {root cause} | {resolution} |

## Semantic Gaps

{Summary of gaps relevant to within-community pairs only.
Cross-community gaps belong in bridge skills.}

| Gap Pattern | Severity | Layer | Pairs Affected | Mitigation |
|-------------|----------|-------|----------------|------------|
| {gap} | {sev} | {L1/L2/L3} | {pairs} | {brief} |

## See Also

- [meta-convert-guide](../meta-convert-guide/SKILL.md) — APTV workflow, 8 Pillars
- [meta-convert-dev](../meta-convert-dev/SKILL.md) — How to create/extend convert skills
- Bridge skills for cross-community conversion:
  - [meta-convert-bridge-typed-dynamic-dev](../meta-convert-bridge-typed-dynamic-dev/SKILL.md) — B1
  - [meta-convert-bridge-dynamic-object-dev](../meta-convert-bridge-dynamic-object-dev/SKILL.md) — B2
  - [meta-convert-bridge-object-systems-dev](../meta-convert-bridge-object-systems-dev/SKILL.md) — B3
- Other community skills
```

---

## reference/ File Templates (Community)

### layer-coupling.md

Documents this community's layer coupling with concrete examples:
- Which layers are coupled and why (e.g., "L2+L3 coupled because method dispatch depends on class hierarchy")
- Code examples showing the coupling in practice (3-4 language pairs)
- How the coupled core is solved as a unit during conversion
- Comparison to other communities' coupling patterns

### ir-extraction.md

How to extract community IR from this community's languages:
- Shared layers (L0, L4): reference S0 definitions, document any community-specific quirks
- Community L1-L3: extraction steps in coupling-aware order
- Coupled core extraction: how coupled layers are extracted together
- Common extraction failures and their error codes

### ir-annotations.md

Community-specific annotations only (family-specific, 1-3 families):
- List each annotation with: when to emit, what layer it belongs to, example JSON
- Organized by layer (L1, L2, L3, coupled core)
- Explicitly note which annotations are NOT here (bridge annotations, cross-cutting patterns)

### shared-layers.md

Community-specific notes on using the universal L0 and L4 schemas:
- Any language-specific quirks in expression IR (L0) for this community's languages
- Any language-specific quirks in structural IR (L4) for this community's languages
- How shared layers connect to community layers at extraction/synthesis boundaries

### {family}.md (e.g., beam-family.md)

Per-family reference doc covering:
- All pairs within this sub-family
- Detailed type mapping tables organized by layer
- Family-specific idiom translations (10-20 patterns)
- Family-specific pitfalls and gotchas
- Full before/after code examples for common patterns

Target length: 300-800 lines depending on family complexity.

### {pair-specific}.md (only where needed)

Created ONLY when a specific pair has patterns that do not generalize to the family level:
- Similarity less than 0.90 with family average
- Direction-specific patterns (A to B differs from B to A)
- Unique tooling or FFI requirements

### gap-catalog.md

Within-community semantic gaps from Phase 3:
- Filtered to gaps between member languages only
- Each gap with: description, severity, affected layer(s), affected pairs, mitigation
- Organized by gap category (impossible, lossy, structural, idiomatic, runtime, semantic)

### decision-points.md

Human judgment points from Phase 3 relevant to within-community conversion:
- Filtered subset of the 16 decision points
- Each with: when it arises, which layer, options, trade-offs, recommended default

---

## schemas/ Organization (Community)

Each community defines its own L1-L3 JSON schemas, organized by coupling:

### Typed-FP (no coupling)

```
schemas/
├── L1-data-flow.json       # Immutable bindings, transforms
├── L2-control-flow.json    # Pattern match, recursion, effects
└── L3-type.json            # ADTs, type classes, HKT, constraints
```

All three schemas are independent. No coupled-core.json needed.

### Dynamic-FP (L2+L3 coupled)

```
schemas/
├── L1-data-flow.json       # Dynamic bindings, transforms (independent)
├── coupled-core.json       # L2+L3: actor dispatch + dynamic types (solved together)
├── L2-control-flow.json    # Standalone L2 subset (for reference only; use coupled-core in practice)
└── L3-type.json            # Standalone L3 subset (for reference only; use coupled-core in practice)
```

### Object/Managed (L2+L3 coupled)

```
schemas/
├── L1-data-flow.json       # Mutable variables, assignments (independent)
├── coupled-core.json       # L2+L3: method dispatch + class hierarchy (solved together)
├── L2-control-flow.json    # Standalone L2 subset (for reference only)
└── L3-type.json            # Standalone L3 subset (for reference only)
```

### Systems (L1+L3 coupled)

```
schemas/
├── coupled-core.json       # L1+L3: ownership/lifetimes + traits/raw types (solved together)
├── L1-data-flow.json       # Standalone L1 subset (for reference only)
├── L2-control-flow.json    # Unsafe blocks, inline, intrinsics (independent)
└── L3-type.json            # Standalone L3 subset (for reference only)
```

---

## examples/ Organization (Community)

Examples use a consistent structure:

```markdown
# {Example Title}

**Pair:** {Source} -> {Target}
**Community:** {community name}
**Complexity:** Basic | Intermediate | Advanced
**Demonstrates:** {what patterns this example shows}
**Layers Involved:** {which layers are exercised, noting coupled core}

## Source ({Language})

```{lang}
{complete, runnable source code}
```

## Target ({Language})

```{lang}
{complete, idiomatic target code}
```

## Per-Layer Conversion Notes

### L0 (Expression) — Shared
- {Syntax mapping decisions}

### L4 (Structural) — Shared
- {Module/import mapping decisions}

### {Independent Layer(s)}
- {Layer-specific conversion notes}

### {Coupled Core} (if applicable)
- {How the coupled layers were solved together}
- {What information was used from each coupled layer}

## IR Representation (Optional)

{If helpful, show the community IR JSON for a key fragment}
```

### Example Count Targets (Community)

| Community | Basic | Intermediate | Advanced | Total |
|-----------|-------|--------------|----------|-------|
| C1 (Typed-FP) | 3-4 | 3-4 | 2-3 | 8-11 |
| C2 (Dynamic-FP) | 2-3 | 2-3 | 1-2 | 5-8 |
| C3 (Object/Managed) | 3-4 | 3-4 | 2-3 | 8-11 |
| C4 (Systems) | 2-3 | 2-3 | 2-3 | 6-9 |

Examples should cover diverse pairs within the community, not just one pair.

---

## Merge Process Checklist (Community)

Use this checklist when executing phases C1-C4:

### Pre-Merge

- [ ] List all source convert-* skills whose language pairs fall within this community
- [ ] Compute pairwise similarity scores (if not already in Phase 3 data)
- [ ] Identify sub-families within the community (e.g., BEAM, LISP within Dynamic-FP)
- [ ] Review gap-catalog for within-community language pairs
- [ ] Review decision-points relevant to within-community conversion
- [ ] Verify shared layer schemas (L0, L4) from S0 are complete and available
- [ ] Identify this community's coupled core and confirm coupling pattern

### During Merge

- [ ] Define community L1-L3 schemas (including coupled-core.json where applicable)
- [ ] Extract universal patterns shared across ALL source skills -> SKILL.md
- [ ] Group family-specific patterns -> reference/{family}.md
- [ ] Identify pair-specific patterns (similarity < 0.90) -> reference/{pair}.md
- [ ] Document layer coupling with code examples -> reference/layer-coupling.md
- [ ] Map IR extraction steps for community languages -> reference/ir-extraction.md
- [ ] List community-specific annotations (NOT bridge annotations) -> reference/ir-annotations.md
- [ ] Document shared layer usage notes -> reference/shared-layers.md
- [ ] Create examples covering diverse within-community pairs -> examples/
- [ ] Document within-community semantic gaps -> reference/gap-catalog.md
- [ ] Document decision points -> reference/decision-points.md

### Post-Merge

- [ ] SKILL.md at most 500 lines (soft limit)
- [ ] Language Pair Lookup table covers ALL within-community source skill pairs
- [ ] Coupled core is documented with concrete examples
- [ ] Community L1-L3 schemas validate against test data
- [ ] Run validate-merge.sh -- no patterns dropped without justification
- [ ] Run similarity-check.py -- no L2+ regression vs original skills
- [ ] Write merge-log.md with full audit trail
- [ ] Run Phase 5.1 tech debt cleanup pattern on all new files
- [ ] Update index.md phase status
- [ ] Close beads issue

---

# Part 2: Bridge Skill Template

For phases B1 (Typed-FP <-> Dynamic-FP), B2 (Dynamic-FP <-> Object/Managed), B3 (Object/Managed <-> Systems).

Bridge skills cover **cross-community** conversion between adjacent communities. They transform only the layers that diverge; shared layers and identical independent layers pass through untouched.

## Directory Structure

```
context/skills/meta-convert-bridge-{name}-dev/
├── SKILL.md                    # Hub: routing, quick-ref, bridge protocol (~300-500 lines)
├── reference/                  # Deep technical content for cross-community transforms
│   ├── bridge-protocol.md      # Formal protocol: which layers transform, which pass through
│   ├── layer-transforms/       # Per-layer transform documentation
│   │   ├── L1-transforms.md    # L1 transforms (if this bridge touches L1)
│   │   ├── L2-transforms.md    # L2 transforms (if this bridge touches L2)
│   │   └── L3-transforms.md    # L3 transforms (if this bridge touches L3)
│   ├── asymmetry.md            # Directional difficulty differences (e.g., GC->ownership 4:1)
│   ├── chaining.md             # How this bridge composes with others for non-adjacent pairs
│   ├── loss-catalog.md         # Information loss tracking per transform
│   ├── decision-points.md      # Human judgment required for cross-community transforms
│   └── {specific-pattern}.md   # Deep dives on specific difficult transforms
├── schemas/                    # Bridge-specific schemas
│   ├── bridge-protocol.json    # Bridge protocol definition (layers, transforms, loss tracking)
│   ├── L1-transform.json       # L1 transform schema (if applicable)
│   ├── L2-transform.json       # L2 transform schema (if applicable)
│   └── L3-transform.json       # L3 transform schema (if applicable)
├── examples/                   # Full before/after cross-community conversions
│   ├── {direction-a-to-b}/     # Examples for one direction
│   │   ├── basic.md
│   │   ├── intermediate.md
│   │   └── advanced.md
│   └── {direction-b-to-a}/     # Examples for reverse direction (may differ in difficulty)
├── scripts/                    # Automation for this bridge skill
│   ├── validate-bridge.sh      # Validate bridge covers all cross-community pairs
│   ├── preservation-check.py   # Per-step preservation tracking through bridge
│   └── chain-test.py           # Test chained conversions through this bridge
├── docs/                       # Internal documentation
│   ├── src/
│   │   ├── adrs/
│   │   ├── log/
│   │   │   └── merged.md       # What cross-paradigm skills were merged
│   │   ├── data/
│   │   │   ├── asymmetry.md    # Directional difficulty ratios
│   │   │   └── loss-data.md    # Quantified information loss per transform
│   │   ├── source/
│   │   │   └── skills.md       # Original cross-community skills that were absorbed
│   │   └── SUMMARY.md
│   └── book.toml
├── .gitignore
└── justfile
```

### What Goes Where

| Directory | Purpose | Audience | When Loaded |
|-----------|---------|----------|-------------|
| `SKILL.md` | Quick reference, routing, bridge protocol overview | Anyone doing a cross-community conversion | Always (first thing Claude reads) |
| `reference/` | Deep transform rules, loss catalogs, decision points | User mid-conversion needing specific transform details | On demand via SKILL.md routing |
| `schemas/` | Bridge protocol and transform schemas | Tooling and validation | On demand by bridge tooling |
| `examples/` | Complete before/after cross-community conversions | User wanting to see full conversions | On demand when user asks for examples |
| `scripts/` | Validation, preservation tracking, chain testing | Skill maintainer | Never auto-loaded; run manually |
| `docs/` | Merge provenance and internal notes | Skill maintainer | Never auto-loaded; for audit trail |

---

## SKILL.md Structure (Bridge)

```markdown
---
name: meta-convert-bridge-{name}-dev
description: {One-line: which communities, what direction, key transforms}
tags: [meta, convert, bridge, {community-a}, {community-b}, dev]
---

# Bridge: {Community A} <-> {Community B}

{2-3 sentence overview: which communities are connected, the paradigm gap,
the key transforms this bridge handles.}

## When to Use

- Converting between a {Community A} language and a {Community B} language
- Example pairs: {Lang X} -> {Lang Y}, {Lang Y} -> {Lang Z}
- Non-adjacent conversions that chain through this bridge

## This Skill Does NOT Cover

- Within-community conversions (see community skills)
- Shared layer mapping (L0, L4 — handled universally)
- Language-specific idiom polishing (see idiomatic-{lang}-dev skills)
- Non-adjacent pairs that do NOT chain through this bridge

## Cross-Community Pair Lookup

> Find your conversion pair below. Note: difficulty may be asymmetric by direction.

| Source | Target | Direction | Key Transforms | Difficulty | Asymmetry |
|--------|--------|-----------|----------------|------------|-----------|
| {Lang A} | {Lang B} | A -> B | {transforms} | Medium | {ratio} |
| {Lang B} | {Lang A} | B -> A | {transforms} | Hard | {ratio} |
| ... | ... | ... | ... | ... | ... |

### Chained Conversions (via this bridge)

| Source | Target | Full Path | Bridges Used |
|--------|--------|-----------|-------------|
| {Lang X} | {Lang Z} | Community A ->B1-> Community B ->B2-> Community C | B1 + B2 |
| ... | ... | ... | ... |

See [chaining.md](reference/chaining.md) for chained conversion details.

## Bridge Protocol

This bridge transforms layers that diverge between {Community A} and {Community B}.
Shared layers and identical independent layers pass through untouched.

| Layer | Action | Description |
|-------|--------|-------------|
| L0: Expression | **Pass through** | Shared layer, syntax mapping only |
| L1: Data Flow | {Transform/Pass through} | {description} |
| L2: Control Flow | {Transform/Pass through} | {description} |
| L3: Type | {Transform/Pass through} | {description} |
| L4: Structural | **Pass through** | Shared layer, structural mapping only |

See [bridge-protocol.md](reference/bridge-protocol.md) for the formal protocol
definition.

### Coupled Core Alignment

Source community coupled core: {description, e.g., "L2+L3 coupled"}
Target community coupled core: {description, e.g., "L1+L3 coupled"}

The bridge must decompose the source coupled core and recompose into the
target coupled core. This is the hardest part of cross-community conversion.

{Brief description of how this bridge handles the coupled core mismatch.}

## Key Paradigm Transforms

The fundamental transforms this bridge handles, organized by layer:

### L{n} Transforms (if applicable)

| Source Concept | Target Concept | Transform | Confidence | Human Review? |
|---------------|---------------|-----------|------------|---------------|
| {concept} | {concept} | {strategy} | {0.0-1.0} | {Yes/No} |
| ... | ... | ... | ... | ... |

See [reference/layer-transforms/L{n}-transforms.md](reference/layer-transforms/L{n}-transforms.md) for full details.

## Directional Asymmetry

Some transforms are significantly harder in one direction:

| Transform | A -> B | B -> A | Ratio | Why |
|-----------|--------|--------|-------|-----|
| {transform} | {difficulty} | {difficulty} | {ratio} | {explanation} |

See [asymmetry.md](reference/asymmetry.md) for detailed analysis.

## Information Loss

Transforms where information is necessarily lost:

| Pattern ID | Layer | Information Lost | Mitigation | Preservation Level |
|-----------|-------|-----------------|------------|-------------------|
| {EF-nnn} | {Ln} | {what is lost} | {mitigation} | {0-3} |

See [loss-catalog.md](reference/loss-catalog.md) for the complete catalog.

## Decision Points

Transforms requiring human judgment:

| Decision ID | Layer | Question | Default | Options |
|------------|-------|----------|---------|---------|
| {DP-nnn} | {Ln} | {question} | {default} | {options} |

See [decision-points.md](reference/decision-points.md) for full analysis.

## Common Pitfalls

| Pitfall | Direction | Layer | Why It Happens | Fix |
|---------|-----------|-------|----------------|-----|
| {pitfall} | {A->B / B->A / Both} | {Ln} | {root cause} | {resolution} |

## See Also

- Community skills (for within-community conversion):
  - [meta-convert-community-{a}-dev](../meta-convert-community-{a}-dev/SKILL.md)
  - [meta-convert-community-{b}-dev](../meta-convert-community-{b}-dev/SKILL.md)
- Other bridge skills:
  - {list other bridges}
- [meta-convert-guide](../meta-convert-guide/SKILL.md) — APTV workflow, 8 Pillars
- [meta-convert-dev](../meta-convert-dev/SKILL.md) — How to create/extend convert skills
```

---

## reference/ File Templates (Bridge)

### bridge-protocol.md

Formal bridge protocol definition:
- Which layers this bridge transforms vs passes through
- Per-layer transform rules with confidence scores
- Loss tracking format and thresholds
- Decision point registry
- Bridge YAML protocol example (see ADR-010 Bridge Protocol section)

### layer-transforms/L{n}-transforms.md

Per-layer transform documentation:
- Every source concept to target concept mapping for this layer
- Transform strategies with code examples
- Confidence scores and when human review is required
- Edge cases and failure modes

### asymmetry.md

Directional difficulty analysis:
- Asymmetry ratios for each transform (from ADR-010 data)
- Why each direction differs in difficulty
- Strategy differences by direction
- Pairs where asymmetry is highest and requires special attention

### chaining.md

How this bridge composes with adjacent bridges:
- Which non-adjacent pairs chain through this bridge
- Layer pass-through behavior during chaining
- Cumulative information loss across chained bridges
- Per-step preservation tracking examples

### loss-catalog.md

Complete information loss tracking:
- Every transform where information is lost
- Quantified preservation level per transform (0-3 scale)
- Mitigation strategies applied
- Cumulative loss when multiple transforms compose

### decision-points.md

Human judgment points specific to cross-community conversion:
- Filtered from Phase 3's 16 decision points to those relevant to this bridge
- Each with: when it arises, which layer, options, trade-offs, recommended default
- Examples of each decision in context

---

## schemas/ Organization (Bridge)

Each bridge defines its own protocol and transform schemas:

### B1 (Typed-FP <-> Dynamic-FP)

```
schemas/
├── bridge-protocol.json    # Formal protocol: transforms L2, L3; passes L0, L1, L4
├── L2-transform.json       # Static effects <-> actor dispatch transforms
└── L3-transform.json       # HKT/type classes <-> protocols/dynamic types transforms
```

### B2 (Dynamic-FP <-> Object/Managed)

```
schemas/
├── bridge-protocol.json    # Formal protocol: transforms L2, L3; passes L0, L1, L4
├── L2-transform.json       # Actors/processes <-> objects/threads transforms
└── L3-transform.json       # Protocols/specs <-> classes/interfaces transforms
```

### B3 (Object/Managed <-> Systems)

```
schemas/
├── bridge-protocol.json    # Formal protocol: transforms L1, L2, L3; passes L0, L4
├── L1-transform.json       # GC references <-> ownership/lifetimes transforms
├── L2-transform.json       # Exceptions/async <-> Result/unsafe transforms
└── L3-transform.json       # Classes/generics <-> traits/raw types transforms
```

Note: B3 transforms the most layers because the paradigm gap is the widest (GC to ownership affects data flow L1, not just types L3).

---

## examples/ Organization (Bridge)

Bridge examples use a direction-aware structure:

```markdown
# {Example Title}

**Pair:** {Source} -> {Target}
**Bridge:** B{n} ({Community A} -> {Community B})
**Complexity:** Basic | Intermediate | Advanced
**Demonstrates:** {what cross-community patterns this example shows}
**Layers Transformed:** {which layers the bridge transforms for this example}
**Layers Passed Through:** {which layers pass through unchanged}

## Source ({Language}, {Community A})

```{lang}
{complete, runnable source code}
```

## Target ({Language}, {Community B})

```{lang}
{complete, idiomatic target code}
```

## Bridge Conversion Notes

### Passed-Through Layers
- **L0 (Expression):** {syntax mapping, trivial}
- **L4 (Structural):** {module mapping, trivial}
- {Other passed-through layers}

### Transformed Layers
- **L{n}:** {what was transformed and how}
- **L{m}:** {what was transformed and how}

### Coupled Core Alignment
- Source coupled core ({community A}): {what the coupled core captured}
- Target coupled core ({community B}): {how it was recomposed}

### Information Lost
- {What was lost, which layer, mitigation applied}

### Decision Points Hit
- {Which decisions required human judgment}

## Per-Step Preservation

| Step | Preservation Level | Notes |
|------|--------------------|-------|
| Extract to {Community A} IR | 3 | {notes} |
| Bridge L{n} transform | {0-3} | {notes} |
| Bridge L{m} transform | {0-3} | {notes} |
| Synthesize to {Language B} | {0-3} | {notes} |
```

### Example Count Targets (Bridge)

| Bridge | A->B | B->A | Basic | Intermediate | Advanced | Total |
|--------|------|------|-------|--------------|----------|-------|
| B1 (Typed-FP <-> Dynamic-FP) | 2-3 | 2-3 | 2-3 | 2-3 | 1-2 | 5-8 |
| B2 (Dynamic-FP <-> Object/Managed) | 2-3 | 2-3 | 2-3 | 2-3 | 1-2 | 5-8 |
| B3 (Object/Managed <-> Systems) | 2-3 | 2-3 | 2-3 | 2-3 | 2-3 | 6-9 |

Both directions must be covered because bridge transforms are often asymmetric.

---

## Merge Process Checklist (Bridge)

Use this checklist when executing phases B1-B3:

### Pre-Merge

- [ ] Verify both adjacent community skills (C{x}, C{y}) are complete
- [ ] List all source convert-* skills whose pairs cross this bridge's communities
- [ ] Review ADR-010 bridge protocol for this bridge (layers transformed, layers passed)
- [ ] Review asymmetry ratios for cross-community pairs
- [ ] Review Phase 3 gap data for cross-community pairs
- [ ] Review Phase 3 decision points relevant to this bridge
- [ ] Identify which annotation patterns are bridge-scoped (cross-cutting, 4+ families)

### During Merge

- [ ] Define bridge protocol schema (bridge-protocol.json)
- [ ] Define per-layer transform schemas for each transformed layer
- [ ] Document per-layer transforms with code examples -> reference/layer-transforms/
- [ ] Document coupled core alignment (source coupled core -> target coupled core)
- [ ] Extract universal bridge patterns -> SKILL.md
- [ ] Document directional asymmetry -> reference/asymmetry.md
- [ ] Document chained conversion paths -> reference/chaining.md
- [ ] Build information loss catalog -> reference/loss-catalog.md
- [ ] Document decision points -> reference/decision-points.md
- [ ] Create examples covering BOTH directions -> examples/
- [ ] Validate chained conversions through this bridge -> scripts/chain-test.py

### Post-Merge

- [ ] SKILL.md at most 500 lines (soft limit)
- [ ] Cross-Community Pair Lookup table covers ALL cross-community pairs for this bridge
- [ ] Both directions have examples (asymmetric difficulty is explicitly documented)
- [ ] Bridge protocol schema validates against test data
- [ ] Per-step preservation tracking shows no regression vs original skills
- [ ] Chained conversion tests pass (for bridges enabling non-adjacent paths)
- [ ] Information loss catalog is complete with mitigations
- [ ] Run validate-bridge.sh -- no cross-community patterns dropped without justification
- [ ] Run preservation-check.py -- per-layer preservation meets thresholds
- [ ] Write merge-log.md with full audit trail
- [ ] Run Phase 5.1 tech debt cleanup pattern on all new files
- [ ] Update index.md phase status
- [ ] Close beads issue

---

# Shared Sections

The following apply to both community and bridge skills.

## scripts/ Contents

### validate-merge.sh (Community) / validate-bridge.sh (Bridge)

Validates that the merged skill covers all patterns from its source skills:

```bash
# For each source skill:
# 1. Extract section headings
# 2. Extract type mapping entries
# 3. Extract idiom pattern names
# 4. Check each appears in SKILL.md or reference/ docs
# Report: covered, moved-to-reference, dropped (with justification)
```

### similarity-check.py (Community) / preservation-check.py (Bridge)

Compares conversion quality:

```python
# Given a code sample and a source/target pair:
# 1. Run conversion using original individual skill context
# 2. Run conversion using merged community/bridge skill context
# 3. Compare outputs at per-layer semantic equivalence
# 4. Report any quality regression, broken down by layer
```

### chain-test.py (Bridge only)

Tests chained conversions through multiple bridges:

```python
# Given a non-adjacent pair (e.g., Haskell -> Rust):
# 1. Identify the bridge chain (B1 + B2 + B3)
# 2. Run conversion step by step through each bridge
# 3. Measure per-step preservation level
# 4. Measure cumulative information loss
# 5. Compare against direct conversion (if original skill exists)
```

---

## docs/ Contents

### merge-log.md

Audit trail of the merge process:

```markdown
# Merge Log: {Community/Bridge Name}

## Source Skills Merged
| Skill | Lines | Unique Patterns | Layer Relevance | Disposition |
|-------|-------|-----------------|-----------------|-------------|
| convert-elixir-erlang | 1,202 | 12 | L2+L3 | Merged into beam-family.md |
| ... | ... | ... | ... | ... |

## Patterns Dropped
| Pattern | Source Skill | Layer | Reason |
|---------|-------------|-------|--------|
| {pattern} | {skill} | {Ln} | {why dropped — redundant, outdated, etc.} |

## Decisions Made
| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| {decision} | {options} | {choice} | {why} |
```

### similarity-data.md

Pairwise similarity scores used to determine community/bridge groupings.

### source-skills.md

Complete list of original skills that were merged, with file paths for archive reference.

---

## Progressive Disclosure Depth Levels

Content is organized into 5 depth levels. Users start at Level 1 and drill deeper as needed.

### Community Skills

| Level | Where | What | When Loaded |
|-------|-------|------|-------------|
| **L1: Routing** | SKILL.md top | Language Pair Lookup table, "When to Use" | Always |
| **L2: Universal** | SKILL.md body | Patterns shared across all within-community pairs | Always |
| **L3: Family** | reference/{family}.md | Patterns specific to a language family | When user's pair is in that family |
| **L4: Pair** | reference/{pair}.md | Direction-specific patterns for one pair | Only when pair has unique concerns |
| **L5: Layer** | reference/layer-coupling.md, schemas/ | Layer-specific schemas and coupling details | When debugging layer-specific issues |

### Bridge Skills

| Level | Where | What | When Loaded |
|-------|-------|------|-------------|
| **L1: Routing** | SKILL.md top | Cross-Community Pair Lookup, bridge protocol summary | Always |
| **L2: Protocol** | SKILL.md body | Bridge protocol, key transforms, asymmetry overview | Always |
| **L3: Layer** | reference/layer-transforms/L{n}.md | Per-layer transform details | When working on a specific layer |
| **L4: Loss/Decision** | reference/loss-catalog.md, decision-points.md | Information loss and human judgment details | When conversion hits a loss or decision point |
| **L5: Chain** | reference/chaining.md | Multi-bridge composition details | When conversion chains through multiple bridges |

### How Claude Routes

1. User asks to convert Language A to Language B
2. Claude determines community membership for both languages
3. If same community: load community SKILL.md, find pair in lookup, follow reference links
4. If different communities: identify bridge chain, load bridge SKILL.md(s), follow protocol
5. Claude reads ONLY the reference docs relevant to the user's specific pair and direction
6. Claude does NOT read all reference/ files upfront

---

## Naming Convention

### Community Skills

```
meta-convert-community-{community-name}-dev
```

| Community | Skill Name |
|-----------|------------|
| C1: Typed-FP | `meta-convert-community-typed-fp-dev` |
| C2: Dynamic-FP | `meta-convert-community-dynamic-fp-dev` |
| C3: Object/Managed | `meta-convert-community-object-managed-dev` |
| C4: Systems | `meta-convert-community-systems-dev` |

### Bridge Skills

```
meta-convert-bridge-{name}-dev
```

| Bridge | Skill Name |
|--------|------------|
| B1: Typed-FP <-> Dynamic-FP | `meta-convert-bridge-typed-dynamic-dev` |
| B2: Dynamic-FP <-> Object/Managed | `meta-convert-bridge-dynamic-object-dev` |
| B3: Object/Managed <-> Systems | `meta-convert-bridge-object-systems-dev` |

### Convention Details

Category: `meta` (skill development)
Tool: `convert-community-{name}` or `convert-bridge-{name}`
Focus: `dev` (development)

---

## 4-Community Quick Reference

| Community | Families | Languages | Coupled Core | Phases |
|-----------|----------|-----------|-------------|--------|
| **Typed-FP** | ML-FP | Haskell, Elm, Scala, F#, OCaml, Roc | None (fully decomposable) | C1 |
| **Dynamic-FP** | BEAM, LISP | Erlang, Elixir, Gleam, Clojure | L2+L3 | C2 |
| **Object/Managed** | Dynamic, Managed-OOP, Apple | Python, TS, JS, Java, C#, Kotlin, Swift, ObjC | L2+L3 | C3 |
| **Systems** | Systems | Rust, C, C++, Go, Zig | L1+L3 | C4 |

## 3-Bridge Quick Reference

| Bridge | Communities | Layers Transformed | Layers Passed | Phase |
|--------|-----------|-------------------|--------------|-------|
| **B1** | Typed-FP <-> Dynamic-FP | L2, L3 | L0, L1, L4 | B1 |
| **B2** | Dynamic-FP <-> Object/Managed | L2, L3 | L0, L1, L4 | B2 |
| **B3** | Object/Managed <-> Systems | L1, L2, L3 | L0, L4 | B3 |

## Phase Dependencies

```
S0 + V0 (parallel) --> C1, C2, C3, C4 (parallel) --> B1, B2, B3 (parallel) --> F1
                                                       B1 needs C1+C2
                                                       B2 needs C2+C3
                                                       B3 needs C3+C4
```
