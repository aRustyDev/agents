---
id: 1105f062-33cf-4eff-a759-f17fb55296c3
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 1: Core Library"
status: pending
related:
  depends-on: [149d764d-4f87-4786-b204-168aea26d19c]
---

# Phase 1: Core Library

**ID:** `phase-1`
**Dependencies:** phase-0
**Status:** pending
**Effort:** Medium

## Objective

Migrate the zero-dependency library modules that form the foundation for all commands: hashing, symlink checks, output formatting, and markdown chunking.

## Success Criteria

- [ ] `lib/hash.ts` produces identical SHA256 output to Python's `plugin-hash.py` for the same inputs
- [ ] `lib/symlink.ts` correctly identifies healthy, broken, and chained symlinks
- [ ] `lib/output.ts` produces valid JSON in `--json` mode and colored text in human mode
- [ ] `lib/chunker.ts` produces identical chunk output to Python's `lib/chunker.py` for the same markdown files
- [ ] All modules have `bun:test` test suites passing

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Hash module | `.scripts/lib/hash.ts` | TypeScript |
| Symlink module | `.scripts/lib/symlink.ts` | TypeScript |
| Output formatter | `.scripts/lib/output.ts` | TypeScript |
| Chunker module | `.scripts/lib/chunker.ts` | TypeScript |
| Test suites | `.scripts/test/{hash,symlink,output,chunker}.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/lib/hash.ts`
- `.scripts/lib/symlink.ts`
- `.scripts/lib/output.ts`
- `.scripts/lib/chunker.ts`
- `.scripts/test/hash.test.ts`
- `.scripts/test/symlink.test.ts`
- `.scripts/test/output.test.ts`
- `.scripts/test/chunker.test.ts`

**Modify:**
- None

## Tasks

### lib/hash.ts
- [ ] Implement `hashFile()` using `Bun.CryptoHasher` or `crypto.createHash`
- [ ] Implement `hashDirectory()` — sorted rglob, `path + \0 + content + \0` concatenation
- [ ] Implement `computeHash()` — auto-detect file vs directory
- [ ] Implement `formatHash()` / `parseHash()` — `sha256:` prefix handling
- [ ] Implement `verifyHash()`
- [ ] Write parity tests: hash same files/dirs with Python and TS, assert identical output

### lib/symlink.ts
- [ ] Implement `checkSymlink()` — uses `fs.lstat` + `fs.readlink`
- [ ] Implement `createSymlink()` — with parent directory creation
- [ ] Implement `resolveChain()` — follow symlink chains to final target
- [ ] Implement `auditSymlinks()` — recursive directory scan for all symlinks
- [ ] Write tests with temp directories containing healthy/broken/chained symlinks

### lib/output.ts
- [ ] Implement `createOutput({ json, quiet })` factory
- [ ] Implement human mode: `ansis` colored `[ok]`/`[error]`/`[warn]`/`[info]` prefixes
- [ ] Implement JSON mode: structured `{"status","message","data"}` objects to stdout/stderr
- [ ] Implement `table()` — `console-table-printer` in human mode, `JSON.stringify` in JSON mode
- [ ] Implement `tree()` — ASCII box-drawing in human mode, nested JSON in JSON mode
- [ ] Implement `ndjson()` — one JSON object per line (streaming)
- [ ] Implement `spinner()` — `nanospinner` wrapper (suppressed in JSON/quiet mode)
- [ ] Implement `progress()` — `@opentf/cli-pbar` wrapper (suppressed in JSON/quiet mode)
- [ ] Write tests: snapshot human output, parse JSON output

### lib/chunker.ts
- [ ] Implement `parseFrontmatter()` — YAML frontmatter extraction (`---` delimited)
- [ ] Implement `splitIntoSections()` — split by `## ` headings with line numbers
- [ ] Implement `splitIntoParagraphs()` — split by `\n\n+`, skip code blocks, respect minLength
- [ ] Implement `chunkMarkdown()` — 3-level hierarchy (file → section → paragraph)
- [ ] Implement `chunkFile()` — read file + chunkMarkdown
- [ ] Write parity tests: chunk same SKILL.md files with Python and TS, diff JSON output

## Notes

- Hash parity is critical — the plugin build system depends on deterministic hashes matching across runs
- The output module is new (Python used `rich` ad-hoc); no parity testing needed, just correctness
- Chunker frontmatter parsing: start with a ~30-line parser for simple key-value YAML; add `js-yaml` only if complex nested structures are needed
- Symlink module is entirely new — test against known state in `context/skills/` directory
