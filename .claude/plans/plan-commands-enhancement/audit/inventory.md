# Plan Inventory

**Audit Date:** 2025-03-16
**Total Plans:** 7 directories (excluding `.archive`)

## Summary

| Category | Count | Plans |
|----------|-------|-------|
| Compliant | 1 | plan-commands-enhancement |
| Near-compliant | 1 | merge-convert-skills |
| Partial | 1 | sqlite-vec |
| Legacy/Different | 4 | ai-arusty-dev, convert-skill-mcp, features, plugins |

## Detailed Inventory

### 1. plan-commands-enhancement

| Attribute | Value |
|-----------|-------|
| **Category** | Compliant |
| **Structure** | `PLAN.md` + `phase/*.md` |
| **Has Objectives Table** | Yes (with Measurable) |
| **Has Current State** | Yes (with Current/Target/Gap) |
| **Has Phases Table** | Yes (with ID/Dependencies) |
| **Has Risks** | Yes (with Mitigation) |
| **Phase Files Have** | Success Criteria, Deliverables, Files |
| **Migration Needed** | None |

### 2. merge-convert-skills

| Attribute | Value |
|-----------|-------|
| **Category** | Near-compliant |
| **Structure** | `index.md` + `phase/*.md` + `analysis/` + `data/` |
| **Has Objectives Table** | No (has "Goals" prose section) |
| **Has Current State** | Partial (has "Current Status" table but different columns) |
| **Has Phases Table** | Yes (has "Phase Overview" with Effort) |
| **Has Risks** | No |
| **Phase Files Have** | Varies - some have deliverables, none have Files section |
| **Migration Needed** | Rename to PLAN.md, add Objectives table, add Risks, update phases |

### 3. sqlite-vec

| Attribute | Value |
|-----------|-------|
| **Category** | Partial |
| **Structure** | Numbered task files (`00-overview.md` through `07-*.md`) |
| **Has Objectives Table** | No (has "Goal" prose) |
| **Has Current State** | No |
| **Has Phases Table** | No (has "Tasks" table with Blocked By) |
| **Has Risks** | No |
| **Phase Files Have** | Task-specific content, no standard structure |
| **Migration Needed** | Restructure to PLAN.md + phase/, or document as "task list" pattern |

### 4. ai-arusty-dev

| Attribute | Value |
|-----------|-------|
| **Category** | Legacy |
| **Structure** | Two files: `concept-schema.md` (empty), `prd.md` |
| **Has Objectives Table** | No |
| **Has Current State** | No |
| **Has Phases Table** | No |
| **Has Risks** | No |
| **Migration Needed** | Too minimal to migrate - appears to be early draft/notes |

### 5. convert-skill-mcp

| Attribute | Value |
|-----------|-------|
| **Category** | Legacy |
| **Structure** | Single file: `tree-sitter.md` |
| **Has Objectives Table** | No |
| **Has Current State** | No |
| **Has Phases Table** | No |
| **Has Risks** | No |
| **Migration Needed** | Too minimal - appears to be research notes |

### 6. features/

| Attribute | Value |
|-----------|-------|
| **Category** | Legacy (container) |
| **Structure** | Nested directories: `plugin-build-system/`, `plugin-feedback-infrastructure/` |
| **Contains** | Sub-plans with `index.md` + `phase/*.md` pattern |
| **Migration Needed** | Each sub-plan needs individual assessment |

### 7. plugins/

| Attribute | Value |
|-----------|-------|
| **Category** | Legacy (container) |
| **Structure** | Nested directories for each plugin plan |
| **Common Pattern** | `brainstorm.md`, `research.md`, `roadmap.md`, `REPORT.md` |
| **Contains** | 8 plugin plans (asciinema-ops, blog-workflow, browser-extension-dev, design-to-code, job-hunting, mcp-discovery, planning-workflow, skill-dev) |
| **Migration Needed** | Different structure - plugin planning workflow, not general plans |

## Structure Patterns Found

| Pattern | Plans Using It | Schema Compatibility |
|---------|----------------|---------------------|
| `PLAN.md` + `phase/*.md` | plan-commands-enhancement | Full |
| `index.md` + `phase/*.md` | merge-convert-skills, features/* | High (rename index→PLAN) |
| Numbered task files | sqlite-vec | Medium (restructure needed) |
| Research workflow | plugins/* | Low (different purpose) |
| Minimal/notes | ai-arusty-dev, convert-skill-mcp | N/A (not plans) |

## Recommendations

1. **Use as test cases:**
   - merge-convert-skills (near-compliant, good for `--fix-schema` testing)
   - sqlite-vec (partial, good for edge case testing)

2. **Skip migration:**
   - ai-arusty-dev, convert-skill-mcp (too minimal, not real plans)
   - plugins/* (different workflow, schema doesn't apply)

3. **Consider for future:**
   - Document "plugin planning workflow" as separate pattern
   - Document "task list" pattern (sqlite-vec style) as alternative
