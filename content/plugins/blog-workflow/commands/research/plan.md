---
name: blog:research:plan
description: Create analysis from research findings
argument-hint: <path>
arguments:
  - name: path
    description: Path to the research findings
    required: true
---

# Research Plan (Create Analysis)

Create an analysis artifact that synthesizes research findings into themes and insights.

**Important**: This is NOT a refinement of the research plan. This creates an **analysis** artifact from the findings.

## Prerequisites

- Research findings exist at specified path
- Research findings has content (can work on draft or approved findings)

## Behavior

### 1. Load Research Findings

```
Read the research findings at {{path}}
Verify frontmatter has type: research-findings
```

### 2. Verify Content Exists

Check that findings document has:

- At least one source consulted
- At least one finding documented
- Progress shows questions addressed

If findings is empty, error: "Research findings has no content. Run blog:research:draft first to execute research."

### 3. Create Analysis Directory

Create `research/analysis/` directory if needed.

### 4. Identify Themes

Analyze findings to identify cross-cutting themes:

- Group findings by concept, not by source
- Look for patterns across multiple sources
- Identify recurring ideas or approaches
- Note the strength of each theme (how many findings support it)

### 5. Find Agreements and Contradictions

#### Agreements

Where multiple sources align on a point:

- Note the shared conclusion
- Count supporting sources
- Assess confidence level

#### Contradictions

Where sources disagree:

- Document both positions
- Assess credibility of each source
- Provide recommendation on which to trust and why

### 6. Generate Original Observations

Identify insights that emerge from synthesis:

- Connections not made in any single source
- Patterns visible only when combining multiple perspectives
- Gaps in the literature that represent opportunities

### 7. Identify Content Opportunities

Based on the analysis, identify:

| Opportunity | Based On | Priority |
|-------------|----------|----------|
| {{content idea}} | {{theme/finding}} | {{high/medium/low}} |

### 8. Document Open Questions

Questions raised by the research that remain unanswered and may need:

- Additional research
- Expert consultation
- Hands-on experimentation

### 9. Create Analysis Artifact

Use template: `content/plugins/blog-workflow/.templates/research-analysis.md`

Fill in:

- **id**: Generate new UUIDv4
- **type**: `analysis`
- **status**: `draft`
- **parent**: Relative path to findings
- **created/updated**: Current ISO 8601 timestamp
- **Executive Summary**: 2-3 sentence overview
- **Themes**: Identified themes with evidence
- **Synthesis**: Agreements, contradictions, original observations
- **Content Opportunities**: Prioritized list
- **Open Questions**: Unanswered questions

### 10. Create Bidirectional Links

1. Set `parent` in analysis to relative path to findings
2. Add analysis to `children` array in findings frontmatter

### 11. Update Project Index

Add analysis to Artifacts table in `index.md`:

```markdown
| Research Analysis | draft | ./research/analysis/{{slug}}.md |
```

### 12. Self-Review

Run checklist items for synthesis quality:

- Findings organized by theme (not by source)
- Connections between sources identified
- Key insights clearly articulated

## Output Format

```
Analysis created: research/analysis/{{slug}}.md

Themes identified: {{count}}
- {{theme name}} ({{finding_count}} findings)
- {{theme name}} ({{finding_count}} findings)
- {{theme name}} ({{finding_count}} findings)

Content opportunities: {{count}}
Contradictions found: {{count}} (assessed)
Open questions: {{count}}

Next: Run `blog:research:review {{path}}` to evaluate and compile report
```

## Error Handling

| Condition | Response |
|-----------|----------|
| Findings not found | Error with path suggestion |
| Findings empty | Error suggesting draft command |
| Analysis already exists | Prompt to overwrite or create new slug |
| No themes identified | Warn and create minimal analysis |

## Notes

- Analysis should add value beyond summarizing findings
- Focus on synthesis, not repetition
- Prioritize actionable insights for content creation
- Theme names should be meaningful and descriptive
