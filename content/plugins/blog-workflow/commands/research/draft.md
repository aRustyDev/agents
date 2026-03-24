---
name: blog:research:draft
description: Execute research according to an approved research plan
argument-hint: <path>
arguments:
  - name: path
    description: Path to the approved research plan
    required: true
---

# Research Draft (Execute Research)

Execute research according to an approved research plan, creating findings document.

## Prerequisites

- Research plan exists and has `status: approved`
- Research plan has valid methodology and search strategy

## Behavior

### 1. Load and Validate Research Plan

```
Read the research plan at {{path}}
Verify frontmatter has status: approved
If not approved, error: "Research plan must be approved before executing. Run blog:research:spec:review first."
```

### 2. Initialize Findings Document

1. Create `research/findings/` directory if needed
2. Generate slug from research plan primary question
3. Load template from `content/plugins/blog-workflow/.templates/research-findings.md`
4. Initialize with:
   - **id**: Generate new UUIDv4
   - **type**: `research-findings`
   - **status**: `draft`
   - **parent**: Relative path to research plan
   - **created/updated**: Current ISO 8601 timestamp
   - **Progress**: Checkbox list of all research questions

### 3. Execute Research for Each Question

For each research question in the plan:

#### 3.1 Source Discovery

Use `WebSearch` to discover sources based on plan's search strategy:

- Execute specific search queries from plan
- Apply quality criteria from plan
- Record each source in Sources Consulted table

#### 3.2 Deep Reading

For each promising source:

- Use `WebFetch` for standard pages
- Use `crawl4ai` for JavaScript-heavy sites
- Use `Read` for local documents

#### 3.3 Extract Findings

For each source:

- Extract key findings with verbatim quotes
- Note source URL and access date
- Assess relevance (high/medium/low)
- Add interpretation notes

#### 3.4 Update Progress

Mark question as complete in progress tracker:

```markdown
- [x] Question 1: Complete (5 sources)
- [ ] Question 2: In progress (2 sources)
- [ ] Question 3: Not started
```

### 4. Document Unexpected Discoveries

Record findings that weren't explicitly searched for but are relevant to the research or content goals.

### 5. Identify Gaps

Note questions that couldn't be fully answered or areas needing more research.

### 6. Create Bidirectional Links

1. Set `parent` in findings to relative path to research plan
2. Add findings to `children` array in research plan frontmatter

### 7. Update Project Index

Add findings to Artifacts table in `index.md`:

```markdown
| Research Findings | draft | ./research/findings/{{slug}}.md |
```

### 8. Self-Review

Run checklist items for source quality and coverage:

- Primary sources cited for core claims
- All research questions addressed
- Sources properly attributed

## Tools Used

| Tool | Purpose |
|------|---------|
| `WebSearch` | Discover sources for each research question |
| `WebFetch` | Deep read and extract from sources |
| `crawl4ai` | JavaScript-heavy sites, interactive documentation |
| `Read` | Process user-provided local documents |

## Progress Tracking

The findings document includes checkboxes for each question. If research is interrupted:

1. Re-run `blog:research:draft {{path}}`
2. Command detects existing findings file
3. Skips completed questions (marked `[x]`)
4. Continues from incomplete questions

## Output Format

```
Research complete: research/findings/{{slug}}.md

Sources consulted: {{count}}
Questions answered: {{completed}}/{{total}}
Unexpected discoveries: {{count}}

Key findings:
1. {{finding summary}} ({{source_count}} sources)
2. {{finding summary}} ({{source_count}} sources)
3. {{finding summary}} ({{source_count}} sources)

{{If gaps found}}
Gaps identified:
- {{question or area needing more research}}
{{/If}}

Next: Run `blog:research:plan {{path}}` to create analysis
```

## Error Handling

| Condition | Response |
|-----------|----------|
| Research plan not found | Error with path suggestion |
| Research plan not approved | Error with review command hint |
| Findings file already exists | Prompt to continue or overwrite |
| Source inaccessible | Log warning, continue with other sources |
| Rate limited | Apply backoff, retry with limits |

## Notes

- Research can be time-intensive; progress is saved incrementally
- Prioritize primary sources for core claims
- Quote verbatim whenever possible for later verification
- If source contradicts others, note the contradiction
