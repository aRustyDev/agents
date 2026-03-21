# Phase 3d: Output Style Provider

**ID:** `phase-3d`
**Dependencies:** phase-1 (complete)
**Status:** planned

## Objective

Create a `LocalOutputStyleProvider` that discovers output style markdown files from `context/output-styles/`. This is the simplest provider — only 2 files exist currently, no frontmatter, description from content.

## Success Criteria

- [ ] Discovers `.md` files in `context/output-styles/`
- [ ] Excludes `TODO.md` and dot-prefixed files
- [ ] Description from first non-heading paragraph
- [ ] Name from filename (strip `.md`)
- [ ] All tests pass

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Output style provider | `.scripts/lib/component/provider-output-style.ts` | TypeScript |
| Tests | `.scripts/test/component/provider-output-style.test.ts` | bun:test |

## Files

**Create:**
- `.scripts/lib/component/provider-output-style.ts`
- `.scripts/test/component/provider-output-style.test.ts`

## On-Disk Structure

```
context/output-styles/
├── feedback-submission.md   → name: "feedback-submission"
└── TODO.md                  # skip
```

No frontmatter. Description = first paragraph after the H1 heading (or empty if none).

## Tasks

### Task 3d.1: Output Style Provider

Tests (6):
1. discovers output style files
2. excludes TODO.md
3. name from filename
4. description from first paragraph
5. search filters by query
6. returns empty for non-output_style type

Implementation: ~40 lines. Read dir, filter, parse each file for first paragraph.

## Acceptance Criteria

- [ ] Provider ID: `local-output-style`
- [ ] Capabilities: `search`, `list`, `info` for `output_style` only
- [ ] Read-only
- [ ] At least 6 test cases
