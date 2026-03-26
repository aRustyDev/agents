# matrixng Pass 1 — Core Viewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `packages/matrixng` CLI and HTML review viewer so the `search-term-matrices` skill has a functional eval review tool.

**Architecture:** A standalone Bun/TypeScript CLI reads a workspace directory + skill engine references, parses them into a `ViewerData` JSON blob, and assembles a single self-contained HTML file by inlining JS/CSS/data into a shell template. The viewer is vanilla JS with no framework — 5 modules (core, markdown, matrix-parser, comments, benchmark) loaded via IIFE pattern into a `window.MatrixViewer` namespace.

**Tech Stack:** Bun, TypeScript, citty (CLI framework), vanilla JS/CSS/HTML (viewer), bun:test (testing)

**Spec:** `docs/superpowers/specs/2026-03-26-matrixng-viewer-design.md`

**Test fixture:** Real workspace data at `content/skills/search-term-matrices-workspace/iteration-1/`

**Prerequisite:** The `search-term-matrices` skill files and eval workspace must exist before starting. If they don't exist on disk (e.g., were created in a prior conversation but never committed), re-run the skill creation first:

1. Recreate the 11 skill files per the design spec in memory (`project_search_term_matrices_skill.md`)
2. Run the 6 eval agents (3 with-skill, 3 baseline) to produce workspace data
3. Grade all outputs and create `benchmark.json`
4. Commit the skill and workspace data before proceeding with this plan

**Companion code:** Tasks 6, 8-11 produce browser JS/CSS files. Full implementation code for these is in `docs/superpowers/plans/matrixng-pass1-viewer-code/` — one file per module. The plan describes responsibilities and interfaces; the companion files contain the complete code.

---

## Task 1: Package Scaffolding

**Files:**

- Create: `packages/matrixng/package.json`
- Create: `packages/matrixng/tsconfig.json`
- Create: `packages/matrixng/src/types.ts`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "@arustydev/matrixng",
  "version": "0.1.0",
  "type": "module",
  "bin": {
    "matrixng": "./src/bin.ts"
  },
  "exports": {
    ".": "./src/index.ts",
    "./*": "./src/*.ts"
  },
  "dependencies": {
    "citty": "^0.2.1",
    "fast-glob": "^3.3.3"
  },
  "devDependencies": {}
}
```

Note: This package has NO dependency on `@agents/core`, `@agents/sdk`, or `@agents/cli`. It is standalone.

- [ ] **Step 2: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "outDir": "./dist",
    "rootDir": ".",
    "types": ["bun-types"]
  },
  "include": ["src/**/*.ts", "test/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 3: Create src/types.ts with all shared interfaces**

This file defines the `ViewerData` contract and all sub-types from the spec. Every other module imports from here.

```typescript
// === ViewerData: CLI → Viewer ===

export interface ViewerData {
  skillName: string
  iteration: number
  generatedAt: string
  evals: EvalCase[]
  benchmark: Benchmark
  engineOperators: Record<string, EngineOperator[]>
}

export interface EvalCase {
  evalId: number
  evalName: string
  prompt: string
  configurations: {
    with_skill: RunData
    without_skill: RunData
  }
  assertions: Assertion[]
}

export interface RunData {
  raw: string
  parsed: ParsedMatrix
  grading: GradingResult
  timing: { total_tokens: number; duration_ms: number }
}

export interface Assertion {
  id: string
  text: string
  type: 'structural' | 'quality' | 'behavioral'
}

export interface GradingResult {
  pass_rate: number
  passed: number
  total: number
  expectations: GradedExpectation[]
}

export interface GradedExpectation {
  text: string
  passed: boolean
  evidence: string
}

// === ParsedMatrix ===

export interface ParsedMatrix {
  context: { goal: string; type: string; domain: string } | null
  tiers: Tier[]
  runtimeRecovery: string[]
  gradingSummary: string
  decomposition: { subQuestions: string[]; executionOrder: string } | null
}

export interface Tier {
  level: 1 | 2 | 3
  label: string
  rows: MatrixRow[]
}

export interface MatrixRow {
  num: number
  engines: string[]
  query: string
  operators: string
  expectedResults: string
  acceptance: string
  success: string
}

// === Benchmark ===

export interface Benchmark {
  configurations: BenchmarkConfig[]
  delta: Record<string, string>
  analysis: { observations: string[] }
}

export interface BenchmarkConfig {
  name: string
  evals: { eval_name: string; pass_rate: number; tokens: number; duration_seconds: number }[]
  aggregate: { mean_pass_rate: number; mean_tokens: number; mean_duration_seconds: number }
}

// === Engine Operators (Pass 2 — stub for now) ===

export interface EngineOperator {
  engine: string
  operator: string
  syntax: string
  example: string
  description: string
}

// === Semantic Comments (Viewer → File) ===

export interface CommentFile {
  metadata: {
    skillName: string
    iteration: number
    exportedAt: string
  }
  comments: Comment[]
}

export interface Comment {
  id: string
  anchor: SemanticAnchor
  anchorLabel: string
  text: string
  timestamp: string
  resolved: boolean
}

export interface SemanticAnchor {
  evalId: number
  configuration: 'with_skill' | 'without_skill'
  section: 'context' | 'tier1' | 'tier2' | 'tier3' | 'recovery' | 'grading' | 'decomposition'
  row?: number
  column?: 'engines' | 'query' | 'operators' | 'expected' | 'acceptance' | 'success'
  token?: string
  tokenOffset?: number
}
```

- [ ] **Step 4: Create src/index.ts barrel export**

```typescript
export * from './types'
```

- [ ] **Step 5: Fix `_init-bun` in justfile for workspace discovery**

The existing recipe only installs CLI deps. Update it to run root-level `bun install`:

```justfile
[private]
_init-bun:
    @echo "Installing TypeScript dependencies..."
    @bun install --silent
```

- [ ] **Step 6: Install dependencies**

Run: `cd /private/etc/infra/pub/agents && bun install`

This will discover the new workspace package and install its dependencies.

- [ ] **Step 7: Verify TypeScript compiles**

Run: `cd packages/matrixng && bunx tsc --noEmit`
Expected: No errors

- [ ] **Step 8: Commit**

```bash
git add packages/matrixng/package.json packages/matrixng/tsconfig.json packages/matrixng/src/types.ts packages/matrixng/src/index.ts justfile bun.lock
git commit -m "feat(matrixng): scaffold package with types"
```

---

## Task 2: Markdown Table Parser

**Files:**

- Create: `packages/matrixng/src/parse-markdown-table.ts`
- Create: `packages/matrixng/test/parse-markdown-table.test.ts`

This is a generic utility that extracts markdown tables into structured arrays. Future extraction candidate for `@agents/core`.

- [ ] **Step 1: Write the failing test**

```typescript
import { describe, expect, test } from 'bun:test'
import { parseMarkdownTable, findAllTables, type TableRow } from '../src/parse-markdown-table'

const SIMPLE_TABLE = `
| # | Engine(s) | Query | Operators |
|---|-----------|-------|-----------|
| 1 | Google | CRDT typescript | site:dev.to |
| 2 | GitHub, npm | offline sync | stars:>50 |
`.trim()

const TABLE_WITH_PIPES_IN_CELLS = `
| # | Query | Operators |
|---|-------|-----------|
| 1 | "A | B" | site:x.com |
`.trim()

describe('parseMarkdownTable', () => {
  test('parses a simple table into row objects', () => {
    const rows = parseMarkdownTable(SIMPLE_TABLE)
    expect(rows).toHaveLength(2)
    expect(rows[0]).toEqual({
      '#': '1',
      'Engine(s)': 'Google',
      'Query': 'CRDT typescript',
      'Operators': 'site:dev.to',
    })
    expect(rows[1]['Engine(s)']).toBe('GitHub, npm')
  })

  test('returns empty array for non-table input', () => {
    expect(parseMarkdownTable('just some text')).toEqual([])
    expect(parseMarkdownTable('')).toEqual([])
  })

  test('handles single-row table', () => {
    const table = '| A | B |\n|---|---|\n| 1 | 2 |'
    const rows = parseMarkdownTable(table)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toEqual({ A: '1', B: '2' })
  })

  test('trims whitespace from headers and cells', () => {
    const table = '|  Name  |  Value  |\n|---|---|\n|  foo  |  bar  |'
    const rows = parseMarkdownTable(table)
    expect(rows[0]).toEqual({ Name: 'foo', Value: 'bar' })
  })
})

describe('findAllTables', () => {
  test('finds multiple tables in a document', () => {
    const doc = `# Heading

| A | B |
|---|---|
| 1 | 2 |

Some text between tables.

| X | Y |
|---|---|
| 3 | 4 |
| 5 | 6 |`
    const tables = findAllTables(doc)
    expect(tables).toHaveLength(2)
    expect(tables[0]).toHaveLength(1)
    expect(tables[1]).toHaveLength(2)
    expect(tables[0][0]).toEqual({ A: '1', B: '2' })
    expect(tables[1][1]).toEqual({ X: '5', Y: '6' })
  })

  test('returns empty array for document with no tables', () => {
    expect(findAllTables('just text\nmore text')).toEqual([])
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bun test packages/matrixng/test/parse-markdown-table.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Implement parse-markdown-table.ts**

```typescript
export type TableRow = Record<string, string>

/**
 * Parse a markdown table string into an array of row objects.
 * Keys are the header column names. Values are trimmed cell text.
 * Returns [] if the input doesn't contain a valid markdown table.
 */
export function parseMarkdownTable(markdown: string): TableRow[] {
  const lines = markdown.split('\n').filter((l) => l.trim().length > 0)

  // Need at least header + separator + one data row
  if (lines.length < 3) return []

  const headerLine = lines[0]
  const separatorLine = lines[1]

  // Validate: header must have pipes, separator must have dashes
  if (!headerLine.includes('|') || !separatorLine.match(/^\|?[\s-:|]+\|?$/)) return []

  const headers = splitTableRow(headerLine)
  if (headers.length === 0) return []

  const rows: TableRow[] = []
  for (let i = 2; i < lines.length; i++) {
    const cells = splitTableRow(lines[i])
    if (cells.length === 0) continue
    const row: TableRow = {}
    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = cells[j] ?? ''
    }
    rows.push(row)
  }

  return rows
}

/**
 * Split a markdown table row into trimmed cell values.
 * Handles leading/trailing pipes.
 */
function splitTableRow(line: string): string[] {
  let trimmed = line.trim()
  if (trimmed.startsWith('|')) trimmed = trimmed.slice(1)
  if (trimmed.endsWith('|')) trimmed = trimmed.slice(0, -1)
  return trimmed.split('|').map((cell) => cell.trim())
}

/**
 * Find all markdown tables in a document and parse each.
 * Returns an array of table arrays — one per table found.
 */
export function findAllTables(markdown: string): TableRow[][] {
  const tables: TableRow[][] = []
  const lines = markdown.split('\n')
  let i = 0

  while (i < lines.length) {
    // Look for a line that looks like a table header (has pipes)
    if (lines[i].includes('|') && i + 1 < lines.length && lines[i + 1].match(/^\|?[\s-:|]+\|?$/)) {
      // Collect contiguous table lines
      const tableLines: string[] = []
      let j = i
      while (j < lines.length && lines[j].includes('|')) {
        tableLines.push(lines[j])
        j++
      }
      const parsed = parseMarkdownTable(tableLines.join('\n'))
      if (parsed.length > 0) tables.push(parsed)
      i = j
    } else {
      i++
    }
  }

  return tables
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bun test packages/matrixng/test/parse-markdown-table.test.ts`
Expected: All 4 tests pass

- [ ] **Step 5: Commit**

```bash
git add packages/matrixng/src/parse-markdown-table.ts packages/matrixng/test/parse-markdown-table.test.ts
git commit -m "feat(matrixng): add markdown table parser"
```

---

## Task 3: Workspace Parser

**Files:**

- Create: `packages/matrixng/src/parse-workspace.ts`
- Create: `packages/matrixng/test/parse-workspace.test.ts`

Reads the workspace directory structure and assembles `ViewerData`. This is the heaviest parsing module — it reads eval_metadata, outputs, grading, timing, and benchmark files.

- [ ] **Step 1: Write the failing test using real workspace data**

The test uses the actual workspace from the skill eval runs at `content/skills/search-term-matrices-workspace/`.

```typescript
import { describe, expect, test } from 'bun:test'
import { resolve } from 'node:path'
import { parseWorkspace } from '../src/parse-workspace'

const WORKTREE = resolve(import.meta.dir, '../../..')
const WORKSPACE = resolve(WORKTREE, 'content/skills/search-term-matrices-workspace')

describe('parseWorkspace', () => {
  test('parses iteration-1 with 3 evals', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    expect(result.evals).toHaveLength(3)
    expect(result.benchmark).toBeDefined()
    expect(result.benchmark.configurations).toHaveLength(2)
  })

  test('each eval has both configurations', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    for (const ev of result.evals) {
      expect(ev.configurations.with_skill).toBeDefined()
      expect(ev.configurations.without_skill).toBeDefined()
      expect(ev.configurations.with_skill.raw.length).toBeGreaterThan(0)
      expect(ev.configurations.without_skill.raw.length).toBeGreaterThan(0)
    }
  })

  test('grading data is populated', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    const eval1 = result.evals.find((e) => e.evalId === 1)!
    expect(eval1.configurations.with_skill.grading.pass_rate).toBe(1.0)
    expect(eval1.configurations.with_skill.grading.expectations.length).toBeGreaterThan(0)
  })

  test('timing data is populated', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    const eval1 = result.evals.find((e) => e.evalId === 1)!
    expect(eval1.configurations.with_skill.timing.total_tokens).toBeGreaterThan(0)
    expect(eval1.configurations.with_skill.timing.duration_ms).toBeGreaterThan(0)
  })

  test('auto-detects latest iteration when not specified', async () => {
    const result = await parseWorkspace(WORKSPACE)
    expect(result.evals.length).toBeGreaterThan(0)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bun test packages/matrixng/test/parse-workspace.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Implement parse-workspace.ts**

```typescript
import { readdir, readFile } from 'node:fs/promises'
import { join, basename } from 'node:path'
import type { EvalCase, RunData, Benchmark, Assertion, GradingResult, ParsedMatrix } from './types'

export interface WorkspaceData {
  evals: EvalCase[]
  benchmark: Benchmark
}

/**
 * Parse a workspace directory into structured eval data.
 * If iteration is not specified, uses the highest-numbered iteration-N directory.
 */
export async function parseWorkspace(workspacePath: string, iteration?: number): Promise<WorkspaceData> {
  const iterDir = await resolveIterationDir(workspacePath, iteration)
  const evalDirs = await findEvalDirs(iterDir)
  const evals = await Promise.all(evalDirs.map((dir) => parseEvalDir(dir)))
  const benchmark = await readJsonFile<Benchmark>(join(iterDir, 'benchmark.json'))

  return { evals, benchmark }
}

async function resolveIterationDir(workspacePath: string, iteration?: number): Promise<string> {
  if (iteration !== undefined) {
    return join(workspacePath, `iteration-${iteration}`)
  }
  const entries = await readdir(workspacePath)
  const iterDirs = entries
    .filter((e) => e.match(/^iteration-\d+$/))
    .sort((a, b) => {
      const numA = parseInt(a.split('-')[1])
      const numB = parseInt(b.split('-')[1])
      return numB - numA // Descending — latest first
    })
  if (iterDirs.length === 0) throw new Error(`No iteration directories found in ${workspacePath}`)
  return join(workspacePath, iterDirs[0])
}

async function findEvalDirs(iterDir: string): Promise<string[]> {
  const entries = await readdir(iterDir, { withFileTypes: true })
  return entries
    .filter((e) => e.isDirectory() && e.name.startsWith('eval-'))
    .map((e) => join(iterDir, e.name))
    .sort()
}

async function parseEvalDir(evalDir: string): Promise<EvalCase> {
  const metadata = await readJsonFile<{
    eval_id: number
    eval_name: string
    prompt: string
    assertions: Assertion[]
  }>(join(evalDir, 'eval_metadata.json'))

  const withSkill = await parseRunData(join(evalDir, 'with_skill'))
  const withoutSkill = await parseRunData(join(evalDir, 'without_skill'))

  return {
    evalId: metadata.eval_id,
    evalName: metadata.eval_name,
    prompt: metadata.prompt,
    configurations: {
      with_skill: withSkill,
      without_skill: withoutSkill,
    },
    assertions: metadata.assertions,
  }
}

async function parseRunData(runDir: string): Promise<RunData> {
  // Read the first .md file from outputs/
  const outputsDir = join(runDir, 'outputs')
  const outputFiles = await readdir(outputsDir)
  const mdFile = outputFiles.find((f) => f.endsWith('.md'))
  const raw = mdFile ? await readFile(join(outputsDir, mdFile), 'utf-8') : ''

  const grading = await readJsonFile<GradingResult>(join(runDir, 'grading.json'))
  const timing = await readJsonFile<{ total_tokens: number; duration_ms: number }>(
    join(runDir, 'timing.json')
  )

  // ParsedMatrix extraction is done client-side by matrix-parser.js
  // Server-side we pass a stub — the viewer JS handles the parsing
  const parsed: ParsedMatrix = {
    context: null,
    tiers: [],
    runtimeRecovery: [],
    gradingSummary: '',
    decomposition: null,
  }

  return { raw, parsed, grading, timing }
}

async function readJsonFile<T>(path: string): Promise<T> {
  const content = await readFile(path, 'utf-8')
  return JSON.parse(content) as T
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bun test packages/matrixng/test/parse-workspace.test.ts`
Expected: All 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add packages/matrixng/src/parse-workspace.ts packages/matrixng/test/parse-workspace.test.ts
git commit -m "feat(matrixng): add workspace parser"
```

---

## Task 4: Engine Parser Stub + Assembler

**Files:**

- Create: `packages/matrixng/src/parse-engines.ts`
- Create: `packages/matrixng/src/assemble.ts`
- Create: `packages/matrixng/test/assemble.test.ts`

- [ ] **Step 1: Create parse-engines.ts stub**

```typescript
import type { EngineOperator } from './types'

/**
 * Parse engine reference markdown files into operator lookup.
 * Pass 1: stub returning empty object.
 * Pass 2: will read references/engines/*.md and extract operator tables.
 */
export async function parseEngineReferences(
  _skillPath: string
): Promise<Record<string, EngineOperator[]>> {
  return {}
}
```

- [ ] **Step 2: Write the failing assembler test**

```typescript
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdtemp, rm, mkdir, writeFile, readFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { assembleHtml } from '../src/assemble'
import type { ViewerData } from '../src/types'

let tmpDir: string

beforeEach(async () => {
  tmpDir = await mkdtemp(join(tmpdir(), 'matrixng-test-'))
})

afterEach(async () => {
  await rm(tmpDir, { recursive: true, force: true })
})

const MINIMAL_VIEWER_DATA: ViewerData = {
  skillName: 'test-skill',
  iteration: 1,
  generatedAt: '2026-03-26T00:00:00Z',
  evals: [],
  benchmark: { configurations: [], delta: {}, analysis: { observations: [] } },
  engineOperators: {},
}

describe('assembleHtml', () => {
  test('produces a valid HTML file with injected data', async () => {
    // Create minimal template files
    const assetsDir = join(tmpDir, 'assets', 'viewer')
    const scriptsDir = join(tmpDir, 'scripts', 'viewer')
    await mkdir(assetsDir, { recursive: true })
    await mkdir(scriptsDir, { recursive: true })

    await writeFile(join(assetsDir, 'shell.html'), `<!DOCTYPE html>
<html><head><!--STYLES--></head><body><!--SCRIPTS--></body></html>`)
    await writeFile(join(assetsDir, 'styles.css'), 'body { margin: 0; }')
    await writeFile(join(scriptsDir, 'markdown.js'), '// markdown')
    await writeFile(join(scriptsDir, 'matrix-parser.js'), '// parser')
    await writeFile(join(scriptsDir, 'core.js'), '// core')
    await writeFile(join(scriptsDir, 'comments.js'), '// comments')
    await writeFile(join(scriptsDir, 'benchmark.js'), '// benchmark')

    const outputPath = join(tmpDir, 'output.html')
    await assembleHtml(tmpDir, MINIMAL_VIEWER_DATA, outputPath)

    const html = await readFile(outputPath, 'utf-8')
    expect(html).toContain('<!DOCTYPE html>')
    expect(html).toContain('body { margin: 0; }')
    expect(html).toContain('window.__VIEWER_DATA__')
    expect(html).toContain('"test-skill"')
    expect(html).toContain('// markdown')
    expect(html).toContain('// core')
    expect(html).toContain('// comments')
    expect(html).toContain('// benchmark')
  })

  test('inlines JS files in correct order', async () => {
    const assetsDir = join(tmpDir, 'assets', 'viewer')
    const scriptsDir = join(tmpDir, 'scripts', 'viewer')
    await mkdir(assetsDir, { recursive: true })
    await mkdir(scriptsDir, { recursive: true })

    await writeFile(join(assetsDir, 'shell.html'), '<html><head><!--STYLES--></head><body><!--SCRIPTS--></body></html>')
    await writeFile(join(assetsDir, 'styles.css'), '')
    await writeFile(join(scriptsDir, 'markdown.js'), '/* 1-markdown */')
    await writeFile(join(scriptsDir, 'matrix-parser.js'), '/* 2-parser */')
    await writeFile(join(scriptsDir, 'core.js'), '/* 3-core */')
    await writeFile(join(scriptsDir, 'comments.js'), '/* 4-comments */')
    await writeFile(join(scriptsDir, 'benchmark.js'), '/* 5-benchmark */')

    const outputPath = join(tmpDir, 'output.html')
    await assembleHtml(tmpDir, MINIMAL_VIEWER_DATA, outputPath)

    const html = await readFile(outputPath, 'utf-8')
    const idx1 = html.indexOf('1-markdown')
    const idx2 = html.indexOf('2-parser')
    const idx3 = html.indexOf('3-core')
    const idx4 = html.indexOf('4-comments')
    const idx5 = html.indexOf('5-benchmark')
    const idxData = html.indexOf('__VIEWER_DATA__')

    // Data injected before scripts
    expect(idxData).toBeLessThan(idx1)
    // Scripts in order
    expect(idx1).toBeLessThan(idx2)
    expect(idx2).toBeLessThan(idx3)
    expect(idx3).toBeLessThan(idx4)
    expect(idx4).toBeLessThan(idx5)
  })
})
```

- [ ] **Step 3: Run test to verify it fails**

Run: `bun test packages/matrixng/test/assemble.test.ts`
Expected: FAIL — module not found

- [ ] **Step 4: Implement assemble.ts**

```typescript
import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import type { ViewerData } from './types'

/** Ordered list of JS files to inline. Order matters — dependencies first. */
const JS_LOAD_ORDER = [
  'markdown.js',
  'matrix-parser.js',
  'core.js',
  'comments.js',
  'benchmark.js',
]

/**
 * Assemble a standalone HTML file from template parts and viewer data.
 *
 * @param skillPath - Path to the skill directory (contains assets/ and scripts/)
 * @param data - The ViewerData JSON to inject
 * @param outputPath - Where to write the final HTML
 */
export async function assembleHtml(
  skillPath: string,
  data: ViewerData,
  outputPath: string
): Promise<void> {
  // Read template parts
  const shell = await readFile(join(skillPath, 'assets', 'viewer', 'shell.html'), 'utf-8')
  const styles = await readFile(join(skillPath, 'assets', 'viewer', 'styles.css'), 'utf-8')

  // Read JS files in order
  const scriptsDir = join(skillPath, 'scripts', 'viewer')
  const jsContents: string[] = []
  for (const filename of JS_LOAD_ORDER) {
    const content = await readFile(join(scriptsDir, filename), 'utf-8')
    jsContents.push(`/* === ${filename} === */\n${content}`)
  }

  // Build the injected script block
  const dataScript = `<script>\nwindow.__VIEWER_DATA__ = ${JSON.stringify(data, null, 2)};\n</script>`
  const appScripts = jsContents.map((js) => `<script>\n${js}\n</script>`).join('\n')

  // Assemble
  let html = shell
  html = html.replace('<!--STYLES-->', `<style>\n${styles}\n</style>`)
  html = html.replace('<!--SCRIPTS-->', `${dataScript}\n${appScripts}`)

  // Write output
  await mkdir(dirname(outputPath), { recursive: true })
  await writeFile(outputPath, html, 'utf-8')
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `bun test packages/matrixng/test/assemble.test.ts`
Expected: Both tests pass

- [ ] **Step 6: Commit**

```bash
git add packages/matrixng/src/parse-engines.ts packages/matrixng/src/assemble.ts packages/matrixng/test/assemble.test.ts
git commit -m "feat(matrixng): add engine parser stub and HTML assembler"
```

---

## Task 5: CLI Build Command

**Files:**

- Create: `packages/matrixng/src/bin.ts`
- Create: `packages/matrixng/src/build.ts`

- [ ] **Step 1: Implement build.ts orchestrator**

```typescript
import { resolve, basename, dirname, join } from 'node:path'
import { readdir, stat } from 'node:fs/promises'
import { execFile } from 'node:child_process'
import { parseWorkspace } from './parse-workspace'
import { parseEngineReferences } from './parse-engines'
import { assembleHtml } from './assemble'
import type { ViewerData } from './types'

export interface BuildOptions {
  workspace: string
  skillPath?: string
  output?: string
  iteration?: number
  open?: boolean
}

/**
 * Build the viewer HTML from workspace data.
 */
export async function build(options: BuildOptions): Promise<string> {
  const workspace = resolve(options.workspace)
  const skillPath = options.skillPath
    ? resolve(options.skillPath)
    : await autoDetectSkillPath(workspace)

  // Resolve iteration once — used for both parsing and ViewerData
  const iteration = options.iteration ?? await detectLatestIteration(workspace)

  // Parse workspace with resolved iteration
  const { evals, benchmark } = await parseWorkspace(workspace, iteration)

  // Parse engine references (stub in Pass 1)
  const engineOperators = await parseEngineReferences(skillPath)

  // Detect skill name from workspace dir name
  const skillName = detectSkillName(workspace)

  // Assemble ViewerData
  const data: ViewerData = {
    skillName,
    iteration,
    generatedAt: new Date().toISOString(),
    evals,
    benchmark,
    engineOperators,
  }

  // Determine output path
  const outputPath = options.output ?? `/tmp/matrix-review-${skillName}.html`

  // Assemble and write HTML
  await assembleHtml(skillPath, data, outputPath)

  // Open in browser (safe — no shell injection)
  if (options.open !== false) {
    const cmd = process.platform === 'darwin' ? 'open' : 'xdg-open'
    execFile(cmd, [outputPath])
  }

  return outputPath
}

/**
 * Auto-detect the skill path from workspace location.
 * 1. Check sibling directories for SKILL.md — match by workspace name prefix
 * 2. Check content/skills/ relative to git repo root — match by name
 * 3. If neither resolves, throw with guidance
 */
async function autoDetectSkillPath(workspace: string): Promise<string> {
  const parent = dirname(workspace)
  const wsName = basename(workspace).replace(/-workspace$/, '')

  // Strategy 1: sibling directory matching workspace name prefix
  const siblings = await readdir(parent, { withFileTypes: true })
  for (const entry of siblings) {
    if (!entry.isDirectory()) continue
    if (entry.name === basename(workspace)) continue
    // Prefer name match (e.g., "search-term-matrices" matches "search-term-matrices-workspace")
    if (entry.name !== wsName) continue
    const skillMd = join(parent, entry.name, 'SKILL.md')
    try {
      await stat(skillMd)
      return join(parent, entry.name)
    } catch {
      continue
    }
  }

  // Strategy 2: walk up to git root, match by name in content/skills/
  let dir = parent
  for (let i = 0; i < 10; i++) {
    try {
      await stat(join(dir, '.git'))
      const skillDir = join(dir, 'content', 'skills', wsName)
      const skillMd = join(skillDir, 'SKILL.md')
      try {
        await stat(skillMd)
        return skillDir
      } catch {
        break // Git root found but skill not there
      }
    } catch {
      dir = dirname(dir)
    }
  }

  throw new Error(
    `Could not auto-detect skill path for "${wsName}". Use --skill-path to specify it explicitly.`
  )
}

async function detectLatestIteration(workspace: string): Promise<number> {
  const entries = await readdir(workspace)
  const nums = entries
    .filter((e) => e.match(/^iteration-\d+$/))
    .map((e) => parseInt(e.split('-')[1]))
    .sort((a, b) => b - a)
  return nums[0] ?? 1
}

function detectSkillName(workspace: string): string {
  const name = basename(workspace)
  // Strip -workspace suffix if present
  return name.replace(/-workspace$/, '')
}
```

- [ ] **Step 2: Implement bin.ts CLI entry**

```typescript
#!/usr/bin/env bun
import { defineCommand, runMain } from 'citty'
import { build } from './build'

const buildCommand = defineCommand({
  meta: { name: 'build', description: 'Build the matrix review viewer HTML' },
  args: {
    workspace: {
      type: 'positional',
      description: 'Path to the workspace directory',
      required: true,
    },
    'skill-path': {
      type: 'string',
      description: 'Path to the skill directory (auto-detected if omitted)',
    },
    output: {
      type: 'string',
      alias: 'o',
      description: 'Output HTML file path',
    },
    iteration: {
      type: 'string',
      alias: 'i',
      description: 'Iteration number (default: latest)',
    },
    open: {
      type: 'boolean',
      description: 'Open in browser after build',
      default: true,
    },
  },
  async run({ args }) {
    try {
      const outputPath = await build({
        workspace: args.workspace as string,
        skillPath: args['skill-path'] as string | undefined,
        output: args.output as string | undefined,
        iteration: args.iteration ? parseInt(args.iteration as string) : undefined,
        open: args.open as boolean,
      })
      console.log(`Viewer built: ${outputPath}`)
    } catch (err) {
      console.error(`Error: ${(err as Error).message}`)
      process.exit(1)
    }
  },
})

const main = defineCommand({
  meta: { name: 'matrixng', version: '0.1.0', description: 'Search matrix review viewer' },
  subCommands: {
    build: () => Promise.resolve(buildCommand),
  },
})

runMain(main)
```

- [ ] **Step 3: Verify CLI runs (will fail on missing templates — that's expected)**

Run: `bun run packages/matrixng/src/bin.ts build --help`
Expected: Shows usage with workspace positional arg and all flags

- [ ] **Step 4: Commit**

```bash
git add packages/matrixng/src/bin.ts packages/matrixng/src/build.ts
git commit -m "feat(matrixng): add CLI build command"
```

---

## Task 6: Viewer Shell + Styles

**Files:**

- Create: `content/skills/search-term-matrices/assets/viewer/shell.html`
- Create: `content/skills/search-term-matrices/assets/viewer/styles.css`

- [ ] **Step 1: Create shell.html**

This is the outer frame. JS/CSS are injected at the `<!--STYLES-->` and `<!--SCRIPTS-->` markers.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Matrix Review</title>
  <!--STYLES-->
</head>
<body>
  <header id="header">
    <h1 id="skill-name"></h1>
    <span id="meta-info"></span>
  </header>

  <nav id="tab-bar">
    <button class="tab active" data-tab="outputs">Outputs</button>
    <button class="tab" data-tab="benchmark">Benchmark</button>
  </nav>

  <div id="tab-content">
    <!-- Outputs tab -->
    <div id="outputs-tab" class="tab-panel active">
      <nav id="subtab-bar"></nav>
      <div id="mode-bar">
        <button id="mode-rendered" class="mode-btn active">Rendered</button>
        <button id="mode-edit" class="mode-btn">Edit</button>
      </div>
      <div id="outputs-container">
        <aside id="comment-sidebar" class="collapsed">
          <div id="sidebar-header">
            <h3>Comments (<span id="comment-count">0</span>)</h3>
            <button id="sidebar-toggle" title="Toggle sidebar">&#9776;</button>
          </div>
          <div id="comment-list"></div>
        </aside>
        <main id="matrix-content"></main>
      </div>
    </div>

    <!-- Benchmark tab -->
    <div id="benchmark-tab" class="tab-panel">
      <nav id="bench-subtab-bar">
        <button class="bench-subtab active" data-subtab="metrics">Metrics</button>
        <button class="bench-subtab" data-subtab="criteria">Criteria Detail</button>
      </nav>
      <div id="bench-content">
        <div id="metrics-panel" class="bench-panel active"></div>
        <div id="criteria-panel" class="bench-panel"></div>
      </div>
    </div>
  </div>

  <footer id="footer">
    <button id="export-comments">Export Comments</button>
    <div id="nav-buttons">
      <button id="prev-subtab" title="Previous (←)">&#8592; Prev</button>
      <button id="next-subtab" title="Next (→)">Next &#8594;</button>
    </div>
  </footer>

  <!-- Comment popover (hidden by default) -->
  <div id="comment-popover" class="hidden">
    <div id="popover-anchor-label"></div>
    <textarea id="popover-textarea" placeholder="Add a comment..."></textarea>
    <div id="popover-actions">
      <button id="popover-cancel">Cancel</button>
      <button id="popover-save">Save</button>
    </div>
  </div>

  <!--SCRIPTS-->
</body>
</html>
```

- [ ] **Step 2: Create styles.css**

Copy from companion code: `docs/superpowers/plans/matrixng-pass1-viewer-code/styles.css`
→ `content/skills/search-term-matrices/assets/viewer/styles.css`

This file defines all layout, tabs, table formatting, comment sidebar/popover, edit mode, and benchmark styles using CSS custom properties for theming. ~280 lines.

- [ ] **Step 3: Commit**

```bash
git add content/skills/search-term-matrices/assets/viewer/shell.html content/skills/search-term-matrices/assets/viewer/styles.css
git commit -m "feat(matrixng): add viewer shell HTML and styles"
```

---

## Task 7: Viewer JS — markdown.js

**Files:**

- Create: `content/skills/search-term-matrices/scripts/viewer/markdown.js`

The markdown renderer. Converts matrix markdown into HTML with semantic `data-*` attributes on table cells. No external dependencies.

- [ ] **Step 1: Implement markdown.js**

```javascript
/**
 * Markdown → HTML renderer.
 * Supports: tables (with data-* annotations), headings, bold, italic,
 * code blocks, inline code, lists, blockquotes, paragraphs.
 *
 * Tables get special treatment: each cell is annotated with data-anchor
 * attributes for the comment system.
 */
;(function () {
  'use strict'

  const MV = (window.MatrixViewer = window.MatrixViewer || {})

  /**
   * Render markdown string to HTML.
   * @param {string} md - Raw markdown
   * @param {object} [anchorContext] - { evalId, configuration } for table annotation
   * @returns {string} HTML
   */
  MV.renderMarkdown = function (md, anchorContext) {
    if (!md) return ''
    const lines = md.split('\n')
    const result = []
    let i = 0
    let currentSection = null
    let currentTierLevel = 0

    while (i < lines.length) {
      const line = lines[i]

      // Headings
      const headingMatch = line.match(/^(#{1,6})\s+(.+)/)
      if (headingMatch) {
        const level = headingMatch[1].length
        const text = processInline(headingMatch[2])
        const sectionId = detectSection(headingMatch[2])
        if (sectionId) currentSection = sectionId
        if (sectionId && sectionId.startsWith('tier')) {
          currentTierLevel = parseInt(sectionId.replace('tier', ''))
        }
        const attrs = sectionId ? ` data-section="${sectionId}"` : ''
        result.push(`<h${level}${attrs}>${text}</h${level}>`)
        i++
        continue
      }

      // Code blocks
      if (line.startsWith('```')) {
        const lang = line.slice(3).trim()
        const codeLines = []
        i++
        while (i < lines.length && !lines[i].startsWith('```')) {
          codeLines.push(escapeHtml(lines[i]))
          i++
        }
        i++ // skip closing ```
        result.push(`<pre><code class="language-${lang || 'text'}">${codeLines.join('\n')}</code></pre>`)
        continue
      }

      // Tables
      if (line.includes('|') && i + 1 < lines.length && lines[i + 1].match(/^\|?[\s-:|]+\|?$/)) {
        const tableHtml = renderTable(lines, i, anchorContext, currentSection, currentTierLevel)
        result.push(tableHtml.html)
        i = tableHtml.endIndex
        continue
      }

      // Blockquotes
      if (line.startsWith('>')) {
        const quoteLines = []
        while (i < lines.length && lines[i].startsWith('>')) {
          quoteLines.push(processInline(lines[i].replace(/^>\s?/, '')))
          i++
        }
        result.push(`<blockquote>${quoteLines.join('<br>')}</blockquote>`)
        continue
      }

      // Lists
      if (line.match(/^[\s]*[-*+]\s/) || line.match(/^[\s]*\d+\.\s/)) {
        const listResult = renderList(lines, i)
        result.push(listResult.html)
        i = listResult.endIndex
        continue
      }

      // Blank line
      if (line.trim() === '') {
        i++
        continue
      }

      // Paragraph
      const paraLines = []
      while (i < lines.length && lines[i].trim() !== '' && !lines[i].startsWith('#') && !lines[i].startsWith('```') && !lines[i].startsWith('>') && !lines[i].includes('|')) {
        paraLines.push(processInline(lines[i]))
        i++
      }
      if (paraLines.length > 0) {
        result.push(`<p>${paraLines.join(' ')}</p>`)
      }
    }

    return result.join('\n')
  }

  // --- Table rendering with data-anchor attributes ---

  function renderTable(lines, startIndex, ctx, section, tierLevel) {
    const headerLine = lines[startIndex]
    const headers = splitRow(headerLine)

    // Map header names to column keys for anchoring
    const colKeys = headers.map(function (h) {
      const lower = h.toLowerCase().replace(/[^a-z]/g, '')
      if (lower === 'engines' || lower === 'engine' || lower === 'engines') return 'engines'
      if (lower === 'query') return 'query'
      if (lower === 'operators') return 'operators'
      if (lower === 'expectedresults') return 'expected'
      if (lower === 'acceptance' || lower === 'acceptancecriteria') return 'acceptance'
      if (lower === 'success' || lower === 'successcriteria') return 'success'
      return lower
    })

    let i = startIndex + 2 // skip header + separator
    const rows = []
    let rowNum = 0

    while (i < lines.length && lines[i].includes('|') && !lines[i].match(/^\|?[\s-:|]+\|?$/)) {
      rowNum++
      const cells = splitRow(lines[i])
      rows.push({ num: rowNum, cells: cells })
      i++
    }

    // Build HTML
    let html = '<table>'
    html += '<thead><tr>'
    for (const h of headers) {
      html += `<th>${processInline(h)}</th>`
    }
    html += '</tr></thead>'
    html += '<tbody>'

    for (const row of rows) {
      html += '<tr>'
      for (let c = 0; c < headers.length; c++) {
        const cellText = row.cells[c] || ''
        let attrs = ''
        if (ctx && section) {
          attrs = ` data-eval="${ctx.evalId}" data-config="${ctx.configuration}" data-section="${section}" data-row="${row.num}" data-col="${colKeys[c] || ''}"`
        }
        html += `<td${attrs}>${processInline(cellText)}</td>`
      }
      html += '</tr>'
    }

    html += '</tbody></table>'
    return { html: html, endIndex: i }
  }

  function renderList(lines, startIndex) {
    const isOrdered = !!lines[startIndex].match(/^[\s]*\d+\.\s/)
    const tag = isOrdered ? 'ol' : 'ul'
    const items = []
    let i = startIndex

    while (i < lines.length) {
      const match = lines[i].match(isOrdered ? /^[\s]*\d+\.\s(.+)/ : /^[\s]*[-*+]\s(.+)/)
      if (!match) break
      items.push(`<li>${processInline(match[1])}</li>`)
      i++
    }

    return { html: `<${tag}>${items.join('')}</${tag}>`, endIndex: i }
  }

  function detectSection(heading) {
    const lower = heading.toLowerCase()
    if (lower.includes('context')) return 'context'
    if (lower.includes('tier 1') || lower.includes('tier1')) return 'tier1'
    if (lower.includes('tier 2') || lower.includes('tier2')) return 'tier2'
    if (lower.includes('tier 3') || lower.includes('tier3')) return 'tier3'
    if (lower.includes('runtime recovery') || lower.includes('recovery')) return 'recovery'
    if (lower.includes('grading')) return 'grading'
    if (lower.includes('decomposition')) return 'decomposition'
    return null
  }

  function splitRow(line) {
    var trimmed = line.trim()
    if (trimmed.charAt(0) === '|') trimmed = trimmed.slice(1)
    if (trimmed.charAt(trimmed.length - 1) === '|') trimmed = trimmed.slice(0, -1)
    return trimmed.split('|').map(function (c) { return c.trim() })
  }

  function processInline(text) {
    if (!text) return ''
    text = escapeHtml(text)
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>')
    text = text.replace(/`(.+?)`/g, '<code>$1</code>')
    text = text.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
    return text
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }
})()
```

- [ ] **Step 2: Commit**

```bash
git add content/skills/search-term-matrices/scripts/viewer/markdown.js
git commit -m "feat(matrixng): add markdown renderer with table annotation"
```

---

## Task 8: Viewer JS — matrix-parser.js

**Files:**

- Create: `content/skills/search-term-matrices/scripts/viewer/matrix-parser.js`

Parses raw matrix markdown into the `ParsedMatrix` structure client-side. Used by overlay views in Pass 2.

- [ ] **Step 1: Implement matrix-parser.js**

Copy from companion code: `docs/superpowers/plans/matrixng-pass1-viewer-code/matrix-parser.js`
→ `content/skills/search-term-matrices/scripts/viewer/matrix-parser.js`

Key functions (~180 lines):

- `MV.parseMatrix(raw)` → returns a `ParsedMatrix` object
- `MV.parseAllMatrices(raw)` → splits multi-matrix documents (decomposed outputs) and returns array
- `MV.detectSection(heading)` → exposed on namespace so markdown.js and overlay modules can reuse it (avoids duplicated logic)
- Internal: `parseContextBlock`, `parseBulletList`, `parseTierTable`

- [ ] **Step 2: Commit**

```bash
git add content/skills/search-term-matrices/scripts/viewer/matrix-parser.js
git commit -m "feat(matrixng): add client-side matrix parser"
```

---

## Task 9: Viewer JS — core.js

**Files:**

- Create: `content/skills/search-term-matrices/scripts/viewer/core.js`

The main application controller. Initializes the viewer, manages tab/subtab state, renders matrix content, and handles keyboard navigation.

- [ ] **Step 1: Implement core.js**

Copy from companion code: `docs/superpowers/plans/matrixng-pass1-viewer-code/core.js`
→ `content/skills/search-term-matrices/scripts/viewer/core.js`

Key functions (~180 lines):

- `MV.init()` — boots on DOMContentLoaded, reads `window.__VIEWER_DATA__`, populates header, builds subtabs, wires events, initializes comments + benchmark
- `MV.switchTab(tabName)` / `MV.switchSubtab(index)` / `MV.navSubtab(delta)` — navigation
- Internal: `renderCurrentEval()` renders with_skill markdown + collapsible baseline, `renderEditMode()` shows raw markdown in `<pre>` with line numbers
- `MV.getState()` — exposes state for other modules
- Keyboard: `←/→` subtab, `1/2` tab, `e` toggle, `c` sidebar, `Esc` popover. Skipped when input/textarea focused.

- [ ] **Step 2: Commit**

```bash
git add content/skills/search-term-matrices/scripts/viewer/core.js
git commit -m "feat(matrixng): add viewer core controller"
```

---

## Task 10: Viewer JS — comments.js

**Files:**

- Create: `content/skills/search-term-matrices/scripts/viewer/comments.js`

The semantic comment system — add, edit, resolve, delete comments anchored to matrix cells, with localStorage persistence and JSON export.

- [ ] **Step 1: Implement comments.js**

Copy from companion code: `docs/superpowers/plans/matrixng-pass1-viewer-code/comments.js`
→ `content/skills/search-term-matrices/scripts/viewer/comments.js`

Key functions (~220 lines):

- `MV.initComments()` — loads from localStorage, sets up storage key
- `MV.attachCellHandlers()` — called after each render, adds click handlers to `td[data-col]` cells. Click near the `+` icon area or double-click opens popover.
- `MV.saveComment(anchor, text)` / `MV.resolveComment(id)` / `MV.deleteComment(id)` — CRUD
- `MV.renderSidebar(evalId)` — renders comments ordered by document position, click scrolls to cell
- `MV.exportComments()` — builds `CommentFile` JSON, triggers browser file download
- Internal: `anchorFromCell(td)` reads `data-*` attrs, `buildAnchorLabel(anchor)` → "Eval 1 → Tier 1, Row 3 → Operators", `scrollToAnchor` with highlight flash
- localStorage key: `matrixng-comments-<skillName>-<iteration>`

- [ ] **Step 2: Commit**

```bash
git add content/skills/search-term-matrices/scripts/viewer/comments.js
git commit -m "feat(matrixng): add semantic comment system"
```

---

## Task 11: Viewer JS — benchmark.js

**Files:**

- Create: `content/skills/search-term-matrices/scripts/viewer/benchmark.js`

Renders the Benchmark tab: metrics table and criteria detail view.

- [ ] **Step 1: Implement benchmark.js**

Copy from companion code: `docs/superpowers/plans/matrixng-pass1-viewer-code/benchmark.js`
→ `content/skills/search-term-matrices/scripts/viewer/benchmark.js`

Key functions (~170 lines):

- `MV.renderBenchmark()` — called by core.js, renders both subtab panels
- Internal `renderMetricsTable(container, data)` — builds an HTML table from `benchmark.configurations`:
  - Rows: one per eval + aggregate row per config + delta row
  - Color-coded pass rates: green ≥ 80%, yellow ≥ 50%, red < 50%
  - Analysis observations as a list below the table
- Internal `renderCriteriaDetail(container, data)` — for each eval, lists all assertions with:
  - Pass/fail badge (green checkmark / red X)
  - Assertion text
  - Evidence text (collapsed, click to expand)
  - Grouped by eval name with headers
  - Filter buttons at top: `[All] [Structural] [Quality] [Behavioral]`
- Subtab switching between metrics and criteria views

~200 lines.

- [ ] **Step 2: Commit**

```bash
git add content/skills/search-term-matrices/scripts/viewer/benchmark.js
git commit -m "feat(matrixng): add benchmark rendering"
```

---

## Task 12: Integration Test

**Files:**

- Create: `packages/matrixng/test/build.integration.test.ts`

End-to-end test: runs the full build pipeline against the real workspace data and verifies the output HTML.

- [ ] **Step 1: Write the integration test**

```typescript
import { describe, expect, test } from 'bun:test'
import { resolve } from 'node:path'
import { readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { build } from '../src/build'

const WORKTREE = resolve(import.meta.dir, '../../..')
const WORKSPACE = resolve(WORKTREE, 'content/skills/search-term-matrices-workspace')
const SKILL_PATH = resolve(WORKTREE, 'content/skills/search-term-matrices')

describe('build integration', () => {
  const outputPath = join(tmpdir(), 'matrixng-integration-test.html')

  test('builds a complete HTML file from real workspace data', async () => {
    await build({
      workspace: WORKSPACE,
      skillPath: SKILL_PATH,
      output: outputPath,
      iteration: 1,
      open: false,
    })

    const html = await readFile(outputPath, 'utf-8')

    // Basic structure
    expect(html).toContain('<!DOCTYPE html>')
    expect(html).toContain('window.__VIEWER_DATA__')

    // Data was injected
    expect(html).toContain('search-term-matrices')
    expect(html).toContain('offline-sync')
    expect(html).toContain('llm-regulatory')
    expect(html).toContain('webtransport')

    // All JS modules present
    expect(html).toContain('MatrixViewer')
    expect(html).toContain('renderMarkdown')
    expect(html).toContain('initComments')
    expect(html).toContain('renderBenchmark')

    // CSS present
    expect(html).toContain('<style>')

    // Benchmark data
    expect(html).toContain('pass_rate')
    expect(html).toContain('with_skill')
    expect(html).toContain('without_skill')

    // Clean up
    await rm(outputPath, { force: true })
  })

  test('auto-detects skill path from workspace sibling', async () => {
    const out = join(tmpdir(), 'matrixng-autodetect-test.html')
    await build({
      workspace: WORKSPACE,
      output: out,
      iteration: 1,
      open: false,
    })

    const html = await readFile(out, 'utf-8')
    expect(html).toContain('window.__VIEWER_DATA__')
    await rm(out, { force: true })
  })
})
```

- [ ] **Step 2: Run all tests**

Run: `bun test packages/matrixng/`
Expected: All tests pass (parse-markdown-table, parse-workspace, assemble, integration)

- [ ] **Step 3: Manual verification — build and open viewer**

Run:

```bash
bun run packages/matrixng/src/bin.ts build \
  content/skills/search-term-matrices-workspace \
  --skill-path content/skills/search-term-matrices \
  --iteration 1
```

Expected: Browser opens with the viewer showing 3 eval subtabs, rendered matrices, benchmark metrics, and working comment system.

- [ ] **Step 4: Commit**

```bash
git add packages/matrixng/test/build.integration.test.ts
git commit -m "test(matrixng): add integration test with real workspace data"
```

---

## Task 13: Final Wiring + Justfile

**Files:**

- Modify: `justfile`

- [ ] **Step 1: Add matrixng recipe to justfile**

Add after the existing `agents` recipe:

```justfile
# Matrix review viewer
[group('tools')]
matrixng *args:
    @bun run packages/matrixng/src/bin.ts {{ args }}
```

- [ ] **Step 2: Verify `_init-bun` was updated in Task 1**

The `_init-bun` recipe should already be running root-level `bun install` (done in Task 1, Step 5). Verify with `just _init-bun` or `grep 'bun install' justfile`.

```justfile
# Already done in Task 1 — just verify:
[private]
_init-bun:
    @echo "Installing TypeScript dependencies..."
    @bun install --silent
```

- [ ] **Step 3: Run full test suite**

Run: `bun test packages/matrixng/`
Expected: All tests pass

- [ ] **Step 4: Run the viewer end-to-end**

Run: `just matrixng build content/skills/search-term-matrices-workspace --iteration 1`
Expected: Opens viewer in browser

- [ ] **Step 5: Final commit**

```bash
git add justfile
git commit -m "feat(matrixng): add justfile recipe and finalize Pass 1"
```
