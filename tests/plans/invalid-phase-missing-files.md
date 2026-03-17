# Phase 1: Example Invalid Phase

**ID:** `phase-1`
**Dependencies:** None
**Status:** pending

This phase document is **invalid** because it lacks the required `## Files` section.

**Expected Warning:** `Phase file missing Files section`

## Objective

Demonstrate what happens when a phase is missing required sections.

## Success Criteria

- [ ] Validation catches the missing section
- [ ] Clear error message provided

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Example output | `examples/output.md` | Markdown |

## Tasks

- [ ] Create the example
- [ ] Document the error

## Notes

This phase is missing the `## Files` section.

To fix, add:

```markdown
## Files

**Create:**
- `<path/to/new/file>`

**Modify:**
- `<path/to/existing/file>`
```

Or if no file operations:

```markdown
## Files

**Create:**
- None

**Modify:**
- None
```
