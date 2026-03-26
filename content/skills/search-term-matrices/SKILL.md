---
name: search-term-matrices
description: >-
  Strategic search planning for agent-driven research workflows. Use when you
  need to research a topic, find documentation, compare technologies, verify
  claims, or gather evidence before making decisions. Generates structured
  search-term matrices with tiered fallback strategies, engine-specific
  operators, and grading criteria. Produces a complete research plan — not
  ad-hoc queries — so every search is deliberate, gradable, and recoverable.
  Applies to any domain: technical, academic, regulatory, or general.
license: AGPL-3.0
metadata:
  triggers:
    type: domain
    enforcement: suggest
    priority: high
    keywords:
      - search
      - research
      - look up
      - find out
      - investigate
      - gather evidence
      - literature review
      - search matrix
      - search plan
      - search strategy
    intent-patterns:
      - "\\b(search|research|look\\s+up|find|investigate)\\b.*?\\b(topic|question|claim|technology|library|paper)\\b"
      - "\\b(compare|evaluate|survey|verify)\\b.*?\\b(options|alternatives|approaches|tools|frameworks)\\b"
      - "\\bbuild\\s+(a\\s+)?search\\s+(matrix|plan|strategy)\\b"
      - "\\b(deep[- ]?dive|literature\\s+review|state\\s+of\\s+the\\s+art)\\b"
---

# Search Term Matrices

Strategic search planning for agent-driven research workflows. Produces structured, tiered search matrices with engine-specific operators, fallback strategies, and grading criteria.

## Overview

**This skill covers:**
- Building multi-tier search matrices for any research question
- Selecting engines and operators matched to the research domain
- Designing pre-planned fallback strategies (not ad-hoc retries)
- Grading search results against acceptance and success thresholds
- Reporting issues found in the skill itself

**This skill does NOT cover:**
- Executing searches (that is the agent's job after the matrix is built)
- Setting up API keys, MCP servers, or authentication
- Summarizing or synthesizing search results into reports
- Managing citations or bibliographies

## Matrix Template

Every matrix follows this shape. Copy it, fill it in, and hand it to the executing agent.

```markdown
## Search Matrix: [Research Question]

### Context

Goal: [what we are trying to learn]
Type: [deep-dive | survey | comparison | verification]
Domain: [tech | academic | regulatory | general]

### Tier 1: Primary (high-precision)

| # | Engine(s) | Query | Operators | Expected Results | Acceptance Criteria | Success Criteria |
|---|-----------|-------|-----------|-----------------|---------------------|-----------------|
| 1 | ...       | ...   | ...       | ...             | ...                 | ...             |

### Tier 2: Broadened (if Tier 1 < acceptance threshold)

| # | Engine(s) | Query | Operators | Expected Results | Acceptance Criteria | Success Criteria |
|---|-----------|-------|-----------|-----------------|---------------------|-----------------|
| 1 | ...       | ...   | ...       | ...             | ...                 | ...             |

### Tier 3: Alternative sources (if Tier 2 insufficient)

| # | Engine(s) | Query | Operators | Expected Results | Acceptance Criteria | Success Criteria |
|---|-----------|-------|-----------|-----------------|---------------------|-----------------|
| 1 | ...       | ...   | ...       | ...             | ...                 | ...             |

### Runtime Recovery

Hints for when all tiers are exhausted:
- [ ] Decompose the question into narrower sub-questions
- [ ] Pivot terminology (synonyms, related jargon, alternate spellings)
- [ ] Try a different domain classification
- [ ] Escalate to the human for guidance

### Per-Tier Thresholds

| Tier | Acceptance (minimum / gate) | Success (ideal / goal) |
|------|----------------------------|----------------------|
| 1    | ...                        | ...                  |
| 2    | ...                        | ...                  |
| 3    | ...                        | ...                  |

(Full grading methodology: [references/grading.md](references/grading.md))
```

## Workflow

### Step 1: Assess Scope

Determine whether the research question is focused enough for a single matrix.

**Signals that decomposition is needed:**
- The question spans multiple unrelated domains
- Answering it requires more than 3 tiers of 4+ queries each
- The question contains "and" joining distinct sub-topics

**Stop and ask.** If you believe the question should be decomposed, present the proposed sub-questions to the user and wait for confirmation before proceeding. Do not silently decompose. Example:

> This question spans CRDT algorithms and their production deployment patterns. I recommend splitting into two matrices:
> 1. "What CRDT algorithms exist for collaborative text editing?"
> 2. "Which production systems use CRDTs and how do they handle conflicts?"
>
> Should I proceed with this split, or would you prefer a single broad matrix?

See [references/decomposition.md](references/decomposition.md) for decomposition strategies.

### Step 2: Classify Research Type

Identify the research type to guide engine selection and query design.

| Type | Description | Engine Bias | Query Style |
|------|-------------|-------------|-------------|
| deep-dive | Thorough exploration of a narrow topic | Specialized engines, documentation, academic | Precise, operator-heavy |
| survey | Broad landscape scan across a domain | General search, aggregators, registries | Broad terms, fewer operators |
| comparison | Evaluating alternatives against each other | Registries, documentation, forums | "X vs Y", feature-specific |
| verification | Confirming or refuting a specific claim | Academic, regulatory, authoritative sources | Exact phrases, source-constrained |

Hybrid types are allowed and often appropriate. For example, "survey + comparison" for a landscape scan that also compares the top candidates. State the hybrid explicitly in the Context block (e.g., `Type: survey + comparison`).

### Step 3: Select Engines

Choose engines based on the research type and domain. Group engines in a single row when they share operators; split into separate rows when operators diverge.

Engine references (load only the categories you need):
- [references/engines/general-search.md](references/engines/general-search.md) -- Google, Bing, DDG, Brave, SearXNG, Marginalia
- [references/engines/academic.md](references/engines/academic.md) -- Google Scholar, Semantic Scholar, arXiv, ACL Anthology, PubMed, Scopus, medRxiv, bioRxiv, PaperswithCode
- [references/engines/package-registries.md](references/engines/package-registries.md) -- npm, crates.io, docs.rs, PyPI, GoDocs, HexDocs
- [references/engines/code-platforms.md](references/engines/code-platforms.md) -- GitHub, GitLab, StackOverflow
- [references/engines/documentation.md](references/engines/documentation.md) -- MDN, AWS, Apple, Cloudflare, DeepWiki, MkDocs, Prisma, Refs, Context7
- [references/engines/regulatory.md](references/engines/regulatory.md) -- FDA, SEC, PubMed, medRxiv, bioRxiv
- [references/engines/paid-services.md](references/engines/paid-services.md) -- Tavily, Perplexity, Serper, Exa, Jina, FireCrawl, etc.

### Step 4: Build the Matrix

Fill in the template tier by tier.

**Tier 1 (Primary / high-precision):** Your best guesses — specific queries with tight operators aimed at authoritative sources. These should have the highest chance of returning exactly what you need.

**Tier 2 (Broadened):** Relaxed versions of Tier 1 queries — broader terms, fewer operators, more general engines. Use when Tier 1 falls below its acceptance threshold.

**Tier 3 (Alternative sources):** Different engine categories entirely. If Tiers 1 and 2 used documentation and code platforms, Tier 3 might try forums, academic sources, or paid services.

**Engines column rules:**
- Group engines in one row when they share identical operator syntax (e.g., Google + Bing both support `site:`)
- Split into separate rows when operators differ materially
- Default to grouping for token efficiency; split when precision matters

### Step 5: Design Fallback Tiers

Fallback is pre-planned, not ad-hoc. Each tier is designed before execution begins.

**Tier escalation logic:**
1. Execute Tier 1 queries
2. Grade results against Tier 1 acceptance criteria
3. If below acceptance threshold, execute Tier 2
4. Grade Tier 2 results against its own criteria
5. If still below, execute Tier 3
6. If all tiers exhausted, invoke runtime recovery hints

The matrix must make this escalation path obvious. Do not leave it to the executing agent to improvise fallback queries.

### Step 6: Add Runtime Recovery

Runtime recovery handles the case where all pre-planned tiers are exhausted. These are hints, not commands — the executing agent can use its own judgment.

Typical recovery hints:
- Decompose the question into narrower sub-questions
- Pivot terminology (synonyms, acronyms, related jargon)
- Reclassify the domain and try engines from a different category
- Relax time constraints (older results may still be relevant)
- Escalate to the human with a summary of what was tried

### Step 7: Set Grading Criteria

Each tier needs two thresholds:
- **Acceptance criteria (minimum / gate):** The minimum result quality to avoid escalating to the next tier. This is the "good enough to stop" bar.
- **Success criteria (ideal / goal):** The result quality that fully answers the research question. This is the "we nailed it" bar.

Compact thresholds go in the matrix. Full grading methodology is in [references/grading.md](references/grading.md).

## Worked Example: CRDT Libraries for Collaborative Editing

Research question: "What CRDT libraries are available for building collaborative text editors, and how mature are they?"

```markdown
## Search Matrix: CRDT Libraries for Collaborative Text Editing

### Context

Goal: Identify CRDT libraries suitable for collaborative text editing, assess maturity
Type: survey + comparison
Domain: tech

### Tier 1: Primary (high-precision)

| # | Engine(s)           | Query                                         | Operators                    | Expected Results                | Acceptance Criteria          | Success Criteria              |
|---|---------------------|-----------------------------------------------|------------------------------|---------------------------------|------------------------------|-------------------------------|
| 1 | GitHub              | CRDT collaborative text editor                | language:typescript stars:>50 | Library repos with README docs | >=3 active repos             | >=5 repos with recent commits |
| 2 | npm, crates.io      | crdt text                                     | (keyword search)             | Published packages              | >=2 packages with docs       | >=4 packages, downloads >1k   |
| 3 | Google              | CRDT library collaborative editing comparison | site:github.com OR site:reddit.com | Comparison posts, awesome-lists | >=1 comparison resource      | Structured comparison table   |

### Tier 2: Broadened (if Tier 1 < acceptance threshold)

| # | Engine(s)           | Query                                | Operators           | Expected Results              | Acceptance Criteria    | Success Criteria             |
|---|---------------------|--------------------------------------|---------------------|-------------------------------|------------------------|------------------------------|
| 1 | Google              | CRDT text editor library 2024        | (none)              | Blog posts, tutorials         | >=2 relevant results   | >=4 with implementation details |
| 2 | StackOverflow       | CRDT collaborative editing library   | [crdt] answers:1    | Q&A with recommendations      | >=1 answered question  | >=3 with library comparisons |
| 3 | Semantic Scholar    | CRDT collaborative text editing      | year:>2020          | Academic papers on CRDT impls | >=1 relevant paper     | >=3 papers with benchmarks   |

### Tier 3: Alternative sources (if Tier 2 insufficient)

| # | Engine(s)           | Query                                       | Operators | Expected Results            | Acceptance Criteria  | Success Criteria            |
|---|---------------------|---------------------------------------------|-----------|-----------------------------|----------------------|-----------------------------|
| 1 | DeepWiki            | yjs automerge diamond-types                 | (none)    | Library documentation       | >=1 library overview | All 3 libraries documented  |
| 2 | Perplexity / Tavily | best CRDT libraries for collaborative editing | (none)  | Curated summary with sources | Has source links    | Cites >=3 libraries with URLs |

### Runtime Recovery

- [ ] Decompose: split into "CRDT algorithms" vs "editor integration libraries"
- [ ] Pivot terms: "OT vs CRDT", "real-time collaboration library", "conflict-free replicated"
- [ ] Try HuggingFace or PaperswithCode for ML-adjacent CRDT work
- [ ] Escalate to user: share what was found, ask for domain clarification

### Per-Tier Thresholds

| Tier | Acceptance (minimum / gate)           | Success (ideal / goal)                    |
|------|---------------------------------------|-------------------------------------------|
| 1    | >=3 distinct libraries identified     | >=5 libraries with maturity indicators    |
| 2    | >=2 additional libraries or comparisons | Comparison data for top candidates       |
| 3    | Any new library not found in earlier tiers | Complete landscape with maturity ratings |
```

## Issue Reporting

**Read this section every time you use this skill.**

If you encounter problems with this skill — incorrect operators, missing engines, unclear instructions, broken workflows — report them. Do not silently work around issues.

### Report Flow

1. Identify the problem while using the skill
2. Classify it: `bug` (something is wrong) or `improvement` (something could be better)
3. Assess severity:
   - **blocks-work**: Cannot complete research planning without a workaround
   - **degrades-quality**: Produces a matrix but with suboptimal results
   - **nice-to-have**: Minor friction, cosmetic, or documentation gap
4. Draft an issue using the template in [references/issue-template.md](references/issue-template.md)
5. Present the draft to the user for review before filing
6. File against: `github.com/arustydev/agents`

### What to Report

- Engine operators that are incorrect or outdated
- Missing engines that should be in a category
- Workflow steps that are ambiguous or produce poor matrices
- Grading criteria that do not match real search result quality
- Decomposition guidance that leads to over- or under-splitting
- Any instruction in this skill that contradicts observed behavior

## Reference Index

| Reference | Purpose |
|-----------|---------|
| [references/engines/general-search.md](references/engines/general-search.md) | Google, Bing, DDG, Brave, SearXNG, Marginalia operators |
| [references/engines/academic.md](references/engines/academic.md) | Google Scholar, Semantic Scholar, arXiv, ACL Anthology, PubMed, Scopus, medRxiv, bioRxiv, PaperswithCode |
| [references/engines/package-registries.md](references/engines/package-registries.md) | npm, crates.io, docs.rs, PyPI, GoDocs, HexDocs |
| [references/engines/code-platforms.md](references/engines/code-platforms.md) | GitHub, GitLab, StackOverflow |
| [references/engines/documentation.md](references/engines/documentation.md) | MDN, AWS, Apple, Cloudflare, DeepWiki, MkDocs, Prisma, Refs, Context7 |
| [references/engines/regulatory.md](references/engines/regulatory.md) | FDA, SEC, PubMed, medRxiv, bioRxiv |
| [references/engines/paid-services.md](references/engines/paid-services.md) | Tavily, Perplexity, Serper, Exa, Jina, FireCrawl, and others |
| [references/grading.md](references/grading.md) | Scoring rubrics, two-threshold model, worked example |
| [references/issue-template.md](references/issue-template.md) | Issue template, labels, severity levels |
| [references/decomposition.md](references/decomposition.md) | When and how to decompose broad questions |
