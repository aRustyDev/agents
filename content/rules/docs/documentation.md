---
paths:
  - docs/**
  - "*.md"
---

# Documentation Types

## Where Things Go

| Type | Location | Format | When |
|------|----------|--------|------|
| **User docs** | `docs/src/` | mdBook chapters | Features, guides, reference |
| **ADRs** | `docs/src/adr/` | ADR template | Architecture decisions |
| **Blog/Lessons** | `docs/blog/` | Blog post template | Problems solved, insights |
| **Notes** | `docs/notes/` | Free-form | Scratchpad, research, spikes |

## Output Style by Type

### User Docs (`docs/src/`)
- Written for **end users**
- Task-oriented: "How to X"
- Include code examples with expected output
- Update `SUMMARY.md` when adding pages

### ADRs (`docs/src/adr/`)
- Written for **future maintainers**
- Follow template: Status → Context → Decision → Consequences
- Numbered sequentially: `001-decision-name.md`
- Never delete, only supersede

### Blog/Lessons (`docs/blog/`)
- Written for **future agents and developers**
- Must include: Problem context, Investigation, Solution, Reproduction steps
- Goal: enough context to recreate the problem and understand the fix
- Use `docs/blog/_template.md` as starting point

### Notes (`docs/notes/`)
- Written for **yourself**
- No format requirements
- Ephemeral - can be deleted freely
- Good for research dumps before formalizing

## Brand Assets

- **Source**: `aRustyDev/brand` (serves `brand.arusty.dev`)
- **In production**: Use CDN URLs (`brand.arusty.dev/logos/...`)
- **In development**: Direct file references are fine
- **Assets**: Logos, colors, typography, guidelines
- Use `design-brand-applying-dev` skill when styling artifacts

## Central Documentation

- `aRustyDev/docs` aggregates docs from all repos → `docs.arusty.dev`
- `aRustyDev/blog` serves blog content → `blog.arusty.dev`
