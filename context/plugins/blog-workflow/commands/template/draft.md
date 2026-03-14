---
name: blog/template/draft
description: Create a new structural template for blog artifacts
argument-hint: <type> <name>
arguments:
  - name: type
    description: "Template type: outlines, research-plans, review-checklists, brainstorm-plans"
    required: true
  - name: name
    description: Template name/slug
    required: true
---

# Template Draft

Create a new structural template for blog workflow artifacts.

## Behavior

1. **Validate type**:
   - Must be one of: `outlines`, `research-plans`, `review-checklists`, `brainstorm-plans`
   - Error if invalid type provided

2. **Generate slug** from name:
   - Lowercase, replace spaces with hyphens
   - Add appropriate suffix based on type:
     - outlines → `.outline.md`
     - research-plans → `.md`
     - review-checklists → `.md`
     - brainstorm-plans → `.md`

3. **Generate template structure** based on type:

   **outlines**:
   - Frontmatter: type, name, applies_to, content_type
   - Sections with word count estimates
   - Required vs optional markers

   **research-plans**:
   - Frontmatter: type, name, applies_to
   - Methodology sections
   - Source categories
   - Deliverable format

   **review-checklists**:
   - Frontmatter: type, name, applies_to
   - Criteria grouped by category
   - Severity indicators (fail/warn)

   **brainstorm-plans**:
   - Frontmatter: type, name, applies_to
   - Exploration areas
   - Constraint definitions
   - Output goals

4. **Mark sections**:
   - Required sections: must be filled
   - Optional sections: can be omitted
   - Conditional sections: include if applicable

5. **Add placeholder guidance** for each section

## Output

```text
Created template: .templates/<type>/<slug>.<suffix>

Type: <type>
Sections: X (Y required, Z optional)

Next: Run `blog:template:plan <path>` to refine with examples
```

## Example

**Input**: `blog:template:draft outlines case-study`

**Output**:

```text
Created template: .templates/outlines/case-study.outline.md

Type: outlines
Sections: 7 (5 required, 2 optional)

Structure:
1. [required] Problem Statement (200-300 words)
2. [required] Context & Constraints (300-400 words)
3. [required] Technical Approach (500-800 words)
4. [optional] Alternative Approaches Considered (200-300 words)
5. [required] Results & Metrics (300-400 words)
6. [required] Lessons Learned (200-300 words)
7. [optional] Future Improvements (100-200 words)

Next: Run `blog:template:plan .templates/outlines/case-study.outline.md` to refine
```

## Template Types Reference

| Type | Purpose | Suffix |
|------|---------|--------|
| `outlines` | Post structure templates | `.outline.md` |
| `research-plans` | Research methodology templates | `.md` |
| `review-checklists` | Evaluation criteria | `.md` |
| `brainstorm-plans` | Brainstorming structure | `.md` |
