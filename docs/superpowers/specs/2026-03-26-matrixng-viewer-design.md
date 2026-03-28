# matrixng — Search Matrix Review Viewer

> **Date:** 2026-03-26
> **Status:** Draft
> **Skill:** `content/skills/search-term-matrices`
> **Package:** `packages/matrixng`

## Overview

A standalone CLI tool and HTML review viewer for search-term matrices. The CLI reads a workspace directory (eval outputs, grading, benchmarks) and the skill's engine reference files, then assembles a single self-contained HTML file for interactive review.

The viewer provides markdown rendering with edit mode, semantic cell-level comments with JSON export, tabbed navigation across matrices, and benchmark metrics. A second pass adds analysis overlays: structural compliance badges, operator hover tooltips, tier progression visualization, and decomposition suggestions.

## Goals

- Ship a review viewer alongside the `search-term-matrices` skill
- Enable human-in-the-loop feedback via semantic comments exportable to JSON
- Provide structural and qualitative analysis of matrix outputs
- Standalone package — no dependency on `@agents/cli` or `@agents/sdk`, usable via `npx`

## Architecture

### Data Flow

```
Workspace dir + Skill engine references
        │
        ▼
  matrixng CLI (parse + assemble)
        │
        ▼
  ViewerData JSON blob
        │
        ▼
  Inject into shell.html + inline all JS/CSS
        │
        ▼
  Single standalone HTML file (offline-capable)
```

### Directory Structure

```
content/skills/search-term-matrices/
├── SKILL.md
├── references/                       # Existing engine refs, grading, etc.
├── evals/                            # Existing eval definitions
├── assets/
│   └── viewer/
│       ├── shell.html                # Outer HTML frame, layout grid
│       └── styles.css                # Styles (inlined at build)
└── scripts/
    └── viewer/
        ├── core.js                   # Tab/subtab mgmt, state, markdown toggle, keyboard nav
        ├── comments.js               # Semantic comment system + export
        ├── markdown.js               # Markdown → HTML renderer (tables, headings, code)
        ├── matrix-parser.js          # Raw markdown → ParsedMatrix structure
        ├── benchmark.js              # Benchmark tab rendering
        └── overlays/                 # Pass 2
            ├── structural.js         # Compliance checklist badges
            ├── operators.js          # Hover tooltips from engine refs
            ├── progression.js        # Tier broadening visualization
            └── decomposition.js      # Heuristic decomposition suggestions

packages/matrixng/
├── package.json                      # @arustydev/matrixng, bin: "matrixng"
└── src/
    ├── bin.ts                        # CLI entry (citty)
    ├── build.ts                      # Orchestrates the build pipeline
    ├── parse-workspace.ts            # Workspace dir → EvalCase[] + Benchmark
    ├── parse-engines.ts              # Engine .md → EngineOperator[]
    ├── parse-markdown-table.ts       # Markdown table → structured rows
    └── assemble.ts                   # Template + JS/CSS + data → HTML
```

### Workspace Directory Layout

The CLI expects this structure, produced by the skill-creator eval workflow:

```
<workspace>/
├── iteration-1/
│   ├── eval-1-offline-sync/
│   │   ├── eval_metadata.json        # { eval_id, eval_name, prompt, assertions[] }
│   │   ├── with_skill/
│   │   │   ├── outputs/
│   │   │   │   └── matrix.md         # The matrix output
│   │   │   ├── grading.json          # { expectations[]: { text, passed, evidence } }
│   │   │   └── timing.json           # { total_tokens, duration_ms }
│   │   └── without_skill/
│   │       ├── outputs/
│   │       │   └── plan.md           # Baseline output
│   │       ├── grading.json
│   │       └── timing.json
│   ├── eval-2-llm-regulatory/
│   │   └── ...                       # Same structure
│   ├── eval-3-webtransport/
│   │   └── ...
│   └── benchmark.json                # Aggregate metrics (per-iteration)
├── iteration-2/
│   └── ...
└── ...
```

Files are JSON. `eval_metadata.json` and `grading.json` schemas are defined in the Data Model section below.

### SDK/Core Extraction Candidates

These modules stay in `matrixng` for now. Extract when stable:

| Module | Future home | Rationale |
|--------|------------|-----------|
| `parse-markdown-table.ts` | `@agents/core` | Generic — any skill can use it |
| `parse-workspace.ts` | `@agents/sdk` | Workspace eval conventions are a shared pattern |
| `parse-engines.ts` | stays | Skill-specific operator extraction |
| `assemble.ts` | stays | Viewer-specific HTML assembly |

### Package Scope

`@arustydev/matrixng` — published to npm for standalone use via `npx`. This is a consumer package, not a workspace-internal `@agents/` package. It has no dependency on `@agents/cli` or `@agents/sdk`. The SDK design references `@agents/*-viewer` as a consumer pattern; this package fulfills that role under the `@arustydev/` scope used for published tools.

The package is **not** registered as a subcommand of the `agents` CLI. It is standalone only. Integration with `just agents` may be added later via a thin wrapper but is out of scope.

## Data Model

### ViewerData (CLI → Viewer)

```typescript
interface ViewerData {
  skillName: string;
  iteration: number;
  generatedAt: string;
  evals: EvalCase[];
  benchmark: Benchmark;
  engineOperators: Record<string, EngineOperator[]>; // Pass 2
}

interface EvalCase {
  evalId: number;
  evalName: string;
  prompt: string;
  configurations: {
    with_skill: RunData;
    without_skill: RunData;
  };
  assertions: Assertion[];
}

interface RunData {
  raw: string;                  // Full markdown output
  parsed: ParsedMatrix;         // Structured extraction
  grading: GradingResult;       // From grading.json
  timing: { total_tokens: number; duration_ms: number };
}

interface Assertion {
  id: string;                   // e.g. "matrix-structure"
  text: string;                 // Human-readable assertion description
  type: "structural" | "quality" | "behavioral";
}

interface GradingResult {
  pass_rate: number;            // 0.0 - 1.0
  passed: number;
  total: number;
  expectations: GradedExpectation[];
}

interface GradedExpectation {
  text: string;                 // Assertion text (matches Assertion.text)
  passed: boolean;
  evidence: string;             // Explanation of why it passed/failed
}
```

### ParsedMatrix

```typescript
interface ParsedMatrix {
  context: { goal: string; type: string; domain: string } | null;
  tiers: Tier[];
  runtimeRecovery: string[];
  gradingSummary: string;
  decomposition: { subQuestions: string[]; executionOrder: string } | null;
}

interface Tier {
  level: 1 | 2 | 3;
  label: string;
  rows: MatrixRow[];
}

interface MatrixRow {
  num: number;
  engines: string[];
  query: string;
  operators: string;
  expectedResults: string;
  acceptance: string;
  success: string;
}
```

### Benchmark

```typescript
interface Benchmark {
  configurations: BenchmarkConfig[];
  delta: Record<string, string>;
  analysis: { observations: string[] };
}

interface BenchmarkConfig {
  name: string;
  evals: { eval_name: string; pass_rate: number; tokens: number; duration_seconds: number }[];
  aggregate: { mean_pass_rate: number; mean_tokens: number; mean_duration_seconds: number };
}
```

### Engine Operators (Pass 2)

```typescript
interface EngineOperator {
  engine: string;               // "Google", "GitHub", etc.
  operator: string;             // "site:", "language:", etc.
  syntax: string;               // "site:domain"
  example: string;              // "site:reddit.com CRDT"
  description: string;          // From reference table row
}
```

### Semantic Comments (Viewer → File)

```typescript
interface CommentFile {
  metadata: {
    skillName: string;
    iteration: number;
    exportedAt: string;
  };
  comments: Comment[];
}

interface Comment {
  id: string;
  anchor: SemanticAnchor;
  anchorLabel: string;          // Human-readable: "Eval 1 → Tier 1, Row 3 → Operators"
  text: string;
  timestamp: string;
  resolved: boolean;
}

interface SemanticAnchor {
  evalId: number;
  configuration: "with_skill" | "without_skill";
  section: "context" | "tier1" | "tier2" | "tier3" | "recovery" | "grading" | "decomposition";
  row?: number;
  column?: "engines" | "query" | "operators" | "expected" | "acceptance" | "success";
  // Reserved for Pass 2 token-level comments:
  token?: string;
  tokenOffset?: number;
}
```

## CLI Interface

```bash
# Published package (standalone)
npx @arustydev/matrixng build <workspace> [options]

# Local dev
bun run packages/matrixng/src/bin.ts build <workspace> [options]
```

This is a standalone CLI. It is not registered as a subcommand of `just agents`.

### `build` command options

| Flag | Default | Description |
|------|---------|-------------|
| `--skill-path <path>` | auto-detect | Path to skill dir for engine refs |
| `--output <path>` | `/tmp/matrix-review-<name>.html` | Output HTML path |
| `--iteration <N>` | latest (highest N) | Which iteration directory |
| `--open` / `--no-open` | `--open` | Open in browser after build |

### `--skill-path` auto-detection

When `--skill-path` is not provided, the CLI resolves it with:

1. Check if `<workspace>` is a sibling of a directory containing `SKILL.md` (i.e., `<workspace>/../<skill-name>/SKILL.md`). This handles the common case where workspace is `content/skills/search-term-matrices-workspace/` next to the skill dir.
2. Check if `<workspace>` is inside a git repo, and look for `content/skills/*/SKILL.md` relative to the repo root.
3. If neither resolves, require `--skill-path` explicitly.

### Build pipeline

1. **Resolve paths** — workspace, skill dir, iteration dir
2. **Parse workspace** (`parse-workspace.ts`):
   - Walk `iteration-N/eval-*/` directories
   - Read `eval_metadata.json` for eval name, prompt, assertions
   - Read `with_skill/outputs/*.md` and `without_skill/outputs/*.md` for matrix content
   - Read `*/grading.json` for assertion results
   - Read `*/timing.json` for token/duration data
   - Read `benchmark.json` from the iteration root
3. **Parse engine references** (`parse-engines.ts`):
   - Read `references/engines/*.md` from skill path
   - Extract operator tables into `EngineOperator[]` lookup
   - Pass 1: stub returning `{}`
4. **Assemble HTML** (`assemble.ts`):
   - Read `assets/viewer/shell.html`
   - Inline `assets/viewer/styles.css` into `<style>`
   - Inline JS files from `scripts/viewer/` in this order:
     1. `markdown.js` (no dependencies)
     2. `matrix-parser.js` (depends on markdown)
     3. `core.js` (depends on matrix-parser)
     4. `comments.js` (depends on core)
     5. `benchmark.js` (depends on core)
     6. Pass 2: `overlays/*.js` (depend on core + matrix-parser)
   - Inject `window.__VIEWER_DATA__ = { ... };` before app scripts
   - Write to output path
5. **Open** — `open <output-path>` (macOS) / `xdg-open` (Linux) unless `--no-open`

All JS files use an IIFE or `window.MatrixViewer` namespace pattern so load order defines availability but avoids global pollution.

## Viewer Design

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Header: skill name, iteration #, generated date    │
├─────────────────────────────────────────────────────┤
│  [Outputs]  [Benchmark]                   tab bar   │
├─────────────────────────────────────────────────────┤
│  [Offline Sync] [LLM Regulatory] [WebTransport]     │
├────────────┬────────────────────────────────────────┤
│  Comment   │  Main content: rendered matrix          │
│  sidebar   │  (or edit mode, or overlay views)       │
│  (toggle)  │                                        │
├────────────┼────────────────────────────────────────┤
│            │  [Export Comments]  [← Prev] [Next →]  │
└────────────┴────────────────────────────────────────┘
```

### Tab 1: Outputs

- Subtab per eval case, labeled by eval name
- Each subtab shows with_skill output (primary), baseline collapsible below
- Default: rendered markdown with tables as proper `<table>` elements
- Toggle to edit mode: raw markdown with line numbers (read-only, for copying)
- All table cells annotated with `data-anchor` attributes for comment targeting
- Pass 2 adds view selector ribbon: `[Rendered] [Structural] [Operators] [Progression] [Decomposition]`

### Tab 2: Benchmark

- **Subtab A — Metrics Table**: per-eval and aggregate pass rates, tokens, duration, delta column. With_skill rows before baseline rows.
- **Subtab B — Criteria Detail**: every assertion listed with pass/fail badge and evidence text. Grouped by eval, filterable by type (structural / quality / behavioral).

### Rendered mode

- Markdown tables → HTML `<table>` with semantic `data-*` attributes
- Each cell: `data-eval="1" data-section="tier1" data-row="3" data-col="operators"`
- Section headings annotated at block level
- Click any cell → comment popover
- Comments in sidebar scroll-linked to anchored elements

### Edit mode

- Raw markdown in read-only `<pre>` with line numbers
- Comment anchors shown as gutter icons mapped from semantic position
- For reading/copying, not modifying

### Keyboard navigation

| Key | Action |
|-----|--------|
| `←` / `→` | Previous/next subtab |
| `1` / `2` | Switch to Outputs / Benchmark tab |
| `e` | Toggle edit/rendered |
| `c` | Focus comment sidebar |
| `Esc` | Close popover |

Note: `Tab` key is not intercepted — it retains native browser focus behavior for accessibility.

### Comment UX

- Hover annotated cell → comment icon appears
- Click icon → inline popover with auto-generated anchor label + textarea
- Sidebar shows all comments for current subtab, ordered by document position (context → tiers → recovery → grading)
- Clicking sidebar comment scrolls to and highlights anchored element
- Comments persist in `localStorage` keyed by `skillName + iteration`
- Resolved comments dimmed but visible
- Export downloads `comments-<skillName>-iter<N>.json`

## Pass Scoping

### Pass 1: Core Viewer

**Goal:** Ship the skill with a functional review viewer.

**CLI (`packages/matrixng/`):**
- `build` command with full pipeline
- `parse-workspace.ts`, `parse-markdown-table.ts`, `assemble.ts`
- `parse-engines.ts` as stub returning `{}`

**Viewer assets (`content/skills/search-term-matrices/`):**
- `assets/viewer/shell.html` + `styles.css`
- `scripts/viewer/core.js` — tabs, subtabs, toggle, keyboard nav
- `scripts/viewer/markdown.js` — markdown → HTML with table support
- `scripts/viewer/matrix-parser.js` — raw → ParsedMatrix
- `scripts/viewer/comments.js` — cell-level comments, sidebar, localStorage, JSON export
- `scripts/viewer/benchmark.js` — metrics table + criteria detail

### Pass 2: Analysis Overlays

**CLI additions:**
- `parse-engines.ts` full implementation

**Viewer additions (`scripts/viewer/overlays/`):**
- `structural.js` — green/red badges on required sections per grading assertions
- `operators.js` — hover tooltips matching operator tokens to engine reference data
- `progression.js` — side-by-side tier columns with broadening indicators and precision tags
- `decomposition.js` — heuristic flags: >5 Tier 1 rows, 3+ engine categories, mixed domains, independent sub-queries. Rendered as suggestion cards.

**Comment system additions:**
- Token-level selection within cells (`token` + `tokenOffset` on anchor)
- Selection UI paired with operator hover

**CLI additions:**
- `--previous <workspace-path>` flag — loads previous iteration data for diff view. Adds `previousEvals: EvalCase[]` to `ViewerData`. Viewer renders a collapsible "Previous Output" section per subtab.

**View selector ribbon** on each Outputs subtab — overlays are toggleable and combinable (e.g., structural badges + operator hover simultaneously).
