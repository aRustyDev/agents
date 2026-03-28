# Matrix Review Viewer

The review viewer is a standalone HTML application built by the `matrixng` CLI.
It displays search-term matrix eval results with interactive commenting, benchmark
metrics, and side-by-side skill vs baseline comparison.

## Building the Viewer

```bash
# Via justfile
just matrixng build <workspace> [options]

# Via npx (when published)
npx @arustydev/matrixng build <workspace> [options]

# Direct
bun run packages/matrixng/src/bin.ts build <workspace> [options]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--skill-path <path>` | auto-detect | Path to the skill directory |
| `--output <path>` / `-o` | `/tmp/matrix-review-<name>.html` | Output HTML file |
| `--iteration <N>` / `-i` | latest | Iteration number |
| `--open` / `--no-open` | `--open` | Open in browser after build |

### Skill Path Auto-Detection

When `--skill-path` is omitted, the CLI looks for the skill directory by:

1. Checking sibling directories of the workspace for a matching `SKILL.md`
   (e.g., `search-term-matrices-workspace` finds `search-term-matrices/SKILL.md`)
2. Walking up to the git root and checking `content/skills/<name>/SKILL.md`
3. If neither resolves, the CLI exits with an error asking for `--skill-path`

## Viewer Layout

```
+-----------------------------------------------------+
|  Header: skill name, iteration #, date              |
+---------+-------------------------------------------+
|  [Outputs]  [Benchmark]              tab bar        |
+---------+-------------------------------------------+
|  [Eval 1] [Eval 2] [Eval 3]         subtab bar     |
+---------+-------------------------------------------+
|  [Rendered] [Edit]                   mode toggle    |
+--------+--------------------------------------------+
| Comment|  Main content area                         |
| sidebar|                                            |
| (toggle|  Rendered matrix markdown                  |
|  able) |  or raw edit mode                          |
|        |                                            |
|        |  Collapsible baseline below                |
+--------+--------------------------------------------+
|  [Export Comments]            [<- Prev] [Next ->]   |
+-----------------------------------------------------+
```

## Tabs

### Outputs Tab

Displays matrix eval results. One subtab per eval case (labeled by eval name,
e.g., "Offline Sync Frameworks").

Each subtab shows:

- **With-skill output** (primary) -- the matrix markdown rendered as formatted HTML
- **Baseline output** (collapsible) -- click "Baseline (without skill)" to expand

#### Rendered Mode (default)

Matrix markdown is rendered as proper HTML with:

- Tables with full formatting (headers, striped rows, hover highlight)
- Headings, bold, italic, inline code, code blocks, lists, blockquotes, links
- Semantic `data-*` attributes on every table cell for the comment system

#### Edit Mode

Toggle with the "Edit" button or press `e`. Shows raw markdown in a read-only
view with line numbers. Useful for copying specific queries or seeing the exact
markdown structure. Comments appear as gutter indicators.

### Benchmark Tab

Two subtabs:

**Metrics** -- Aggregate comparison table:

| Column | Description |
|--------|-------------|
| Configuration | `with_skill` or `without_skill` |
| Eval | Eval case name |
| Pass Rate | Color-coded: green >= 80%, yellow >= 50%, red < 50% |
| Tokens | Total tokens used |
| Duration | Wall-clock time |

Includes per-config aggregate rows and a delta row showing the skill's impact.
Analysis observations (from `benchmark.json`) are listed below the table.

**Criteria Detail** -- Every assertion from every eval, with:

- Pass/fail badge (green checkmark or red X)
- Assertion text
- Click to expand evidence (explanation of why it passed or failed)
- Filter buttons: All, Structural, Quality, Behavioral

## Comment System

The comment system enables cell-level feedback on matrix content. Comments are
anchored semantically to specific parts of the matrix (not line numbers), so they
remain valid even if the matrix is regenerated.

### Adding Comments

In rendered mode, hover over any table cell -- a blue `+` icon appears in the
top-right corner. Click the icon (or double-click the cell) to open the comment
popover. Type your comment and click Save.

### Comment Sidebar

Click the hamburger icon to expand the sidebar. It shows all comments for the
current eval, ordered by document position:

1. Context section
2. Tier 1 rows
3. Tier 2 rows
4. Tier 3 rows
5. Runtime Recovery
6. Grading Summary

Click a comment in the sidebar to scroll to and briefly highlight the anchored
cell. Each comment has Resolve and Delete actions.

### Semantic Anchoring

Comments are anchored by a structured `SemanticAnchor`:

```json
{
  "evalId": 1,
  "configuration": "with_skill",
  "section": "tier1",
  "row": 3,
  "column": "operators"
}
```

The anchor label is auto-generated as a human-readable string:
`"Eval 1 -> Tier 1, Row 3 -> Operators"`.

### Persistence

Comments are saved to `localStorage` (keyed by skill name + iteration number)
and survive page refreshes. They are local to your browser.

### Exporting Comments

Click "Export Comments" in the footer. This downloads a JSON file:

```
comments-<skillName>-iter<N>.json
```

The file contains:

```json
{
  "metadata": {
    "skillName": "search-term-matrices",
    "iteration": 1,
    "exportedAt": "2026-03-26T14:30:00Z"
  },
  "comments": [
    {
      "id": "a7f3c",
      "anchor": { "evalId": 1, "section": "tier1", "row": 3, "column": "operators" },
      "anchorLabel": "Eval 1 -> Tier 1, Row 3 -> Operators",
      "text": "This operator syntax is wrong for Brave Search",
      "timestamp": "2026-03-26T14:22:00Z",
      "resolved": false
    }
  ]
}
```

The agent reads this file and maps each comment back to the matrix via the
`anchor` object. The `anchorLabel` provides a human-readable summary.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `<-` / `->` | Previous / next eval subtab |
| `1` | Switch to Outputs tab |
| `2` | Switch to Benchmark tab |
| `e` | Toggle rendered / edit mode |
| `c` | Open comment sidebar |
| `Esc` | Close comment popover |

Shortcuts are disabled when typing in an input field or textarea.

## Architecture

The viewer is a single self-contained HTML file with no external dependencies.
The `matrixng build` command assembles it from parts:

```
assets/viewer/shell.html     -- HTML frame with placeholders
assets/viewer/styles.css     -- All CSS (inlined into <style>)
scripts/viewer/markdown.js   -- Markdown -> HTML renderer
scripts/viewer/matrix-parser.js -- Markdown -> structured data
scripts/viewer/core.js       -- App controller, tabs, keyboard nav
scripts/viewer/comments.js   -- Comment system, sidebar, export
scripts/viewer/benchmark.js  -- Benchmark tab rendering
```

All JS modules use the `window.MatrixViewer` namespace (IIFE pattern). They are
inlined as `<script>` blocks in dependency order. Eval data is injected as
`window.__VIEWER_DATA__` before the scripts load.

The output is fully offline-capable -- no network requests, no CDN dependencies.

## Workspace Data Format

The viewer reads from a workspace directory with this structure:

```
<workspace>/
  iteration-1/
    eval-1-offline-sync/
      eval_metadata.json         -- eval id, name, prompt, assertions
      with_skill/
        outputs/matrix.md        -- matrix output
        grading.json             -- pass/fail per assertion with evidence
        timing.json              -- tokens and duration
      without_skill/
        outputs/plan.md          -- baseline output
        grading.json
        timing.json
    eval-2-.../
    benchmark.json               -- aggregate metrics and analysis
```

This structure is produced by the skill-creator eval workflow. See the matrixng design spec at `docs/superpowers/specs/2026-03-26-matrixng-viewer-design.md`
in the repository root for the full data model.
