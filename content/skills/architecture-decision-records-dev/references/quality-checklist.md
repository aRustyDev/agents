# ADR Quality Framework

Comprehensive quality criteria for reviewing Architecture Decision Records.

## E.C.A.D.R. Criteria (Detailed)

| Criterion | Question | Pass | Fail |
|-----------|----------|------|------|
| **E**xplicit | Is the problem clearly stated? | Reader understands the problem without prior context | Vague ("we need a database") or assumes knowledge |
| **C**omprehensive | Are alternatives explored? | 2+ options with honest pros/cons for each | Single option presented, or strawman alternatives |
| **A**ctionable | Is the decision specific? | Someone could implement it from the ADR alone | Ambiguous ("use a modern framework") or deferred |
| **D**ocumented | Are consequences listed? | Positive, negative, and neutral outcomes stated | Only benefits listed, or consequences missing |
| **R**eviewable | Can an outsider understand it? | New team member can follow the reasoning | Requires tribal knowledge or undocumented context |

## Strategic Lenses

Apply these for significant or hard-to-reverse decisions.

### Chesterton's Fence

> Before removing or changing something, understand why it exists.

| Check | Question |
|-------|----------|
| Original purpose | Why does the current approach exist? |
| Changed conditions | What has changed to make it inadequate? |
| Preserved value | What value from the current approach must be maintained? |

### Path Dependence

> Some decisions are hard to reverse — assess lock-in.

| Check | Question |
|-------|----------|
| Reversibility | How hard is it to change this decision later? |
| Lock-in factors | Vendor, data format, API contract, team skill investment? |
| Exit strategy | If this fails, what is the migration path? |
| Time horizon | How long will we live with this decision? |

### Second-System Effect

> Beware over-engineering the replacement.

| Check | Question |
|-------|----------|
| Scope bounded | Does this solve the stated problem, not all future problems? |
| Complexity justified | Is each feature earned by a requirement, not speculation? |
| MVP defined | What is the minimum viable version of this decision? |

## Quality Scoring Rubric

| Score | Label | Criteria |
|-------|-------|----------|
| 5 | Exemplary | All E.C.A.D.R. criteria met, strategic lenses applied, diagram clear |
| 4 | Good | All E.C.A.D.R. criteria met, minor gaps in depth |
| 3 | Adequate | Most criteria met, 1-2 sections need expansion |
| 2 | Incomplete | Missing sections or strawman alternatives |
| 1 | Draft | Skeleton only, significant gaps throughout |

## Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Rubber stamp | ADR written after implementation to justify choice | Write before or during — capture real deliberation |
| Strawman options | Alternatives clearly inferior to chosen option | Include genuinely viable alternatives |
| Kitchen sink | Multiple decisions in one ADR | Split into focused, single-decision ADRs |
| Amnesia | No reference to prior decisions or context | Link related ADRs via `related:` frontmatter |
| Crystal ball | Speculative future requirements driving the decision | Ground in current, concrete needs |
| Echo chamber | No trade-offs listed for chosen option | Every choice has downsides — document them |
| Tombstone | ADR written but never referenced or followed | Add code traceability, link from issues |

## INVESTIGATE Markers

For sections that cannot be completed from available information.

### Format

```markdown
- [INVESTIGATE: <specific question to answer>]
```

### Rules

| Rule | Rationale |
|------|-----------|
| Be specific | `[INVESTIGATE: Benchmark Redis vs Memcached latency]` not `[INVESTIGATE: performance]` |
| One question per marker | Easier to track and resolve |
| Place in relevant section | Don't collect at the bottom |
| Resolve before accepting | ADR status stays `proposed` until all markers resolved |

### Resolution

When resolving an INVESTIGATE marker:

1. Replace the marker with the finding
2. If the finding changes the decision, update the Decision Outcome
3. If the finding invalidates an option, document why in that option's cons
