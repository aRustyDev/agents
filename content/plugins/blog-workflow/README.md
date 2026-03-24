# Blog Workflow Plugin

Multi-phase blog content creation with personas, templates, and iterative review.

## Installation

```bash
claude plugin install blog-workflow
```

## Quick Start

1. Initialize the workflow in your project:

   ```text
   /blog/init
   ```

2. Start with an idea:

   ```text
   /blog/idea/brainstorm "Your topic here"
   ```

3. Review and refine:

   ```text
   /blog/idea/review content/_projects/<slug>/idea.md
   ```

4. Continue through phases: research -> content -> post -> publish

## Commands

### Initialization

| Command | Purpose |
|---------|---------|
| `/blog/init` | Set up directories and copy templates |
| `/blog/init --with-hooks` | Also configure validation hooks |

### Ideation (`/blog/idea/*`)

| Command | Purpose |
|---------|---------|
| `brainstorm` | Start a new idea from raw concept |
| `review` | Evaluate idea or plan |
| `refine` | Improve based on feedback |
| `draft-plan` | Create project plan from approved idea |

### Research (`/blog/research/*`)

| Command | Purpose |
|---------|---------|
| `spec/draft` | Create research plan |
| `spec/plan` | Refine research plan |
| `spec/review` | Evaluate research plan |
| `draft` | Execute research |
| `plan` | Create analysis from findings |
| `refine` | Update research artifacts |
| `review` | Evaluate analysis + compile report |

### Content Planning (`/blog/content/*`)

| Command | Purpose |
|---------|---------|
| `draft` | Brainstorm content pieces |
| `plan` | Decompose into phases |
| `refine` | Update content plan |
| `review` | Validate decomposition |

### Post Writing (`/blog/post/*`)

| Command | Purpose |
|---------|---------|
| `spec` | Create post specification |
| `plan` | Create outline from spec |
| `draft` | Write full draft |
| `refine` | Update post artifacts |
| `review` | Evaluate draft quality |

### Publishing (`/blog/publish/*`)

| Command | Purpose |
|---------|---------|
| `seo-review` | Optimize for search |
| `pre-check` | Validate before publish |
| `promote` | Move to live location |
| `validate` | Verify build success |

### Meta Commands

| Command | Purpose |
|---------|---------|
| `/blog/persona/*` | Manage authorial personas |
| `/blog/template/*` | Manage structural templates |

## Configuration

The plugin expects these directories in your project:

- `content/_projects/` - Project files
- `content/_drafts/` - Post drafts
- `content/_templates/` - Personas, outlines, checklists

Run `/blog/init` to create this structure automatically.

## Personas

Define authorial voice in `content/_templates/personas/<name>.md`.
Two personas included by default: `practitioner.md` and `educator.md`.

## Templates

Outline templates in `content/_templates/outlines/` define post structure.
18 templates included covering tutorials, deep-dives, experiments, and more.

## Hooks

The plugin includes validation hooks:

- **validate-blog-frontmatter.sh** - Validates artifact frontmatter on save
- **promote-safety.sh** - Prevents accidental writes to `src/data/blog/`

Customize by copying to `.claude/hooks/` in your project.

## Migration from v1.x

| Old Command | New Command |
|-------------|-------------|
| `draft-post` | `/blog/post/draft` |
| `gather-resources` | `/blog/research/draft` |
| `outline-post` | `/blog/post/plan` |
| `publish-prep` | `/blog/publish/pre-check` |
| `research-topic` | `/blog/research/draft` |
| `seo-pass` | `/blog/publish/seo-review` |

Legacy commands remain in v2.0.0 with deprecation notices.
