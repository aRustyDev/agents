---
id: eaf5ca62-ce98-4450-8a61-1c138d069804
project:
  id: 6233cf65-b369-4afe-8fd9-b934b1dc8716
title: "Phase 5: Validation & Testing"
status: draft
related:
  depends-on: [8dc50661-f068-4c5a-8463-d4353927e752]
---

# Phase 5: Validation & Testing

**ID:** `phase-5`
**Dependencies:** phase-4
**Status:** pending
**Effort:** 3-4 hours

## Objective

Validate that the refactoring preserves all existing workflows and document the migration path for current users.

## Success Criteria

- [ ] Fresh init with Astro detection produces correct `.blog-workflow.yaml`
- [ ] Full workflow (idea → draft → edit → publish) works end-to-end with platform skill
- [ ] Frontmatter validation uses platform-specific field names from skill
- [ ] Build validation uses platform-specific commands from skill
- [ ] Progressive disclosure verified: SKILL.md loads by default, reference files on demand
- [ ] Migration guide documents what changed and how to verify setup

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Test scenarios document | `docs/src/platforms/testing.md` | Documentation |
| Migration guide | `docs/src/platforms/migration.md` | Documentation |
| Updated CHANGELOG | `CHANGELOG.md` | Changelog entry |

## Tasks

- [ ] Create test scenarios covering:
  - Fresh init with Astro detection
  - Full workflow: idea → draft → review → edit → publish
  - Frontmatter validation against platform schema
  - Build validation with platform commands
  - No-platform-detected error path
- [ ] Test progressive disclosure:
  - Verify SKILL.md loads with `/blog/init`
  - Verify reference files load only when deeper context needed
  - Measure token budget impact
- [ ] Write migration guide:
  - What changed for existing Astro users (minimal: run `/blog/init` to create config)
  - How to verify setup is correct
  - Troubleshooting common issues
- [ ] Update CHANGELOG.md with platform extensibility changes

## Files

**Create:**

- `content/plugins/blog-workflow/docs/src/platforms/testing.md`
- `content/plugins/blog-workflow/docs/src/platforms/migration.md`

**Modify:**

- `content/plugins/blog-workflow/CHANGELOG.md`
