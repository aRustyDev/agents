# Phase 2: Create Command Enhancement

**ID:** `phase-2`
**Dependencies:** phase-1
**Status:** complete
**Effort:** 2 hours

## Objective

Update `/context:plan:create` to generate schema-compliant plans with all required sections.

## Success Criteria

- [ ] Generated plans pass schema validation
- [ ] All required tables include correct columns
- [ ] Phase documents include Files section
- [ ] Output validation step confirms compliance

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Enhanced create.md | `context/commands/context/plan/create.md` | Slash command |

## Files

**Create:**

- None

**Modify:**

- `context/commands/context/plan/create.md`

## Key Changes

### 1. Output Structure Update

Change from `index.md` to `PLAN.md`:

```text
<location>/<plan-name>/
├── PLAN.md            # Unified plan (schema-compliant)
└── phase/
    ├── 1-<name>.md
    └── ...
```

### 2. PLAN.md Template

Add required sections:

- `## Objectives` table with `Measurable` column
- `## Current State` table with `Current/Target/Gap` columns
- `## Phases` table with `ID/Dependencies/Status` columns
- `## Risks` table with `Mitigation` column

### 3. Phase Template

Add required sections per phase:

- `## Success Criteria` as checklist
- `## Deliverables` table with `Location` column
- `## Files` with `Create:` and `Modify:` subsections

### 4. Validation Step

Add Step 6: Validate Output

- Check PLAN.md has all required tables
- Check each phase has required sections
- Report validation status in output

### 5. Enhanced Questions

Update AskUserQuestion to collect:

- Measurable objectives (not just objectives)
- Current state metrics
- Target values per metric

## Tasks

- [ ] Update PLAN.md template with required tables
- [ ] Update phase template with Files section
- [ ] Add validation step before reporting
- [ ] Update AskUserQuestion prompts
- [ ] Update output report to show schema status

## Notes

- Backward compatibility: old plans still work, just won't validate
- Consider `--minimal` flag for quick scaffolding without questions
