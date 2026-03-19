---
name: blog:content:draft
description: Create content brainstorm from research report
argument-hint: <path> [--force]
arguments:
  - name: path
    description: Path to the research report
    required: true
  - name: force
    description: Overwrite existing content-brainstorm.md
    required: false
---

# Content Draft Command

Create a content brainstorm document from a completed research report. This command analyzes research findings and identifies potential content pieces (tutorials, deep-dives, experiments, explainers).

## Tools

- `Read` - Load research report and project index
- `Write` - Create content brainstorm

## Behavior

1. **Validate input**:
   - Check research report exists at `{{path}}`
   - Check report status is `complete`
   - Check content-brainstorm.md doesn't exist (unless `--force`)

2. **Persona verification**: Check for configured persona in project
   - If set, load from `.templates/personas/<slug>.md`
   - Display current persona and prompt for confirmation
   - Allow changing persona if needed

3. **Extract content opportunities** from report:
   - Identify potential tutorials from "how-to" findings
   - Identify deep-dives from complex technical findings
   - Identify experiments from open questions
   - Identify explainers from conceptual findings

4. **Assess feasibility** for each opportunity:
   - Estimate effort required
   - Identify expertise gaps
   - Check scope manageability

5. **Assign default templates** based on content type:
   - `tutorial` → `getting-started.outline.md`
   - `deep-dive` → `algorithm-deep-dive.outline.md`
   - `experiment` → `experiment.outline.md`
   - `explainer` → `first-look.outline.md`

6. **Generate content brainstorm** using `.templates/content-brainstorm.md`

7. **Create bidirectional links**:
   - Set `parent` in brainstorm to relative path to report
   - Add brainstorm to `children` in report frontmatter

8. **Update project status** → `content-planning` in `index.md`

9. **Add to Artifacts table** in `index.md`

10. **Self-review** (feasibility check):
    - Are effort estimates realistic?
    - Are there expertise gaps?
    - Is scope manageable?

## Output

```text
Created content brainstorm: content/_projects/<slug>/content-brainstorm.md

Content opportunities identified:
- Tutorials: {{count}} ({{templates}})
- Deep dives: {{count}} ({{templates}})
- Experiments: {{count}} ({{templates}})
- Explainers: {{count}} ({{templates}})

Total pieces: {{total}}
Recommended sequence: {{count}} ordered items

Self-review: {{passed|warnings}}

Next: Run `/blog/content/plan content/_projects/<slug>/content-brainstorm.md`
      Or: Run `/blog/content/review content/_projects/<slug>/content-brainstorm.md` first
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Report doesn't exist | "Research report not found at {{path}}" | Verify path or run research phase |
| Report status not complete | "Research report status is '{{status}}', expected 'complete'" | Complete research phase first |
| Brainstorm already exists | "Content brainstorm already exists at {{path}}. Use --force to overwrite" | Use --force flag or review existing |
| Persona not found | "Persona '{{slug}}' not found in .templates/personas/" | Create persona or choose different |
| Project index missing | "Project index.md not found. Run /blog/idea/brainstorm first" | Start from ideation phase |

## Example Usage

```text
# From research report
/blog/content/draft content/_projects/kubernetes-migration/research/reports/final.md

# Overwrite existing brainstorm
/blog/content/draft content/_projects/kubernetes-migration/research/reports/final.md --force
```

## Direct Entry

When entering without prior research report (external research):

1. Accept research document path (can be outside project)
2. Create project structure if needed
3. Create minimal `index.md` and `plan.md` as stubs
4. Set project status to `content-planning`
5. Continue with brainstorm creation
