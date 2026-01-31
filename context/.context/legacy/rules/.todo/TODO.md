# TODOs for AI Rules

1. Make rule selection tool for dynamic `.rules` loading based on project type.
   - ex: create different rules for different roles
   - ex: create project specific rules (e.g. how to search code in TF vs Go projects)
2. Rules for [`semantic-release`](https://github.com/semantic-release/semantic-release) usage.
3. Rules for `.editorconfig` generation, enforcement, review, suggestions, etc.
4. Rules for `.gitattributes` generation, enforcement, review, suggestions, etc.
5. Rules for `.gitignore` generation, enforcement, review, suggestions, etc.
6. Rules for `Justfile` generation, enforcement, review, suggestions, etc.
   - ex: when should the agent create a recipe for something?
7. Rules for `Dockerfile` generation, enforcement, review, suggestions, etc.
8. Prompts for Rule Review; Look for conflicts after generation.
9. Tool for `rule` token optimization (should be plain text vs MD)

## Adopt `.ai/checklists/init.project.md` pattern

- Included as part of new project scaffolding.
- If `git config --local project.id` is null, then follow `.ai/checklists/init.project.md`.

### Example `.ai/checklists/init.project.md` snippet

```markdown
- if `.meta.json:id` is present, then set `git config --local project.id` to that value.
  - else set it with `git config --local project.id "$(uuidgen)"` && write to `.meta.json:id`
- setup `tdd-guard`
- setup `pre-commit`
- setup `semantic-release`
- use mustache and templates to generate all required files
- verify required MCP servers are available and configured
- verify XDG pattern enforced/followed
```

## Hooks

- SessionStart:
  - Always begin your chat by saying only "Remembering..." and retrieve all relevant
  - Use `whoami` to identify the current user
    - Create or retrieve user profile from the knowledge graph
  - Query `{PROJECT_ID}::*` entities for context
  - Retrieve both user-specific and project-specific context
- SessionEnd:
  - Add new decisions/learnings as entities to `{PROJECT_ID}::*` for context
