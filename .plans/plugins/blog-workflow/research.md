# Plugin Research: blog-workflow

## Existing Plugins

| Plugin | Domain | Coverage | Recommendation |
|--------|--------|----------|----------------|
| content-creation | General content | ~20% | reference (empty scaffold) |

## Component Research

### Skills

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| technical-writing-style | - | - | 0% | create |
| seo-for-developers | - | - | 0% | create |
| content-structure-patterns | - | - | 0% | create |
| code-example-best-practices | - | - | 0% | create |

### Commands

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| /research-topic | - | - | 0% | create |
| /refine-research-plan | - | - | 0% | create |
| /gather-resources | - | - | 0% | create |
| /outline-post | - | - | 0% | create |
| /draft-post | - | - | 0% | create |
| /seo-pass | - | - | 0% | create |
| /publish-prep | - | - | 0% | create |
| /series-plan | - | - | 0% | create |

### Agents

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| research-synthesizer | research-analyst | context/agents/ | 70% | extend |
| technical-editor | technical-writer | context/agents/ | 60% | extend |
| series-architect | - | - | 0% | create |

### Output Styles

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| tutorial-format | - | - | 0% | create |
| deep-dive-format | - | - | 0% | create |
| research-summary-format | - | - | 0% | create |
| dev-journal-format | - | - | 0% | create |

### Hooks

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| frontmatter-validator | - | - | 0% | create |
| link-checker | lychee (pre-commit) | .pre-commit-config.yaml | 80% | reuse/adapt |
| code-block-linter | - | - | 0% | create |

### MCP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| - | - | - | - | - |

### LSP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| - | - | - | - | - |

## Key Findings

### Reusable Agents

1. **research-analyst** (70% coverage for research-synthesizer)
   - Strong methodology for information gathering
   - Source evaluation and synthesis
   - Gap: Not specialized for blog research workflow

2. **technical-writer** (60% coverage for technical-editor)
   - Comprehensive writing standards
   - SEO awareness
   - Gap: Not focused on blog editing specifically

3. **seo-specialist** (useful reference for /seo-pass)
   - Full SEO workflow
   - Technical and content optimization
   - Can inform skill and command design

### Pre-commit Integration

- **lychee** already validates links in markdown files
- Can be adapted as a hook for blog posts specifically

## Summary

- **Reuse**: 1 component (lychee for link checking)
- **Extend**: 2 components (research-analyst → research-synthesizer, technical-writer → technical-editor)
- **Create**: 19 components

Total effort reduction: ~15% from extending existing agents
