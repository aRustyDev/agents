---
name: blog:research:refine
description: Update any research artifact based on review feedback
argument-hint: <path> ["feedback"]
arguments:
  - name: path
    description: Path to the research artifact to refine
    required: true
  - name: feedback
    description: Direct feedback to apply (optional, reads from ## Review section if not provided)
    required: false
---

# Research Refine

Update any research artifact based on review feedback.

## Prerequisites

- Research artifact exists at specified path
- Artifact has either a `## Review` section or feedback is provided directly

## Behavior

### 1. Load and Detect Artifact Type

```
Read the artifact at {{path}}
Detect type from frontmatter: research-plan, research-findings, analysis, or report
```

Supported artifact types:

| Type | Expected Location |
|------|-------------------|
| `research-plan` | `research/plans/<slug>.md` |
| `research-findings` | `research/findings/<slug>.md` |
| `analysis` | `research/analysis/<slug>.md` |
| `report` | `research/reports/<slug>.md` |

### 2. Load Feedback

If `--feedback` argument provided:
- Use the provided feedback text

Otherwise:
- Read the `## Review` section from the artifact
- Parse checklist items marked as `[ ]` (fail) or `[~]` (warn)
- Extract action items if present

If no feedback found, error: "No feedback found. Provide feedback via --feedback or run review command first."

### 3. Load Review Checklist

Based on artifact type, load corresponding checklist:

| Artifact Type | Checklist Path |
|---------------|----------------|
| `research-plan` | `.templates/review-checklists/research-plan.md` |
| `research-findings` | `.templates/review-checklists/research-findings.md` |
| `analysis` | `.templates/review-checklists/research-analysis.md` |

### 4. Apply Improvements

For each feedback item:

#### Research Plan

- Clarify research questions
- Expand scope boundaries
- Add specific sources to methodology
- Refine search strategy
- Adjust timeline estimates

#### Research Findings

- Add additional sources for gaps
- Improve source attribution
- Clarify contradictions between sources
- Update relevance assessments
- Document missing gaps

#### Analysis

- Reorganize by theme instead of source
- Strengthen connections between findings
- Add original observations
- Clarify content opportunities
- Document open questions

#### Report

- Improve executive summary
- Strengthen key findings
- Expand implications section
- Update bibliography format

### 5. Remove Review Section

**Important**: Remove the existing `## Review` section from the artifact.

The review section will be regenerated on the next review. Keeping old reviews causes confusion about current state.

### 6. Reset Status

Set artifact status → `draft`

This requires re-review before the artifact can be approved again.

### 7. Update Timestamp

Update `updated` field to current ISO 8601 timestamp.

### 8. Self-Review

Run fail-only checklist items for the artifact type:

- Only report blocking issues
- Do not report warnings

### 9. Update Project Index

Update the Artifacts table with new status:

```markdown
| {{Artifact Type}} | draft | {{path}} |
```

## Output Format

```
Refined: {{path}}

Changes applied:
- {{specific change}}
- {{specific change}}
- {{specific change}}

Status reset to: draft

{{If self-review issues}}
Self-review issues:
- {{blocking issue}}
{{/If}}

Next: Run appropriate review command to re-evaluate
```

## Error Handling

| Condition | Response |
|-----------|----------|
| Artifact not found | Error with path suggestion |
| Unknown artifact type | Error listing supported types |
| No feedback available | Error suggesting review command |
| No Review section and no --feedback | Error with guidance |

## Notes

- Refine is idempotent — can be run multiple times
- Always resets status to draft to require re-review
- Removes old review section to prevent stale feedback
- Focus on addressing specific feedback items
