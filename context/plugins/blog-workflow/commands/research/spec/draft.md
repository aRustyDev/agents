---
name: blog:research:spec:draft
description: Create a research plan from an approved project plan
arguments:
  - name: path
    description: Path to the approved project plan (plan.md)
    required: true
---

# Research Spec Draft

Create a research plan from an approved project plan.

## Prerequisites

- Project plan exists and has `status: approved`
- Project `index.md` exists

## Behavior

### 1. Load and Validate Project Plan

```
Read the project plan at {{path}}
Verify frontmatter has status: approved
If not approved, error: "Project plan must be approved before creating research plan. Run blog:idea:review first."
```

### 2. Persona Verification

Check for configured persona in the project:

1. Read project `index.md` frontmatter for `persona` field
2. If set, load persona from `context/plugins/blog-workflow/.templates/personas/<slug>.md`
3. Display to user: "This project uses persona: **{{name}}** — {{description}}. Use this persona? (yes / no / change)"
4. If not set, prompt user to select from available personas or proceed without one

### 3. Extract Research Requirements

From the project plan, extract:

- Research section content
- Key questions to answer
- Scope boundaries
- Source requirements

### 4. Generate Research Plan

Use template: `context/plugins/blog-workflow/.templates/research-plan.md`

Fill in:

- **id**: Generate new UUIDv4
- **type**: `research-plan`
- **status**: `draft`
- **parent**: Relative path to plan.md (e.g., `../../plan.md`)
- **created/updated**: Current ISO 8601 timestamp
- **Primary question**: Derived from research requirements
- **Secondary questions**: Supporting questions from plan
- **Scope**: In/out of scope from plan
- **Methodology**: Initial source strategy
- **Timeline**: Estimated based on scope

### 5. Create Output Files

1. Create `research/plans/` directory if needed
2. Generate slug from primary research question (lowercase, hyphenated, max 50 chars)
3. Write research plan to `research/plans/<slug>.md`

### 6. Update Bidirectional Links

1. Add `children: [./research/plans/<slug>.md]` to plan.md frontmatter
2. Ensure parent link in research plan points to plan.md

### 7. Update Project Index

1. Update project status to `research` in index.md frontmatter
2. Add research plan to Artifacts table:

```markdown
| Research Plan | draft | ./research/plans/<slug>.md |
```

### 8. Self-Review

Run checklist from `context/plugins/blog-workflow/.templates/review-checklists/research-plan.md`:

- Only flag `fail` items
- Report any failures to user
- Do not block on `warn` items

## Output Format

```
Created research plan: content/_projects/{{project-slug}}/research/plans/{{slug}}.md

Research Questions:
- Primary: {{primary question}}
- Secondary: {{count}} questions

Timeline: ~{{estimate}} estimated

Self-review: {{passed|failed with N issues}}

Next: Run `blog:research:spec:plan {{path}}` to refine methodology
```

## Error Handling

| Condition | Response |
|-----------|----------|
| Plan not found | Error with path suggestion |
| Plan not approved | Error with review command hint |
| Research plan already exists | Prompt to overwrite or use different slug |
| Missing research section in plan | Error asking user to add research requirements |
