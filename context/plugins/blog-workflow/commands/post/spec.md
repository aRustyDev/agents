---
name: blog/post/spec
description: Create post specification from phase file
arguments:
  - name: path
    description: Path to the phase file
    required: true
  - name: force
    description: Overwrite existing spec
    required: false
---

# Post Spec Command

Create a post specification from a phase file. The spec defines the target audience, key takeaways, prerequisites, and scope for a single post.

## Tools

- `Read` - Load phase file, research, project index
- `Write` - Create spec
- `Bash` - Create directories

## Behavior

1. **Validate input**:
   - Check phase file exists at `{{path}}`
   - Check phase status is `draft` or `approved`
   - Check spec doesn't exist (unless `--force`)

2. **Persona verification**:
   - Check for configured persona in phase or project
   - If set, load from `.templates/personas/<slug>.md`
   - Display current persona and prompt for confirmation
   - Allow changing persona if needed

3. **Extract post requirements** from phase:
   - Title and summary
   - Key points
   - Code example needs
   - Related research
   - Template preference

4. **Generate spec** using `.templates/post-spec.md`:
   - Define target audience from phase
   - List 3-5 key takeaways
   - Identify prerequisites
   - Specify code examples needed
   - Estimate word count based on content type

5. **Create post directory**: `post/<phase-slug>/`

6. **Write spec**: `post/<phase-slug>/spec.md`

7. **Create bidirectional links**:
   - Set `parent` in spec to relative path to phase file
   - Add spec to `children` in phase file

8. **Update project status** -> `post` in `index.md`

9. **Add to Post Artifacts table** in `index.md`

10. **Self-review** (completeness check):
    - Are takeaways concrete?
    - Are prerequisites clear?
    - Is scope achievable?

## Output

```text
Created post spec: content/_projects/<slug>/post/<phase-slug>/spec.md

Post: {{title}}
Persona: {{persona}}
Template: {{template}}.outline.md
Target: ~{{words}} words (~{{minutes}} min read)

Takeaways: {{count}}
Prerequisites: {{count}}
Code examples: {{count}}

Self-review: {{passed|warnings}}

Next: Run `/blog/post/plan content/_projects/<slug>/post/<phase-slug>/spec.md`
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Phase file doesn't exist | "Phase file not found at {{path}}" | Verify path or run content planning |
| Phase status is complete | "Phase '{{slug}}' already has a complete post" | Check post/ directory |
| Spec already exists | "Spec already exists at post/{{slug}}/spec.md. Use --force to overwrite" | Use --force flag |
| Persona not found | "Persona '{{slug}}' not found in .templates/personas/" | Create persona or select different |
| Template not found | "Outline template '{{slug}}' not found in .templates/outlines/" | Check available templates |
| Project index missing | "Project index.md not found" | Verify project structure |

## Example Usage

```text
# From phase file
/blog/post/spec content/_projects/kubernetes-migration/phase/0-tutorial-basics.md

# Overwrite existing spec
/blog/post/spec content/_projects/kubernetes-migration/phase/0-tutorial-basics.md --force
```

## Direct Entry

When entering without a phase file:

1. Prompt for post topic and type
2. Create minimal project structure if needed
3. Create synthetic phase file with provided details
4. Continue with spec creation
