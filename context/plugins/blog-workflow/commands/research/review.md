---
name: blog:research:review
description: Evaluate research analysis and compile final report
argument-hint: <path> [--approve]
arguments:
  - name: path
    description: Path to the research analysis to review
    required: true
  - name: approve
    description: Auto-approve if only warnings remain (no fails)
    required: false
  - name: no-approve
    description: Evaluate only, never compile report
    required: false
---

# Research Review (Evaluate + Compile Report)

Evaluate research analysis quality and, if approved, compile the final research report.

**Important**: This command does TWO things:
1. Evaluates the analysis quality against the checklist
2. If approved, compiles the final report

There is no separate "compile" or "report" command.

## Prerequisites

- Research analysis exists at specified path
- Analysis has `type: analysis` in frontmatter

## Behavior

### 1. Load Analysis and Context

```
Read the analysis at {{path}}
Load the parent findings (from analysis.parent)
Load the research plan (from findings.parent)
Extract project path from artifact location
```

### 2. Load Review Checklist

Load checklist from: `context/plugins/blog-workflow/.templates/review-checklists/research-analysis.md`

### 3. Evaluate Each Criterion

For each checklist item, evaluate as:

- **pass** `[x]` - Criterion fully met
- **warn** `[~]` - Criterion partially met or could be improved
- **fail** `[ ]` - Criterion not met, blocks approval

#### Synthesis Quality

- [ ] Findings organized by theme (not by source)
- [ ] Connections between sources identified
- [ ] Contradictions acknowledged and assessed

#### Insight Depth

- [ ] Key insights are clearly articulated
- [ ] Implications for content are outlined
- [ ] Original observations present (not just summary)

#### Actionability

- [ ] Content opportunities are specific
- [ ] Next steps are clear and actionable
- [ ] Open questions documented for future work

#### Traceability

- [ ] Each theme links back to specific findings
- [ ] Analysis can be verified against source material

### 4. Append Review Section

Remove any existing `## Review` section from the analysis, then append:

```markdown
## Review

**Reviewed**: {{ISO 8601 timestamp}}
**Result**: {{pass|warn|fail}}

### Synthesis Quality
- [x] Organized by theme — pass
- [x] Connections identified — pass
- [x] Contradictions assessed — pass

### Insight Depth
- [x] Key insights clear — pass
- [x] Content implications outlined — pass
- [x] Original observations present — pass

### Actionability
- [x] Content opportunities specific — pass
- [x] Next steps clear — pass
- [x] Open questions documented — pass

### Traceability
- [x] Themes link to findings — pass
- [x] Verifiable against sources — pass

**Summary**: {{pass_count}} pass, {{warn_count}} warn, {{fail_count}} fail

{{If warnings or fails}}

### Action Items
1. {{specific action to address issue}}
2. {{specific action to address issue}}
{{/If}}
```

### 5. Determine Approval

| Condition | `--approve` flag | `--no-approve` flag | Default |
|-----------|------------------|---------------------|---------|
| All pass | approved + compile | in-review | Prompt user |
| Warns only | approved + compile | in-review | Prompt user |
| Any fail | in-review | in-review | in-review |

If prompting user: "Analysis review complete with {{summary}}. Approve and compile report? (yes/no)"

### 6. If Not Approved

- Set analysis `status: in-review` in frontmatter
- Update `updated` timestamp
- Update `index.md` with status change
- Stop here — do not compile report

### 7. If Approved — Compile Report

#### 7.1 Create Report Directory

Create `research/reports/` directory if needed.

#### 7.2 Generate Report

Use template: `context/plugins/blog-workflow/.templates/research-report.md`

Fill in:

- **id**: Generate new UUIDv4
- **type**: `report`
- **status**: `complete`
- **parent**: Relative path to analysis
- **created/updated**: Current ISO 8601 timestamp
- **Overview**: Research questions, period, source count
- **Key Findings**: Top 3-5 major findings with implications
- **Detailed Analysis**: Synthesized narrative from analysis
- **Implications for Content**: What to emphasize, avoid, unique angle
- **Source Bibliography**: Full citations for all sources

#### 7.3 Update Analysis Status

Set analysis `status: complete`

#### 7.4 Update Upstream Artifacts

Set status → `complete` for:
- Research findings
- Research plan

#### 7.5 Create Bidirectional Links

1. Set `parent` in report to relative path to analysis
2. Add report to `children` array in analysis frontmatter

#### 7.6 Update Project Index

Add report to Artifacts table:

```markdown
| Research Report | complete | ./research/reports/{{slug}}.md |
```

Update project status in `index.md`:
- If content phase planned: `status: content-planning`
- If research-only project: `status: complete`

## Output Format

### If Not Approved

```
## Research Analysis Review: {{filename}}

### Synthesis Quality
- [x] Organized by theme — pass
- [ ] Connections identified — fail: themes are isolated
- [x] Contradictions assessed — pass

...

Summary: 9 pass, 0 warn, 2 fail
Status: in-review

Action Items:
1. Add cross-references between Theme 2 and Theme 4
2. {{other action}}

Next: Run `blog:research:refine {{path}}` to address issues
```

### If Approved

```
## Research Analysis Review: {{filename}}

### Synthesis Quality
- [x] Organized by theme — pass
- [x] Connections identified — pass
- [x] Contradictions assessed — pass

...

Summary: 11 pass, 0 warn, 0 fail
Status: approved

---

Report compiled: research/reports/{{slug}}.md

Key findings: {{count}}
Sources cited: {{count}}
Content implications: {{count}} action items

Research phase complete.

Next: Run `blog:content:draft {{report-path}}` to begin content planning
```

## Error Handling

| Condition | Response |
|-----------|----------|
| Analysis not found | Error with path suggestion |
| Wrong artifact type | Error indicating expected type |
| Checklist not found | Error with checklist path |
| Parent findings not found | Warn, continue with available data |
| Parent plan not found | Warn, continue with available data |

## Notes

- The report is only compiled when analysis is approved
- Report compilation uses data from all upstream artifacts
- All upstream artifacts are marked complete upon report generation
- Project status advances to content-planning (or complete)
