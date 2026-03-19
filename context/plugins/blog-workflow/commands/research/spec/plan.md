---
name: blog:research:spec:plan
description: Refine a research plan with detailed methodology and sources
argument-hint: <path>
arguments:
  - name: path
    description: Path to the research plan to refine
    required: true
---

# Research Spec Plan

Refine an existing research plan with detailed methodology, specific sources, and actionable search strategies.

## Prerequisites

- Research plan exists at specified path
- Research plan has `type: research-plan` in frontmatter

## Behavior

**Important**: This command updates the research plan file **in place**. It does not create a new file.

### 1. Load Research Plan

```
Read the research plan at {{path}}
Verify frontmatter has type: research-plan
```

### 2. Expand Source Strategy

For each source type in the methodology section, add specific resources:

**Primary Sources**:
- Named documentation sites (e.g., official docs URLs)
- Relevant RFCs or specifications
- Authoritative reference materials

**Peer-Reviewed Sources**:
- Specific academic databases to search
- Conference proceedings to review
- Journal names relevant to topic

**Expert Sources**:
- Known experts in the field (blogs, talks)
- Conference talk recordings
- Technical blog posts from practitioners

**Community Sources**:
- Specific forums or communities
- Stack Overflow tags to monitor
- Discord/Slack communities if relevant

### 3. Add Detailed Search Queries

For each database/source type, add specific search queries:

```markdown
### Search Queries

| Source | Query | Expected Results |
|--------|-------|------------------|
| Google Scholar | "{{topic}}" AND "{{technique}}" | Academic papers |
| GitHub | "{{keyword}}" in:readme stars:>100 | Reference implementations |
| Hacker News | {{topic}} site:news.ycombinator.com | Community discussions |
```

### 4. Refine Timeline

Update timeline with concrete milestones:

```markdown
| Phase | Duration | Output | Checkpoint |
|-------|----------|--------|------------|
| Source discovery | 2 hours | Source list (15+ sources) | Review list quality |
| Deep reading | 4 hours | Raw notes per source | Verify coverage |
| Synthesis | 2 hours | Draft analysis | Theme identification |
```

### 5. Add Tool Recommendations

Recommend specific tools for research execution:

```markdown
### Recommended Tools

- **WebSearch**: Initial source discovery, current discussions
- **WebFetch**: Extract content from documentation sites
- **crawl4ai**: JavaScript-heavy sites, interactive documentation
- **Read**: Local documents, PDFs, existing research
```

### 6. Identify Coverage Gaps

Review research questions and flag any without clear source strategy:

```markdown
### Coverage Analysis

| Question | Sources Identified | Gap? |
|----------|-------------------|------|
| Primary | 8 sources | No |
| Secondary 1 | 3 sources | No |
| Secondary 2 | 1 source | Yes - need more expert sources |
```

### 7. Update Metadata

- Update `updated` timestamp to current ISO 8601
- Keep all other frontmatter unchanged

### 8. Self-Review

Run checklist items for methodology quality:

- Source types identified with purpose
- Search strategy is specific and actionable
- Quality criteria defined for source selection

## Output Format

```
Refined research plan: {{path}}

Added:
- {{N}} specific sources to consult
- Search queries for {{N}} databases
- Tool recommendations (WebSearch, WebFetch, crawl4ai)
- Milestone checkpoints
- Coverage analysis

{{If gaps found}}
Coverage gaps identified:
- {{question}}: {{gap description}}
{{/If}}

Next: Run `blog:research:spec:review {{path}}` to evaluate
```

## Notes

- This command is idempotent - running it multiple times will refine further
- Focus on making the plan actionable, not just comprehensive
- Prefer specific over generic (named sources over "search the web")
