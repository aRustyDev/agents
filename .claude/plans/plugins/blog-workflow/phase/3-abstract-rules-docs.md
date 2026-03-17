---
id: 1eac04fd-7c9d-4646-8fd4-71a0616500c3
project:
  id: 6233cf65-b369-4afe-8fd9-b934b1dc8716
title: "Phase 3: Abstract Rules & Documentation"
status: draft
related:
  depends-on: [09b45d7f-1ac5-4be3-8748-20da81378c2e]
---

# Phase 3: Abstract Rules & Documentation

**ID:** `phase-3`
**Dependencies:** phase-1
**Status:** pending
**Effort:** 3-4 hours

## Objective

Make rules and documentation platform-agnostic by replacing Astro-specific content with generic references and adding platform skill cross-references.

## Success Criteria

- [ ] `rules/blog-frontmatter.md` uses generic field names with a "Platform Mapping" section
- [ ] `docs/src/workflow/publishing.md` uses generic paths/commands
- [ ] `docs/src/platforms/index.md` exists with platform support overview and extension guide
- [ ] All Astro-specific content in rules/docs is replaced or moved to platform skill references

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Generic frontmatter rule | `rules/blog-frontmatter.md` | Rule file |
| Generic publishing docs | `docs/src/workflow/publishing.md` | Documentation |
| Generic frontmatter docs | `docs/src/reference/frontmatter.md` | Documentation |
| Platform support overview | `docs/src/platforms/index.md` | Documentation |

## Tasks

- [ ] Update `rules/blog-frontmatter.md`: Replace AstroPaper field names with plugin-generic names; add "Platform Mapping" section referencing platform skill
- [ ] Update `docs/src/reference/frontmatter.md`: Document plugin's generic schema; add "Platform-Specific" section with links to platform skills
- [ ] Update `docs/src/workflow/publishing.md`: Replace `src/data/blog/` and `astro build` with generic references; add "Platform Requirements" section
- [ ] Create `docs/src/platforms/index.md`: Overview of platform support, how to add new platforms, platform detection logic

## Files

**Create:**

- `context/plugins/blog-workflow/docs/src/platforms/index.md`

**Modify:**

- `context/plugins/blog-workflow/rules/blog-frontmatter.md`
- `context/plugins/blog-workflow/docs/src/workflow/publishing.md`
- `context/plugins/blog-workflow/docs/src/reference/frontmatter.md`
