# Skill Catalog Pipeline

## Goal

Categorize, analyze, grade, and index 13,644 external skill entries from `.TODO.yaml` into a searchable catalog with taxonomy, quality scores, and fork detection.

## Architecture

Four-phase pipeline, each independently runnable:

```
Phase 1: Taxonomy (offline)     → .taxonomy.yaml
Phase 2: Availability (network) → availability in .catalog.ndjson
Phase 3: Content Analysis (heavy) → full .catalog.ndjson
Phase 4: Grading & Indexing     → grades + .catalog-stats.json
```

## Input

`context/skills/.TODO.yaml` — 13,644 entries as `<org>/<repo>@<skill>`, 9,429 unique skill names across 3,333 repos.

## Taxonomy (19 categories)

| Category | Subcategory Examples |
|---|---|
| **lang** | python, rust, swift, golang, typescript, java, kotlin, elixir, c, cpp, csharp, ruby, php, scala, haskell |
| **frontend** | react, vue, svelte, angular, css, tailwind, design-system, accessibility, animation |
| **ui** | ui-design, components, layout, responsive, icons, color, typography, design-tokens |
| **ux** | user-research, user-story, personas, flows, wireframes, prototyping, a11y-audit |
| **backend** | api, graphql, rest, database, sql, redis, supabase, auth, cache, graphdb, cypher |
| **devops** | docker, kubernetes, terraform, ci-cd, github-actions, gitlab-cicd, gitops, monitoring |
| **ai-ml** | llm, rag, agent, mcp, langchain, embedding, prompt, training, o11y, mlops |
| **mobile** | ios, android, swiftui, react-native, flutter, app-store |
| **security** | pentest, burp, malware, forensics, incident-response, vulnerability, intel, osint |
| **data** | data-engineering, analytics, visualization, dbt, etl, pipeline |
| **content** | seo, marketing, blog, copywriting, social-media, brand |
| **testing** | unit, mock, component, visual, chaos, integration, e2e, qa, vitest, jest, playwright, coverage |
| **methodology** | brainstorming, debugging, code-review, spec, tdd, architecture |
| **tooling** | mermaid, git, editor, cli, documentation, linting |
| **cloud** | aws, gcp, azure, cloudflare, vercel, serverless |
| **finance** | stock, trading, crypto, fintech, payment |
| **game** | godot, unity, 3d, animation, game-design |
| **iot-embedded** | hardware, firmware, raspberry-pi, arduino |
| **misc** | uncategorizable (target: <2% of entries) |

### Classification Strategy (Hybrid)

**Rule engine (~60% of entries):** Keyword prefix matching on skill names. Deterministic, fast, no network.

```typescript
// Example rules
const rules: [RegExp, string, string][] = [
  [/^python[-_]/, 'lang', 'python'],
  [/^rust[-_]/, 'lang', 'rust'],
  [/^react[-_]/, 'frontend', 'react'],
  [/^seo[-_]/, 'content', 'seo'],
  [/^terraform[-_]/, 'devops', 'terraform'],
  [/^docker[-_]/, 'devops', 'docker'],
  [/^k8s[-_]|^kubernetes[-_]/, 'devops', 'kubernetes'],
  [/^llm[-_]/, 'ai-ml', 'llm'],
  [/^pentest[-_]/, 'security', 'pentest'],
  // ... ~100 rules covering known prefixes
]
```

**LLM batch (~40% of entries):** Ambiguous names sent in batches of 200 to Claude API with the taxonomy as context. Returns `{ name, category, subcategory }` for each.

### Output: `.taxonomy.yaml`

```yaml
# context/skills/.taxonomy.yaml
# Auto-generated. Maps unique skill names to category/subcategory.
taxonomy:
  webapp-testing: { category: testing, subcategory: e2e }
  systematic-debugging: { category: methodology, subcategory: debugging }
  brand-guidelines: { category: content, subcategory: brand }
  rag-implementation: { category: ai-ml, subcategory: rag }
  brainstorming: { category: methodology, subcategory: brainstorming }
  # ... 9,429 entries
```

Committed to git. Regenerated when `.TODO.yaml` changes (new entries only — existing classifications are preserved).

## Availability Check

Lightweight network pass before the heavy content analysis.

```bash
curl -sI -o /dev/null -w '%{http_code}' https://github.com/<owner>/<repo>
```

| HTTP Status | Availability |
|---|---|
| 200 | `available` |
| 301 (→ archive notice) | `archived` |
| 404 | `not_found` |
| 401/403 | `private` |
| timeout/error | `error` |

Rate-limited: 50 concurrent requests, 1s delay between batches. GitHub unauthenticated rate limit is 60 req/min; authenticated (GITHUB_TOKEN) is 5,000/hr.

For `not_found` entries: flag for follow-up search (repo may have been renamed/moved). A second pass can search GitHub API for the owner's repos matching the skill name.

## Content Analysis: Tiered Agent Model

Analysis is split into two tiers by cognitive demand. Tier 1 handles mechanical/heuristic checks at scale with Haiku. Tier 2 handles qualitative judgment selectively with Sonnet.

### Tier 1: Mechanical Analysis (Haiku)

**Agent:** `context/agents/catalog/skill-inspector-t1.md`
**Model:** Haiku (fast, cheap, sufficient for deterministic checks)
**Isolation:** Git worktree per batch
**Batch size:** 15-20 skills per dispatch, 5-10 concurrent agents
**Dispatches:** ~700-900 (all available, non-fork skills from Phase 2)

#### Allowed Tools

| Tool | Purpose |
|---|---|
| `Bash(npx:*)` | Download skills via `npx skills add -y --copy --full-depth` |
| `Bash(mdq:*)` | Structured markdown analysis (`mdq -o json`) |
| `Bash(wc:*,find:*,stat:*)` | File/word/line counts |
| `Bash(curl:*)` | URL availability HEAD requests |
| `Bash(mktemp:*,rm:*)` | Temp dir management |
| `Read`, `Glob`, `Grep` | Content inspection |

No `Write`, no `Edit` — agent is read-only. Returns NDJSON to stdout.

#### Tier 1 Checklist

##### Metadata Extraction

```bash
# Structured section tree + links in one pass
mdq -o json '# *' SKILL.md
```

Extracts:
- `wordCount` — `wc -w SKILL.md`
- `sectionCount` — count of sections in JSON output
- `fileCount` — `find <skill-dir> -type f | wc -l`
- `headingTree` — section titles and nesting depths
- `internalLinks[]` — relative paths from `links` object
- `externalLinks[]` — absolute URLs from `links` object

##### Keyword Extraction

Sources (in priority order):
1. Frontmatter `name` and `description`
2. H1 and H2 heading text
3. First paragraph of body content
4. Code block language identifiers

Output: `keywords[]` — deduplicated, lowercase, 5-20 keywords per skill.

##### Complexity Assessment

| Signal | Simple | Moderate | Complex |
|---|---|---|---|
| Word count | <500 | 500-2000 | >2000 |
| Section count | <4 | 4-10 | >10 |
| Max nesting depth | 2 | 3 | 4+ |
| Code block count | 0-1 | 2-5 | >5 |
| File count | 1 | 2-5 | >5 |

Score: average of signal grades. Output: `complexity: simple|moderate|complex`

##### Progressive Disclosure Detection

Check for these patterns:
- `<details>` / `<summary>` HTML blocks (collapsible sections)
- Section ordering: "Overview" or "Quick Start" before "Advanced" or "Reference"
- Explicit layering labels: "Basic", "Intermediate", "Advanced"
- Conditional sections: "If you need X, see..."
- `<!-- progressive -->` or similar metadata hints

Output: `progressiveDisclosure: boolean`, `techniques: string[]`

##### Best Practices: Mechanical Checks (0-3.5)

| Check | Points | What |
|---|---|---|
| Frontmatter has `name` | +1 | Required field present |
| Frontmatter has `description` | +1 | Required field present |
| Has examples or code blocks | +1 | Concrete usage patterns |
| Uses `allowed-tools` frontmatter | +0.25 | Restricts tool access |
| No hardcoded absolute paths | +0.25 | Portable across machines |

Output: `bestPracticesMechanical: { score: number, violations: string[] }`

##### Security: Regex-Based Checks (0-4)

| Check | Deduction | What |
|---|---|---|
| Hardcoded tokens/secrets | -2 | Regex: `sk-`, `ghp_`, `AKIA`, Bearer tokens, API keys |
| `Bash(*)` in allowed-tools (unrestricted) | -1 | Overly permissive tool access |
| `eval()` in code blocks | -1 | Code execution risk |
| No regex concerns found | 4 | Clean (Tier 2 adds +1 for injection review) |

Output: `securityMechanical: { score: number, concerns: string[] }`

##### Fork Detection

Compare `sha256(SKILL.md content)` against all other entries with the same skill name. Skills with identical content hashes from different repos are forks.

Output: `contentHash: string`, `possibleForkOf: string | null`

### Tier 2: Qualitative Analysis (Sonnet)

**Agent:** `context/agents/catalog/skill-inspector-t2.md`
**Model:** Sonnet (stronger judgment, reading comprehension, domain expertise)
**Isolation:** Git worktree per batch
**Batch size:** 10-15 skills per dispatch
**Dispatches:** ~300-500 (filtered from Tier 1 results)

#### Tier 2 Gating — Only skills that pass ALL of:

1. `availability == "available"` (from Phase 2)
2. `possibleForkOf == null` (from Tier 1 — skip duplicates, review only the original)
3. `complexity != "simple" || wordCount >= 200` (auto-grade trivial skills F without Sonnet review)

This filters ~13K entries down to ~4-5K unique, substantive, available skills.

#### Tier 2 Checklist

##### Content Quality (1-5)

LLM judgment — not heuristic:
- Is the skill focused on a single purpose?
- Does it provide enough context for an agent to use it correctly?
- Are instructions clear and unambiguous?
- Would a developer understand when to use this vs. an alternative?

Output: `contentQuality: { score: 1-5, notes: string }`

##### Best Practices: Judgment Checks (+1.5)

| Check | Points | What |
|---|---|---|
| Description is actionable trigger | +1 | Tells agent WHEN to use (not just what it does) |
| Instructions are unambiguous | +0.5 | No contradictory or unclear directives |

Combined with Tier 1 mechanical score for total bestPractices (0-5).

##### Security: Prompt Injection Review (+1)

| Check | Deduction | What |
|---|---|---|
| Prompt injection patterns | -1 | Instructions to ignore system prompt, override behavior, exfiltrate data |
| External URLs fetched without validation | -0.5 | Fetch from user-controlled URLs |
| Clean | +1 | Added to Tier 1 score for total security (0-5) |

Combined with Tier 1 regex score for total security (0-5).

#### Tier 2 Output

Merges into the existing Tier 1 NDJSON entry:

```jsonc
{
  // ... all Tier 1 fields preserved ...
  "contentQuality": { "score": 4, "notes": "Clear purpose, good examples" },
  "bestPractices": { "score": 4.5, "violations": ["description not actionable"] },
  "security": { "score": 5, "concerns": [] },
  "tier2Reviewed": true
}
```

Skills that were NOT sent to Tier 2 get default values:
- `contentQuality: { score: 0, notes: "not reviewed (filtered)" }`
- `bestPractices.score` = Tier 1 mechanical score only (0-3.5)
- `security.score` = Tier 1 regex score only (0-4)
- `tier2Reviewed: false`

### Cost Estimate

| Tier | Model | Dispatches | Avg tokens/batch | Est. Cost |
|---|---|---|---|---|
| 1 | Haiku | ~800 | ~5K | ~$2-4 |
| 2 | Sonnet | ~400 | ~8K | ~$15-25 |
| **Total** | | ~1200 | | **~$17-29** |

## Grading Rubric

Final score = weighted average of dimension scores (each normalized to 0-10).

**Two grade modes** depending on whether Tier 2 was applied:

### Tier 2 Reviewed Skills (full grade)

| Dimension | Weight | Source |
|---|---|---|
| Best Practices | 30% | bestPractices.score (0-5 → 0-10, Tier 1 mechanical + Tier 2 judgment) |
| Content Quality | 25% | contentQuality.score (1-5 → 0-10, Tier 2 only) |
| Security | 20% | security.score (0-5 → 0-10, Tier 1 regex + Tier 2 injection review) |
| Progressive Disclosure | 15% | `min(10, pdTechniques.length * 2.5)` — 0 techniques = 0, 4+ = 10 |
| Metadata Completeness | 10% | frontmatter fields present / expected |

### Tier 1 Only Skills (partial grade, flagged)

Skills not sent to Tier 2 (forks, trivial, unavailable) receive a **provisional grade** using only mechanical dimensions. Content Quality is excluded and its weight redistributed:

| Dimension | Weight | Source |
|---|---|---|
| Best Practices (mechanical) | 35% | bestPracticesMechanical.score (0-3.5 → 0-10) |
| Security (regex) | 30% | securityMechanical.score (0-4 → 0-10) |
| Progressive Disclosure | 20% | `min(10, pdTechniques.length * 2.5)` |
| Metadata Completeness | 15% | frontmatter fields present / expected |

Provisional grades are capped at **C** — a skill cannot receive A or B without Tier 2 human-quality judgment. The `tier2Reviewed: false` flag indicates the grade ceiling.

| Grade | Score Range | Meaning |
|---|---|---|
| **A** | 9-10 | Exemplary — reference-quality skill |
| **B** | 7-8 | Good — solid skill with minor gaps |
| **C** | 5-6 | Adequate — functional but could improve |
| **D** | 3-4 | Poor — missing key elements |
| **F** | 0-2 | Failing — broken, empty, or security risk |

## Output Format

### `.catalog.ndjson`

```jsonc
// context/skills/.catalog.ndjson — one line per entry
{
  "source": "org/repo",
  "skill": "skill-name",
  "category": "ai-ml",
  "subcategory": "rag",
  "availability": "available",
  "complexity": "moderate",
  "grade": "B",
  "score": 7.4,
  "wordCount": 1250,
  "sectionCount": 8,
  "fileCount": 3,
  "keywords": ["rag", "vector", "embedding", "retrieval"],
  "internalLinks": ["./assets/diagram.md"],
  "externalLinks": ["https://docs.example.com"],
  "contentHash": "sha256:abc123...",
  "possibleForkOf": null,
  "progressiveDisclosure": true,
  "pdTechniques": ["details-blocks", "overview-before-advanced"],
  "bestPractices": { "score": 4, "violations": ["description not actionable"] },
  "security": { "score": 5, "concerns": [] },
  "contentQuality": { "score": 4, "notes": "Clear purpose, good examples" },
  "reviewedAt": "2026-03-18T15:00:00Z"
}
```

### `.catalog-stats.json`

```json
{
  "totalEntries": 13644,
  "uniqueSkills": 9429,
  "uniqueRepos": 3333,
  "categoryDistribution": { "lang": 1420, "frontend": 950, "..." : "..." },
  "gradeDistribution": { "A": 340, "B": 2100, "C": 4500, "D": 1800, "F": 689 },
  "availabilityDistribution": { "available": 11000, "not_found": 1500, "archived": 800, "..." : "..." },
  "forkClusters": 450,
  "avgScore": 5.8,
  "generatedAt": "2026-03-18T16:00:00Z"
}
```

### Querying with `jq`

```bash
# All A-grade AI skills
jq 'select(.category == "ai-ml" and .grade == "A")' .catalog.ndjson

# Unavailable skills
jq 'select(.availability != "available")' .catalog.ndjson

# Possible forks
jq 'select(.possibleForkOf != null)' .catalog.ndjson

# Skills using progressive disclosure
jq 'select(.progressiveDisclosure == true)' .catalog.ndjson

# Security concerns
jq 'select(.security.score < 3)' .catalog.ndjson

# Keyword search
jq 'select(.keywords | index("kubernetes"))' .catalog.ndjson

# Top skills by score
jq -s 'sort_by(-.score) | .[:20] | .[]' .catalog.ndjson
```

## Pipeline Orchestration

### Phase 1: Taxonomy (offline, no network)

**Input:** `.TODO.yaml` (skill names only)
**Tool:** `ai-tools skill catalog taxonomy` (new subcommand)
**Method:** Hybrid rule engine + LLM batch classification
**Output:** `.taxonomy.yaml`
**Parallelizable:** LLM batches can run in parallel (independent)
**Estimated time:** ~5 min (rules instant, LLM ~200 names/batch × 20 batches)

### Phase 2: Availability Check (network, lightweight)

**Input:** `.TODO.yaml` (source URLs)
**Tool:** `ai-tools skill catalog availability` (new subcommand)
**Method:** HTTP HEAD requests to GitHub, rate-limited
**Output:** Availability field appended to `.catalog.ndjson`
**Parallelizable:** 50 concurrent requests with rate limiting
**Estimated time:** ~15 min at 50 req/batch with 1s delays

### Phase 3: Content Analysis (network + compute, heavy)

**Input:** Available entries from Phase 2
**Tool:** Dispatch `skill-inspector-t1` (Haiku) then `skill-inspector-t2` (Sonnet) agents in worktrees
**Method:** Tier 1: batches of 15-20, 5-10 concurrent. Tier 2: batches of 10-15, 3-5 concurrent (gated by Tier 1 results)
**Output:** Full `.catalog.ndjson` entries
**Parallelizable:** Yes — agents run in isolated worktrees
**Estimated time:** ~4-8 hours (depends on parallelism and network)

**Pre-filter step:** Before dispatching agents, the orchestrator reads `.catalog.ndjson` and filters to only `availability == "available"` entries. This is done via:

```bash
jq 'select(.availability == "available")' .catalog.ndjson > /tmp/catalog-available.ndjson
```

The `analyze` subcommand accepts `--only-available` flag (default: true) to enforce this filter.

**Skip conditions:**
- Skills marked `not_found`, `archived`, or `private` in Phase 2 — excluded by pre-filter, recorded as-is with grade `F` and note "source unavailable"
- Skills already reviewed (by `contentHash` match in existing `.catalog.ndjson`) — skip re-analysis

### Phase 4: Grading & Indexing (offline, fast)

**Input:** `.catalog.ndjson` from Phase 3
**Tool:** `ai-tools skill catalog grade` (new subcommand)
**Method:** Compute weighted scores, detect fork clusters, generate stats
**Output:** Updated `.catalog.ndjson` with grades, `.catalog-stats.json`
**Parallelizable:** Single pass, fast
**Estimated time:** Seconds

### Incremental Updates

When `.TODO.yaml` gains new entries:
1. Diff against existing `.catalog.ndjson` entries
2. Run Phases 1-4 only for new entries
3. Merge results into existing catalog

The `contentHash` field enables deduplication — if a "new" entry has the same hash as an existing entry from a different source, it's marked as a fork without re-analysis.

## CLI Integration

New subcommand tree under `ai-tools skill catalog`:

```
ai-tools skill catalog taxonomy [--force] [--json]
ai-tools skill catalog availability [--concurrency 50] [--json]
ai-tools skill catalog analyze [--batch-size 15] [--concurrency 5] [--json]
ai-tools skill catalog grade [--json]
ai-tools skill catalog stats [--json]
ai-tools skill catalog search <query> [--category <cat>] [--min-grade <grade>] [--json]
ai-tools skill catalog run    # Full pipeline: taxonomy → availability → analyze → grade
```

### Justfile Integration

```just
# context/skills/.catalog/justfile (or in .external/justfile)
mod catalog ".catalog/justfile"

# Invoked as:
just catalog:run          # Full pipeline
just catalog:taxonomy     # Phase 1 only
just catalog:availability # Phase 2 only
just catalog:analyze      # Phase 3 only
just catalog:grade        # Phase 4 only
just catalog:stats        # Show summary
just catalog:search       # Query catalog
```

## Files to Create

| File | Purpose |
|---|---|
| `context/agents/catalog/skill-inspector-t1.md` | Tier 1 mechanical analysis agent (Haiku) |
| `context/agents/catalog/skill-inspector-t2.md` | Tier 2 qualitative analysis agent (Sonnet) |
| `context/skills/.taxonomy.yaml` | Skill name → category mapping (generated) |
| `context/skills/.catalog.ndjson` | Full catalog data (generated) |
| `context/skills/.catalog-stats.json` | Summary statistics (generated) |
| `context/skills/.catalog/justfile` | Catalog pipeline recipes |
| `.scripts/commands/skill.ts` | Add `catalog` subcommand tree |
| `.scripts/lib/taxonomy.ts` | Rule engine + LLM batch classification |
| `.scripts/lib/catalog.ts` | Catalog I/O, grading, fork detection |

## Dependencies

**Existing (already in `.scripts/lib/`):**
- `hash.ts` — content hashing for fork detection
- `output.ts` — table + JSON output
- `schemas.ts` — Valibot schemas for catalog entries
- `github.ts` — authenticated GitHub API for availability checks
- `types.ts` — Result type

**New:**
- `taxonomy.ts` — rule engine + Claude API batch classification
- `catalog.ts` — NDJSON I/O, grading formula, fork clustering

**External tools (already in brewfile):**
- `jq` / `yq` — catalog querying

**External tools (to add to brewfile):**
- `mdq` (yshavit/mdq) — structured markdown analysis (`brew install yshavit/mdq/mdq`)
  - Fallback: existing `lib/chunker.ts` handles frontmatter + section extraction if mdq unavailable

**NPM dependencies (to add to `.scripts/package.json`):**
- `@anthropic-ai/sdk` — Claude API for LLM batch classification in Phase 1
  - Model: `claude-haiku-4-5-20251001` (fast, cheap, sufficient for name classification)
  - Estimated cost: ~19 batches × ~1K tokens ≈ <$0.50 total
  - Phase 1 is resumable: `.taxonomy.yaml` is written incrementally, already-classified names are preserved on retry

## Relationship to TypeScript Migration

This work maps to a **new phase** in the migration plan, after Phase 4b (External Skill Tracking) and potentially parallel to Phases 5-6:

```
Phase 4b: External Skill Tracking  (ai-7q0)
Phase 4c: Skill Catalog Pipeline   (new — depends on 4b for .external/ infra, parallel to Phase 5)
```

The catalog pipeline uses the same `lib/` modules, `ai-tools` CLI, and justfile patterns established in the migration. The inspector agent uses worktree isolation from the `method-git-worktrees-dev` skill.

Note: `.catalog.ndjson` is a generated artifact (~6.5 MB at full catalog size). It should be added to `.gitignore` — the source of truth is `.TODO.yaml` + the pipeline itself. `.taxonomy.yaml` (~470 KB) and `.catalog-stats.json` (small) are committed for auditability. Fork detection hashes persist in `.catalog.ndjson` but can be regenerated.
