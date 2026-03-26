# Grading Search Results

Scoring rubrics, threshold model, and assessment methodology for evaluating search matrix results.

## Table of Contents

- [Two-Threshold Model](#two-threshold-model)
- [Scoring Rubric](#scoring-rubric)
- [Per-Tier Grading](#per-tier-grading)
- [Overall Assessment](#overall-assessment)
- [Worked Example](#worked-example)

---

## Two-Threshold Model

Every tier in a search matrix uses two thresholds:

**Acceptance Criteria (minimum / gate):**
The minimum result quality required to stop searching at this tier. If results fall below the acceptance threshold, escalate to the next tier.

**Success Criteria (ideal / goal):**
The result quality that fully answers the research question from this tier. If results meet the success threshold, the research question is answered and no further tiers are needed.

The gap between acceptance and success defines a "partial" zone: results are good enough to use but not complete enough to stop all research.

```
|--- Below Acceptance ---|--- Partial ---|--- Success ---|
        Escalate            Use + Continue     Done
```

**Rules:**
- Acceptance is always lower than success (by definition)
- If a tier meets acceptance but not success, use its results AND continue to the next tier
- If a tier meets success, stop — do not execute remaining tiers
- If a tier falls below acceptance, discard its results and escalate
- Acceptance criteria should be concrete and testable (e.g., ">=3 distinct libraries identified")
- Success criteria should describe the ideal outcome (e.g., "comparison table with maturity ratings for all candidates")

---

## Scoring Rubric

Grade each tier's results across these dimensions:

### Relevance (0-3)

| Score | Definition |
|-------|------------|
| 0 | No relevant results. Everything returned is off-topic or irrelevant. |
| 1 | Tangentially relevant. Some results touch on the topic but do not answer the question. |
| 2 | Mostly relevant. Most results are on-topic and useful, with some noise. |
| 3 | Highly relevant. All or nearly all results directly address the research question. |

### Coverage (0-3)

| Score | Definition |
|-------|------------|
| 0 | No coverage. The research question is not addressed at all. |
| 1 | Partial coverage. Some aspects of the question are addressed, but significant gaps remain. |
| 2 | Good coverage. Most aspects of the question are addressed. Minor gaps. |
| 3 | Complete coverage. All aspects of the research question are addressed. |

### Authority (0-3)

| Score | Definition |
|-------|------------|
| 0 | No authoritative sources. All results are from unreliable or unknown sources. |
| 1 | Weak authority. Some results from known sources, but mostly unverifiable. |
| 2 | Good authority. Most results from recognized, credible sources. |
| 3 | Strong authority. Results from primary sources, peer-reviewed publications, official documentation, or recognized experts. |

### Recency (0-3)

| Score | Definition |
|-------|------------|
| 0 | Severely outdated. All results are from years before the topic's relevance window. |
| 1 | Dated. Most results are outside the ideal time window but may still be partially valid. |
| 2 | Reasonably current. Most results are within the expected time window. |
| 3 | Current. Results reflect the latest state of the topic. |

### Composite Score

Sum the four dimension scores for a tier composite: 0-12 scale.

| Composite | Interpretation |
|-----------|---------------|
| 0-3 | Failure. Results are unusable. Escalate immediately. |
| 4-6 | Below acceptance for most research types. Escalate unless criteria are very loose. |
| 7-9 | Acceptable range. Meets typical acceptance thresholds. |
| 10-12 | Success range. Results are thorough, authoritative, and current. |

**Note:** The composite score is a guideline, not a formula. Acceptance and success thresholds should be defined in terms of concrete outcomes (e.g., ">=3 libraries found"), not composite scores. The rubric helps structure your assessment, not replace your judgment.

---

## Per-Tier Grading

Grade each tier independently after its queries are executed.

### Process

1. Execute all queries in the tier
2. Collect and deduplicate results across queries
3. Score each dimension (Relevance, Coverage, Authority, Recency)
4. Compare against the tier's acceptance and success criteria
5. Decide: escalate, use + continue, or stop

### Recording Grades

Append a grading summary to the matrix output after execution:

```markdown
### Tier 1 Results
| Dimension | Score | Notes |
|-----------|-------|-------|
| Relevance | 2 | 4/5 results on-topic; 1 was about blockchain CRDTs |
| Coverage | 2 | Found 4 libraries but missing maturity data |
| Authority | 3 | GitHub repos with READMEs and npm packages |
| Recency | 3 | All repos updated within last 6 months |
| **Composite** | **10** | |

**Acceptance (>=3 libraries):** MET (found 4)
**Success (>=5 with maturity data):** NOT MET (missing maturity data)
**Decision:** Use results, proceed to Tier 2
```

### Tier-Specific Considerations

**Tier 1 (Primary):**
- Should have the highest acceptance bar (these are your best-guess queries)
- Failure at Tier 1 suggests the query design needs revision, not just broadening
- If Tier 1 scores 0-3, consider revising the matrix before proceeding to Tier 2

**Tier 2 (Broadened):**
- Acceptance bar can be slightly lower (broader queries naturally return more noise)
- Focus on Coverage improvement over Tier 1
- Tier 2 results supplement Tier 1, not replace them

**Tier 3 (Alternative):**
- Acceptance bar may be the lowest (alternative sources may have different quality profiles)
- Authority scoring may differ (e.g., forum posts vs documentation)
- Value comes from novelty: finding information not available through Tiers 1-2

---

## Overall Assessment

After all tiers are graded, produce an overall assessment.

### Assessment Template

```markdown
### Overall Assessment

**Research Question:** [the original question]
**Type:** [deep-dive | survey | comparison | verification]
**Tiers Executed:** [1 | 1-2 | 1-3 | 1-3 + recovery]

**Summary:**
[1-2 sentences on what was found and what gaps remain]

**Outcome:**
- [ ] Fully answered (success criteria met at some tier)
- [ ] Partially answered (acceptance met but success not met across all tiers)
- [ ] Not answered (acceptance not met; recovery needed or question should be revised)

**Unique results by tier:**
| Tier | Unique Contributions |
|------|---------------------|
| 1    | [what Tier 1 uniquely contributed] |
| 2    | [what Tier 2 added beyond Tier 1] |
| 3    | [what Tier 3 added beyond Tiers 1-2] |

**Recommendation:**
[Use results as-is | Rebuild matrix with different terms | Decompose question | Escalate to human]
```

### Decision Matrix

| Tier 1 | Tier 2 | Tier 3 | Outcome |
|--------|--------|--------|---------|
| Success | -- | -- | Done. Use Tier 1 results. |
| Acceptance | Success | -- | Done. Use Tier 1 + Tier 2 results. |
| Acceptance | Acceptance | Success | Done. Use all tier results. |
| Acceptance | Acceptance | Acceptance | Partial. Use all results, note gaps. |
| Acceptance | Acceptance | Below | Partial. Use Tier 1-2 results, note gaps. |
| Below | * | * | Revise matrix. Tier 1 failure suggests bad query design. |
| Acceptance | Below | Below | Weak. Use Tier 1, consider matrix revision. |

---

## Worked Example

**Research question:** "What CRDT libraries exist for collaborative text editing, and how mature are they?"

**Type:** survey + comparison

### Tier 1 Grading

Queries executed: GitHub (language:typescript stars:>50 CRDT), npm/crates.io (crdt text), Google (CRDT library collaborative editing comparison site:github.com OR site:reddit.com)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Relevance | 3 | All results directly about CRDT text editing libraries |
| Coverage | 2 | Found yjs, automerge, diamond-types, loro; missing maturity comparison |
| Authority | 3 | GitHub repos, npm packages with download counts |
| Recency | 3 | All repos active in last 6 months |
| **Composite** | **11** | |

**Acceptance (>=3 distinct libraries):** MET (found 4)
**Success (>=5 libraries with maturity indicators):** NOT MET (only 4 libraries, no structured comparison)
**Decision:** Use results, proceed to Tier 2

### Tier 2 Grading

Queries executed: Google (CRDT text editor library 2024), StackOverflow ([crdt] answers:1 collaborative editing), Semantic Scholar (CRDT collaborative text editing year:>2020)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Relevance | 2 | Most results relevant; some about CRDTs in general, not text editing |
| Coverage | 3 | Found peritext, cola, and a comparison blog post with maturity data |
| Authority | 2 | Blog post is well-sourced; SO answers are community knowledge |
| Recency | 2 | Blog post from 2023; academic papers from 2021-2023 |
| **Composite** | **9** | |

**Acceptance (>=2 additional libraries or comparisons):** MET (found 2 new libraries + comparison post)
**Success (comparison data for top candidates):** MET (blog post has structured comparison)
**Decision:** Success at Tier 2. Stop.

### Overall Assessment

**Research Question:** What CRDT libraries exist for collaborative text editing, and how mature are they?
**Type:** survey + comparison
**Tiers Executed:** 1-2

**Summary:**
Found 6 CRDT libraries (yjs, automerge, diamond-types, loro, peritext, cola) with maturity comparison data from a 2023 blog post, GitHub activity metrics, and npm download counts.

**Outcome:**
- [x] Fully answered (success criteria met at Tier 2)

**Unique results by tier:**
| Tier | Unique Contributions |
|------|---------------------|
| 1 | Core library identification: yjs, automerge, diamond-types, loro |
| 2 | Additional libraries (peritext, cola) + structured maturity comparison |

**Recommendation:** Use results as-is. The combination of Tier 1 library discovery and Tier 2 comparison data provides a complete landscape view with maturity assessment.
