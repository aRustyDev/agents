# Phase 3: Research Commands

## Objective

Plan, execute, and analyze research based on a project plan.

## Deliverables

### 1. Research Spec Commands

Create under `.claude/commands/blog/research/spec/`:

| Command | Purpose |
|---------|---------|
| `draft.md` | Plan research from project plan → `research/plans/<slug>.md` |
| `plan.md` | Refine research plan with methodology |
| `review.md` | Review research plan quality |

### 2. Research Execution Commands

Create under `.claude/commands/blog/research/`:

| Command | Purpose |
|---------|---------|
| `draft.md` | Execute research → `research/findings/<slug>.md` |
| `plan.md` | Create analysis plan → `research/analysis/<slug>.md` |
| `refine.md` | Update any research artifact |
| `review.md` | Evaluate analysis + compile report → `research/reports/<slug>.md` |

### 3. Review Checklists

Create `content/_templates/review-checklists/research-plan.md`:

```markdown
---
type: review-checklist
name: Research Plan Review
applies_to: research-plan
---

## Scope

- [ ] Research questions clearly defined
- [ ] Boundaries established (what's in/out)

## Methodology

- [ ] Sources identified (primary/secondary)
- [ ] Search strategy documented
- [ ] Quality criteria for sources

## Feasibility

- [ ] Time estimate reasonable
- [ ] Resources available
- [ ] Expertise gaps identified
```

Create `content/_templates/review-checklists/research-findings.md`:

```markdown
---
type: review-checklist
name: Research Findings Review
applies_to: research-findings
---

## Source Quality

- [ ] Primary sources cited
- [ ] Sources are authoritative/peer-reviewed
- [ ] Recency appropriate for topic

## Coverage

- [ ] All research questions addressed
- [ ] No significant gaps in coverage
- [ ] Diverse perspectives represented

## Documentation

- [ ] Sources properly attributed
- [ ] Key quotes captured
- [ ] Links to original sources working
```

Create `content/_templates/review-checklists/research-analysis.md`:

```markdown
---
type: review-checklist
name: Research Analysis Review
applies_to: analysis
---

## Synthesis Quality

- [ ] Findings organized by theme (not source)
- [ ] Connections between sources identified
- [ ] Contradictions acknowledged

## Insight Depth

- [ ] Key insights clearly articulated
- [ ] Implications for content outlined
- [ ] Original observations present (not just summary)

## Actionability

- [ ] Clear next steps identified
- [ ] Content opportunities highlighted
- [ ] Knowledge gaps noted for future research
```

### 4. Research Plan Template

Create `content/_templates/research-plans/standard.md`:

```markdown
---
type: template
name: Standard Research Plan
applies_to: research-plan
---

## Research Questions

1. Primary question: ...
2. Secondary questions: ...

## Methodology

### Sources

- Primary: ...
- Secondary: ...

### Search Strategy

- Keywords: ...
- Databases: ...
- Time range: ...

### Quality Criteria

- [ ] Peer-reviewed or authoritative
- [ ] Recent (within X years)
- [ ] Relevant to question

## Timeline

| Phase | Duration | Output |
|-------|----------|--------|
| Source discovery | ... | Source list |
| Deep reading | ... | Notes |
| Synthesis | ... | Analysis |

## Expected Outputs

- Findings document
- Analysis with key insights
- Final report
```

## Command Behaviors

### spec/draft.md

**Input**: Project `plan.md` path

**Output**: `research/plans/<slug>.md`

**Logic**:

1. Load project plan
2. Extract research needs section
3. Check for persona (prompt if not set)
4. Generate research plan using template
5. Create bidirectional links (parent/children)
6. Update project status → `research` in `index.md`
7. Add research plan to Artifacts table in `index.md`

### spec/review.md

**Input**: Research plan path

**Output**: Checklist evaluation

**Logic**:

1. Load research plan
2. Load `research-plan.md` checklist
3. Evaluate each criterion
4. Update artifact status → `in-review`
5. Update `index.md` with artifact status change

### draft.md (execute)

**Input**: Approved research plan path

**Output**: `research/findings/<slug>.md`

**Logic**:

1. Verify plan is approved
2. Execute research (Claude does actual research)
3. Document findings with sources
4. Create findings artifact
5. Update `index.md`

### plan.md (analysis)

**Input**: Findings path

**Output**: `research/analysis/<slug>.md`

**Logic**:

1. Load findings
2. Plan synthesis approach
3. Identify key themes/insights
4. Create analysis artifact

### review.md (final)

**Input**: Analysis + findings paths

**Output**: `research/reports/<slug>.md`

**Logic**:

1. Load analysis and findings
2. Evaluate analysis quality
3. If approved, compile into final report
4. Update all statuses
5. Update `index.md`

### refine.md

**Input**: Any research artifact path + feedback

**Output**: Updated artifact

**Logic**:

1. Load artifact and feedback
2. Apply improvements
3. Run self-review (fail items only)
4. Set status → `draft`
5. Update `index.md` with status change

## Project Structure After Research

```text
content/_projects/<slug>/
├── index.md
├── idea.md
├── plan.md
└── research/
    ├── plans/
    │   └── main.md
    ├── findings/
    │   └── main.md
    ├── analysis/
    │   └── main.md
    └── reports/
        └── main.md
```

## Tasks

- [ ] Create `.claude/commands/blog/research/spec/` directory
- [ ] Write `spec/draft.md` command
- [ ] Write `spec/plan.md` command
- [ ] Write `spec/review.md` command
- [ ] Write `research/draft.md` command
- [ ] Write `research/plan.md` command
- [ ] Write `research/refine.md` command
- [ ] Write `research/review.md` command
- [ ] Create `content/_templates/review-checklists/research-plan.md`
- [ ] Create `content/_templates/review-checklists/research-findings.md`
- [ ] Create `content/_templates/review-checklists/research-analysis.md`
- [ ] Create `content/_templates/research-plans/standard.md`
- [ ] Test full research flow end-to-end

## Acceptance Tests

- [ ] `/blog/research/spec/draft <plan.md>` creates `research/plans/<slug>.md`
- [ ] Research plan has valid frontmatter with `type: research-plan`
- [ ] Research plan has `parent` pointing to `plan.md`
- [ ] `plan.md` has `children` updated with research plan path
- [ ] `/blog/research/spec/review` evaluates against checklist
- [ ] `/blog/research/draft` creates `research/findings/<slug>.md`
- [ ] `/blog/research/plan` creates `research/analysis/<slug>.md`
- [ ] `/blog/research/review` produces `research/reports/<slug>.md`
- [ ] All research artifacts tracked in `index.md`
- [ ] `/blog/research/refine` accepts any research artifact
- [ ] Persona verification fires at `spec/draft` start
- [ ] Full flow completes without manual `index.md` fixes

## Entry Points

Per SPEC, research phase can be entered:

- **From ideation**: After approved project plan (normal flow)
- **Directly**: With `/blog/research/spec/draft` if you already know what to research

When entering directly without a project plan, the command should:

1. Create a minimal project structure
2. Create index.md with status: `research`
3. Skip the plan.md artifact

## Dependencies

- Phase 0 (Foundation) — required
- Phase 1 (Ideation) — optional (can enter directly)
- Phase 2 (Persona/Template) — for persona verification

## Estimated Effort

4-5 hours
