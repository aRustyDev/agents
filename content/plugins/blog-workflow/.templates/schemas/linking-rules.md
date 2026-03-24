# Linking Rules

## Bidirectional Links

- `parent` and `children` are ALWAYS bidirectional
- When adding a parent link, update the parent's children array
- When adding a child link, update the child's parent field

## Cross-Project Links

| From | To | Link Format |
|------|-----|-------------|
| Phase file | Child project | `children: [content/_projects/<child-slug>/index.md]` |
| Child index | Parent phase | `parent: content/_projects/<parent-slug>/phase/<N>-<slug>.md` |

## Path Conventions

- **Within project**: Use relative paths (`./idea.md`, `./phase/0-tutorial.md`)
- **Cross-project**: Use paths from `content/` root (`content/_projects/<slug>/index.md`)

## Rules

1. Projects are ALWAYS flat at `content/_projects/` — never nested in each other
2. Child projects are peers, not subdirectories
3. Graph relationships live in frontmatter, not directory structure
