# Information Type Coverage

When building a search matrix, ensure your queries across tiers seek diverse
types of information — not just the same angle repeated with different engines.

## The Six Information Types

| Information Type | Purpose | Query Signals | Maps to Matrix Concept |
|---|---|---|---|
| Facts and Data | Concrete evidence, numbers, measurements | "statistics", "data", "benchmark", "market size" | verification type queries, acceptance criteria with countable thresholds |
| Examples and Cases | Real-world implementations, practice | "case study", "example", "implementation", "in production" | deep-dive type queries, `site:github.com`, StackOverflow experience reports |
| Expert Opinions | Authority perspectives, analysis | "expert analysis", "interview", author-scoped searches | Academic engines, blog platforms (`site:blog.*`), conference talks |
| Trends and Predictions | Future direction, trajectory | "trends 2025", "forecast", "future of", "roadmap" | Recency-weighted queries (`after:2024`), news-focused engines |
| Comparisons | Context, alternatives, trade-offs | "vs", "comparison", "alternatives", "pros and cons" | comparison type queries, side-by-side evaluation rows |
| Challenges and Criticisms | Balanced view, limitations | "challenges", "limitations", "criticism", "problems with" | Specific term operators, practitioner forums, HN/Reddit threads |

## How to Use This During Matrix Building

After drafting your Tier 1 queries, check: **are at least 3 of these 6 information
types represented across your queries?** If your rows all target the same type
(e.g., all searching for examples), the matrix has a coverage blind spot.

### Minimum coverage by research type

| Research Type | Must Include | Should Include | Nice to Have |
|---|---|---|---|
| deep-dive | Examples, Facts | Expert Opinions, Challenges | Trends, Comparisons |
| survey | Comparisons, Facts | Trends, Examples | Expert Opinions, Challenges |
| comparison | Comparisons, Facts | Challenges, Examples | Expert Opinions, Trends |
| verification | Facts, Expert Opinions | Challenges | Examples, Comparisons, Trends |

### Example: checking a draft matrix

**Research question:** "Best CRDT library for TypeScript collaborative editing"
**Type:** comparison

Draft Tier 1 queries:
1. npm search for CRDT packages → **Facts** (download counts, versions)
2. GitHub search for CRDT repos → **Examples** (implementations)
3. Google blog search for CRDT comparison → **Comparisons** (side-by-side)

Coverage check: 3 types represented (Facts, Examples, Comparisons). Missing:
Challenges, Expert Opinions, Trends. Consider adding:
4. StackOverflow search for CRDT problems → **Challenges** ("what went wrong")

Now 4 of 6 types are covered — solid for a comparison matrix.

## When to skip this check

- Quick, focused verification queries (e.g., "does library X support feature Y") —
  these legitimately need only Facts
- Tier 2 and 3 queries — coverage diversity matters most in Tier 1. Later tiers
  are about broadening, not diversifying information types
- Single-source lookups — if you know exactly where the answer is, diversity
  adds no value
