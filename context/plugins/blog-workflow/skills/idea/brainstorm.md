---
name: blog:idea:brainstorm
description: Transform a raw concept into a structured idea artifact with project scaffolding
arguments:
  - name: concept
    description: The topic or concept to brainstorm
    required: true
---

# Idea Brainstorm

Transform a raw concept into a structured idea artifact, creating the project scaffolding for the blog workflow.

## Behavior

1. **Generate slug** from concept:
   - Lowercase the concept
   - Replace spaces and special characters with hyphens
   - Remove consecutive hyphens
   - Truncate to 50 characters
   - If `content/_projects/<slug>/` exists, append `-2`, `-3`, etc.

2. **Check persona awareness**:
   - Look for `persona` field in any existing project config
   - If no persona configured, inform user: "No persona configured. Content will use default voice. Use `blog:persona:draft` to create one."

3. **Create project directory**: `content/_projects/<slug>/`

4. **Generate artifacts**:
   - `idea.md` from `.templates/idea.md` with:
     - `id`: Generate UUIDv4
     - `type`: "idea"
     - `status`: "draft"
     - `created`/`updated`: Current ISO 8601 timestamp
     - Fill sections based on user's concept
   - `index.md` from `.templates/project-index.md` with:
     - `type`: "project"
     - `status`: "ideation"
     - Add idea to Artifacts table
   - `README.md` from `.templates/project-readme.md`

5. **Run self-review** per `rules/blog-self-review.md`:
   - Check against `.templates/review-checklists/idea.md`
   - Only report **fail** items (warn items left for explicit review)
   - If any fail items: report issues, keep status as `draft`

## Output

Report the created project structure:

```text
Created project: content/_projects/<slug>/
  - idea.md (status: draft)
  - index.md
  - README.md

Self-review: [passed | X issues found]
```

## Example

**Input**: `blog:idea:brainstorm "Building eBPF tracing tools for production debugging"`

**Output**:

```text
Created project: content/_projects/building-ebpf-tracing-tools/
  - idea.md (status: draft)
  - index.md
  - README.md

Self-review: passed

Next steps:
1. Review the idea: blog:idea:review content/_projects/building-ebpf-tracing-tools/idea.md
2. Refine if needed: blog:idea:refine <path> "feedback"
3. Create plan when approved: blog:idea:draft-plan <path>
```
