# Phase 3: Research Commands

## Objective

Plan, execute, and analyze research based on a project plan.

## Architecture Note

Research is the only phase with a sub-directory structure. This is intentional — research has a distinct **spec-then-execute** pattern:

- **`spec/` commands** define *what* to research (research planning)
- **Top-level commands** *execute* and *analyze* that research

```
research/
├── spec/
│   ├── draft.md   → Create research plan from project plan
│   ├── plan.md    → Refine research plan with methodology
│   └── review.md  → Evaluate research plan quality
├── draft.md       → Execute research → findings
├── plan.md        → Create analysis from findings
├── refine.md      → Update any research artifact
└── review.md      → Evaluate analysis + compile report
```

The `review` command at the end both evaluates the analysis quality AND produces the report as its output. There is no separate "compile" or "report" command.

## Deliverables

### 1. Research Spec Commands

Create under `context/plugins/blog-workflow/commands/research/spec/`:

| Command | Purpose | Output |
|---------|---------|--------|
| `draft.md` | Create research plan from project plan | `research/plans/<slug>.md` |
| `plan.md` | Refine research plan with methodology | Updated research plan |
| `review.md` | Evaluate research plan quality | Checklist evaluation |

**Command frontmatter pattern**:

```yaml
---
name: blog:research:spec:draft
description: Create a research plan from an approved project plan
arguments:
  - name: path
    description: Path to the approved project plan
    required: true
---
```

### 2. Research Execution Commands

Create under `context/plugins/blog-workflow/commands/research/`:

| Command | Purpose | Output |
|---------|---------|--------|
| `draft.md` | Execute research | `research/findings/<slug>.md` |
| `plan.md` | Create analysis from findings | `research/analysis/<slug>.md` |
| `refine.md` | Update any research artifact | Updated artifact |
| `review.md` | Evaluate analysis + compile report | `research/reports/<slug>.md` |

**Command frontmatter pattern**:

```yaml
---
name: blog:research:draft
description: Execute research according to an approved research plan
arguments:
  - name: path
    description: Path to the approved research plan
    required: true
---
```

### 3. Artifact Templates

Create under `context/plugins/blog-workflow/.templates/`:

#### research-plan.md

```markdown
---
type: research-plan
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to plan.md}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Research Plan: {{title}}

## Research Questions

### Primary Question

{{main question this research answers}}

### Secondary Questions

1. {{supporting question}}
2. {{supporting question}}

## Scope

### In Scope

- {{what will be researched}}

### Out of Scope

- {{what will NOT be researched}}

## Methodology

### Source Strategy

| Source Type | Examples | Purpose |
|-------------|----------|---------|
| Primary | Official docs, specs, RFCs | Core claims |
| Peer-reviewed | Papers, journals | Research backing |
| Expert | Conference talks, tech blogs | Practitioner insights |
| Community | Stack Overflow, forums | Common issues |

### Search Strategy

- **Keywords**: {{search terms}}
- **Databases**: {{where to search}}
- **Time range**: {{recency requirements}}

### Quality Criteria

- [ ] Authoritative or peer-reviewed source
- [ ] Recent enough for topic (within {{X}} years)
- [ ] Directly relevant to research questions

## Timeline

| Phase | Duration | Output |
|-------|----------|--------|
| Source discovery | {{estimate}} | Source list |
| Deep reading | {{estimate}} | Raw notes |
| Synthesis | {{estimate}} | Analysis |

## Expected Outputs

- Findings document with sourced claims
- Analysis with key insights and themes
- Final report with actionable conclusions
```

#### research-findings.md

```markdown
---
type: research-findings
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to research-plan.md}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Research Findings: {{title}}

## Progress

- [ ] Question 1: {{status}}
- [ ] Question 2: {{status}}
- [ ] Question 3: {{status}}

## Sources Consulted

| # | Source | Type | Accessed | Relevance |
|---|--------|------|----------|-----------|
| 1 | {{title/URL}} | {{type}} | {{date}} | {{high/medium/low}} |

## Findings by Question

### Question 1: {{question text}}

#### Key Finding 1.1

{{finding statement}}

**Source**: [{{citation}}]({{url}})
**Quote**: "{{relevant quote}}"
**Notes**: {{interpretation or context}}

#### Key Finding 1.2

{{...}}

### Question 2: {{question text}}

{{...}}

## Unexpected Discoveries

{{things found that weren't explicitly searched for but are relevant}}

## Gaps Identified

{{questions that couldn't be answered, areas needing more research}}
```

#### research-analysis.md

```markdown
---
type: analysis
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to research-findings.md}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Research Analysis: {{title}}

## Executive Summary

{{2-3 sentence overview of key insights}}

## Themes

### Theme 1: {{theme name}}

**Summary**: {{what this theme encompasses}}

**Supporting Evidence**:
- Finding 1.1: {{brief reference}}
- Finding 2.3: {{brief reference}}

**Implications**: {{what this means for the content}}

### Theme 2: {{theme name}}

{{...}}

## Synthesis

### Agreements Across Sources

{{where sources align}}

### Contradictions

{{where sources disagree, with assessment of which is more credible}}

### Original Observations

{{insights that emerge from combining sources, not found in any single source}}

## Content Opportunities

| Opportunity | Based On | Priority |
|-------------|----------|----------|
| {{content idea}} | {{theme/finding}} | {{high/medium/low}} |

## Open Questions

{{questions raised by the research that remain unanswered}}

## Recommended Next Steps

1. {{action item}}
2. {{action item}}
```

#### research-report.md

```markdown
---
type: report
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to research-analysis.md}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Research Report: {{title}}

## Overview

**Research Questions**: {{primary question}}
**Period**: {{start date}} — {{end date}}
**Sources Consulted**: {{count}}

## Key Findings

1. {{major finding with implications}}
2. {{major finding with implications}}
3. {{major finding with implications}}

## Detailed Analysis

{{synthesized narrative drawing from analysis}}

## Implications for Content

### What to Emphasize

- {{key point to make in content}}

### What to Avoid

- {{common misconception or outdated information}}

### Unique Angle

{{what makes this research valuable, what perspective it enables}}

## Source Bibliography

{{formatted list of all sources with full citations}}

## Appendix: Raw Data

{{optional: tables, statistics, or detailed data}}
```

### 4. Review Checklists

Create under `context/plugins/blog-workflow/.templates/review-checklists/`:

#### research-plan.md

```markdown
---
type: review-checklist
name: Research Plan Review
applies_to: research-plan
---

## Scope Clarity

- [ ] Primary research question is clearly defined
- [ ] Secondary questions support the primary question
- [ ] Boundaries established (what's in/out of scope)

## Methodology Quality

- [ ] Source types identified with purpose
- [ ] Search strategy is specific and actionable
- [ ] Quality criteria defined for source selection

## Feasibility

- [ ] Time estimate is reasonable for scope
- [ ] Required tools/access are available
- [ ] Expertise gaps identified (if any)

## Alignment

- [ ] Research questions trace back to project plan goals
- [ ] Expected outputs match what content phase needs
```

#### research-findings.md

```markdown
---
type: review-checklist
name: Research Findings Review
applies_to: research-findings
---

## Source Quality

- [ ] Primary sources cited for core claims
- [ ] Sources are authoritative or peer-reviewed
- [ ] Recency is appropriate for topic

## Coverage

- [ ] All research questions addressed
- [ ] No significant gaps in coverage
- [ ] Multiple perspectives represented where relevant

## Documentation

- [ ] Sources properly attributed with URLs
- [ ] Key quotes captured verbatim
- [ ] Access dates recorded
- [ ] Source relevance assessed

## Completeness

- [ ] Progress tracking shows all questions complete
- [ ] Unexpected discoveries documented
- [ ] Knowledge gaps explicitly noted
```

#### research-analysis.md

```markdown
---
type: review-checklist
name: Research Analysis Review
applies_to: analysis
---

## Synthesis Quality

- [ ] Findings organized by theme (not by source)
- [ ] Connections between sources identified
- [ ] Contradictions acknowledged and assessed

## Insight Depth

- [ ] Key insights are clearly articulated
- [ ] Implications for content are outlined
- [ ] Original observations present (not just summary)

## Actionability

- [ ] Content opportunities are specific
- [ ] Next steps are clear and actionable
- [ ] Open questions documented for future work

## Traceability

- [ ] Each theme links back to specific findings
- [ ] Analysis can be verified against source material
```

## Skill Behaviors

### spec/draft.md

**Input**: Path to approved project `plan.md`

**Output**: `research/plans/<slug>.md`

**Tools Used**:
- `Read` — load project plan
- `Write` — create research plan

**Logic**:

1. Load project plan
2. Verify plan status is `approved`
3. Extract research needs from plan's "Research Requirements" section
4. **Persona verification**: Check for configured persona, confirm with user
5. Generate research plan using `.templates/research-plan.md`
6. Create `research/plans/` directory if needed
7. Generate slug from primary research question
8. Create bidirectional links:
   - Set `parent` in research plan to `../../plan.md`
   - Add research plan to `children` in `plan.md`
9. Update project status → `research` in `index.md`
10. Add research plan to Artifacts table in `index.md`
11. Run self-review (fail items only)

**Example output**:

```text
Created research plan: content/_projects/kubernetes-migration/research/plans/migration-patterns.md

Research Questions:
- Primary: What are proven patterns for zero-downtime Kubernetes migrations?
- Secondary: 3 questions

Timeline: ~4 hours estimated

Self-review: passed

Next: Run `blog:research:spec:plan <path>` to refine methodology
```

### spec/plan.md

**Input**: Path to research plan draft

**Output**: **Updates the same file in place** with structured methodology, source types, and coverage gaps filled

> **Note**: This command does NOT create a new file. It refines the existing research plan file created by `spec/draft`.

**Logic**:

1. Load existing research plan
2. Expand source strategy with specific resources:
   - Named documentation sites
   - Specific search queries
   - Known expert sources
3. Add detailed search queries for each database/source
4. Refine timeline with concrete milestones
5. Add tool recommendations (WebSearch, WebFetch, crawl4ai)
6. Update `updated` timestamp
7. Run self-review

**Example output**:

```text
Refined research plan: research/plans/migration-patterns.md

Added:
- 12 specific sources to consult
- Search queries for 3 databases
- Tool recommendations (WebSearch, crawl4ai)
- Milestone checkpoints

Next: Run `blog:research:spec:review <path>` to evaluate
```

### spec/review.md

**Input**: Path to research plan

**Output**: Checklist evaluation with approval decision + `## Review` section appended to artifact

**Logic**:

1. Load research plan
2. Load `.templates/review-checklists/research-plan.md`
3. Evaluate each criterion (pass/warn/fail)
4. **Append `## Review` section** to the artifact file (replacing any previous review section)
5. If all pass (or only warns with `--approve`): set status → `approved`
6. If any fail: keep status as `in-review`, report issues
7. Update `index.md` with status change

> **Review storage**: Review results are appended directly to the reviewed artifact in a `## Review` section.

**Approval flags**:
- `--approve` — Auto-approve if only warn items remain
- `--no-approve` — Always keep in review (for human sign-off)

**Example output**:

```text
## Research Plan Review: migration-patterns.md

### Scope Clarity
- [x] Primary question clearly defined — pass
- [x] Secondary questions support primary — pass
- [x] Boundaries established — pass

### Methodology Quality
- [x] Source types identified — pass
- [x] Search strategy actionable — pass
- [~] Quality criteria defined — warn: could be more specific

### Feasibility
- [x] Time estimate reasonable — pass
- [x] Tools available — pass
- [x] Expertise gaps identified — pass

### Alignment
- [x] Questions trace to project goals — pass
- [x] Outputs match content needs — pass

Summary: 11 pass, 1 warn, 0 fail
Status: approved

Next: Run `blog:research:draft <path>` to begin research
```

### draft.md (execute research)

**Input**: Path to approved research plan

**Output**: `research/findings/<slug>.md`

**Tools Used**:
- `WebSearch` — discover sources for each research question
- `WebFetch` — deep read and extract from sources
- `Read` — process user-provided local documents
- MCP servers — `crawl4ai` for JavaScript-heavy sites

**Logic**:

1. Verify research plan is `approved`
2. Create `research/findings/` directory if needed
3. Initialize findings document from `.templates/research-findings.md`
4. For each research question:
   - Execute search strategy from plan
   - Evaluate and select sources based on quality criteria
   - Extract key findings with quotes and attribution
   - Update progress tracker in findings document
5. Document unexpected discoveries
6. Note any gaps or unanswered questions
7. Create bidirectional links to research plan
8. Update `index.md` with new artifact
9. Run self-review

**Progress tracking**: The findings document includes checkboxes for each question. If research is interrupted, re-running the skill continues from incomplete questions.

**Example output**:

```text
Research complete: research/findings/migration-patterns.md

Sources consulted: 14
Questions answered: 3/3
Unexpected discoveries: 2

Key findings:
1. Blue-green deployments most common (8 sources)
2. Canary releases preferred for stateful services (5 sources)
3. Feature flags essential for rollback (6 sources)

Next: Run `blog:research:plan <path>` to create analysis
```

### plan.md (create analysis)

**Input**: Path to research findings

**Output**: `research/analysis/<slug>.md`

**Note**: This is NOT a refinement of the research plan. This creates an **analysis** artifact that synthesizes the findings into themes and insights.

**Logic**:

1. Load findings document
2. Verify findings has content (can work on draft or approved findings)
3. Create `research/analysis/` directory if needed
4. Identify themes across findings (not organized by source)
5. Find agreements and contradictions between sources
6. Generate original observations from synthesis
7. Identify content opportunities
8. Document open questions
9. Create analysis artifact from `.templates/research-analysis.md`
10. Create bidirectional links (parent: findings, update findings children)
11. Update `index.md`
12. Run self-review

**Example output**:

```text
Analysis created: research/analysis/migration-patterns.md

Themes identified: 4
- Deployment strategies (12 findings)
- State management (8 findings)
- Rollback mechanisms (6 findings)
- Monitoring requirements (5 findings)

Content opportunities: 3
Contradictions found: 1 (assessed)
Open questions: 2

Next: Run `blog:research:review <path>` to evaluate and compile report
```

### review.md (evaluate + compile report)

**Input**: Path to research analysis

**Output**: Evaluation + `research/reports/<slug>.md`

**Note**: This command does TWO things:
1. Evaluates the analysis quality against the checklist
2. If approved, compiles the final report

There is no separate "compile" command.

**Logic**:

1. Load analysis (and transitively: findings, plan)
2. Load `.templates/review-checklists/research-analysis.md`
3. Evaluate each criterion (pass/warn/fail)
4. If any fail: report issues, keep status as `draft`, stop here
5. If approved (all pass, or warns with `--approve`):
   - Create `research/reports/` directory if needed
   - Generate report from `.templates/research-report.md`
   - Populate with executive summary from analysis
   - Include detailed findings narrative
   - Add content implications section
   - Generate full bibliography
   - Set report status → `complete`
   - Set analysis status → `complete`
   - Update project status in `index.md`:
     - If content phase planned: status → `content`
     - If research-only: status → `complete`
6. Update `index.md` with report artifact

**Example output (approved)**:

```text
## Research Analysis Review: migration-patterns.md

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

Summary: 11 pass, 0 warn, 0 fail
Status: approved

---

Report compiled: research/reports/migration-patterns.md

Key findings: 3
Sources cited: 14
Content implications: 5 action items

Research phase complete.

Next: Run `blog:content:draft <report-path>` to begin content planning
```

### refine.md

**Input**: Path to any research artifact (reads `## Review` section from artifact, or accepts feedback as direct input)

**Output**: Updated artifact with `## Review` section removed

**Logic**:

1. Detect artifact type from frontmatter (`research-plan`, `research-findings`, `analysis`, `report`)
2. Read the `## Review` section from the artifact (or accept feedback as direct input)
3. Load corresponding review checklist
4. Apply feedback/improvements to artifact
5. **Remove the `## Review` section** (it will be regenerated on next review)
6. Run self-review (fail items only)
7. Set status → `draft` (resets approval, requires re-review)
8. Update `updated` timestamp
9. Update `index.md` with status change

**Example output**:

```text
Refined: research/findings/migration-patterns.md

Changes applied:
- Added 3 additional sources for Question 2
- Clarified contradiction between sources 5 and 8
- Updated relevance assessments

Status reset to: draft

Next: Run appropriate review command to re-evaluate
```

## Project Structure After Research

```text
content/_projects/<slug>/
├── index.md                    # status: research → content (or complete)
├── idea.md                     # status: complete
├── plan.md                     # status: complete
└── research/
    ├── plans/
    │   └── <slug>.md           # status: complete
    ├── findings/
    │   └── <slug>.md           # status: complete
    ├── analysis/
    │   └── <slug>.md           # status: complete
    └── reports/
        └── <slug>.md           # status: complete
```

## Entry Points

Per SPEC, the flow is not rigid. Research can be entered at:

| Scenario | Start At | Notes |
|----------|----------|-------|
| From approved project plan | `blog:research:spec:draft` | Normal flow |
| Know what to research (no project) | `blog:research:spec:draft` | Creates minimal project first |
| Research already done externally | `blog:content:draft` | Skip to content planning |

### Direct Entry Without Project Plan

When entering `blog:research:spec:draft` without an existing project:

1. Prompt user for research topic
2. Run `blog:idea:brainstorm` internally to create project
3. Run `blog:idea:draft-plan` to create minimal plan with research focus
4. Continue with research spec creation

This keeps the project structure consistent while allowing flexible entry.

## Multiple Research Plans

A single project can have multiple research plans for different aspects:

```text
research/plans/
├── technical-patterns.md       # How the technology works
├── adoption-landscape.md       # Who uses it and why
└── competitive-analysis.md     # Alternatives comparison
```

Each plan follows the same workflow independently. Slugs are generated from each plan's primary question. The final report can synthesize multiple analyses.

## Alignment with SPEC

This phase implements SPEC sections:

- **Phase 2: Research** (lines 97-121) — command structure and flow
- **Entry Points** (lines 562-572) — "Know what to research" entry
- **End-to-End Flow** (lines 507-517) — research flow diagram
- **Acceptance Tests Phase 3** (lines 1031-1042) — all test cases

Key SPEC quotes implemented:

> "Research is the only phase with a sub-directory in the command structure. This is intentional - research has a distinct spec-then-execute pattern"
>
> "The `review` command at the end is the final step that both evaluates the analysis quality and produces the report as its output. There is no separate 'report' command."
>
> "Persona verification: At `spec/draft` start, check for configured persona and confirm with user in conversation."

## Tasks

### Commands (7 files)

- [ ] Create `context/plugins/blog-workflow/commands/research/spec/` directory
- [ ] Write `commands/research/spec/draft.md` with command frontmatter
- [ ] Write `commands/research/spec/plan.md` with command frontmatter
- [ ] Write `commands/research/spec/review.md` with command frontmatter
- [ ] Write `commands/research/draft.md` with command frontmatter
- [ ] Write `commands/research/plan.md` with command frontmatter
- [ ] Write `commands/research/refine.md` with command frontmatter
- [ ] Write `commands/research/review.md` with command frontmatter

### Templates (4 artifact templates)

- [ ] Create `.templates/research-plan.md` artifact template
- [ ] Create `.templates/research-findings.md` artifact template
- [ ] Create `.templates/research-analysis.md` artifact template
- [ ] Create `.templates/research-report.md` artifact template

### Review Checklists (3 files)

- [ ] Create `.templates/review-checklists/research-plan.md`
- [ ] Create `.templates/review-checklists/research-findings.md`
- [ ] Create `.templates/review-checklists/research-analysis.md`

### Plugin Updates

- [ ] Update `plugin.json` with 7 new commands
- [ ] Update `marketplace.json` version (1.2.0 → 1.3.0)

### Testing

- [ ] Test spec flow: spec/draft → spec/plan → spec/review
- [ ] Test execution flow: draft → plan → review (with report compilation)
- [ ] Test refine on each artifact type (research-plan, findings, analysis)
- [ ] Test --approve and --no-approve flags on spec/review
- [ ] Test direct entry without prior project plan
- [ ] Test multiple research plans in single project
- [ ] Test persona verification fires at spec/draft
- [ ] Verify index.md tracking through all stages
- [ ] Verify bidirectional links maintained correctly
- [ ] Test review.md compiles report only when analysis approved

## Acceptance Tests

(From SPEC lines 1031-1042)

- [ ] `/blog/research/spec/draft content/_projects/<slug>/plan.md` creates `research/plans/<slug>.md` inside the project directory
- [ ] Research plan has valid artifact frontmatter with `type: research-plan` and `parent` pointing to `plan.md`
- [ ] `plan.md` has `children` updated to include the research plan path
- [ ] `/blog/research/spec/review` evaluates the research plan against `research-plan.md` checklist
- [ ] `/blog/research/draft` (execute research) creates `research/findings/<slug>.md` with `type: research-findings`
- [ ] `/blog/research/plan` creates `research/analysis/<slug>.md` with `type: analysis`
- [ ] `/blog/research/review` evaluates analysis and produces `research/reports/<slug>.md` with `type: report`
- [ ] All research artifacts are tracked in `index.md`
- [ ] `/blog/research/refine` accepts any research artifact and applies feedback
- [ ] Persona verification fires at `spec/draft` start
- [ ] The full research flow (spec/draft → spec/plan → spec/review → draft → plan → review) completes end-to-end without manual `index.md` fixes

## Dependencies

- Phase 0 (Foundation) — required for templates, rules, schemas
- Phase 1 (Ideation) — required for project plan input (or direct entry creates one)
- Phase 2 (Persona/Template) — for persona verification at spec/draft

## Estimated Effort

5-6 hours

- Spec skills (3 files): 1.5 hours
- Execution skills (4 files): 2 hours
- Artifact templates (4 files): 1 hour
- Review checklists (3 files): 30 min
- Plugin manifest updates: 15 min
- Testing all workflows: 45 min
