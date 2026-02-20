# Plugin Brainstorm: blog-workflow

## Domain & Purpose

**Domain**: Technical content creation
**Purpose**: Structured workflow for creating technical blog posts from research through publication, with consistent formatting and quality validation.

## Use Cases

1. **Technical tutorials** - Step-by-step guides, how-tos, implementation walkthroughs
2. **Analysis & deep dives** - In-depth analysis of tools, patterns, architectures
3. **Research summaries** - Synthesizing research findings, literature reviews
4. **Development journals** - Project updates, lessons learned, build logs
5. **Multi-part series** - Connected content like "Context Engineering" series

### Example Posts

- "Agent Development Done Right: A Workflow Approach"
- "Deep Dive into LLM Observability"
- "A Series on Claude Plugin Development"
- "Context Engineering: Memories v Knowledge"
- "Context Engineering: Recall v RAG"
- "Deep Dive into Git Internals"
- "Learn with Me as I Explore Kernel Development"

## Components

### Skills

| Name | Purpose | Priority |
|------|---------|----------|
| technical-writing-style | Voice, tone, clarity patterns for dev content | must |
| seo-for-developers | Technical SEO without marketing fluff | should |
| content-structure-patterns | Templates for tutorials, analyses, series | must |
| code-example-best-practices | How to present code, snippets, examples effectively | must |

### Commands

| Name | Purpose | Priority |
|------|---------|----------|
| /research-topic | Gather sources, synthesize background for a topic | must |
| /refine-research-plan | Iterate on research direction and scope | should |
| /gather-resources | Find repos or external resources to link/reference | should |
| /outline-post | Generate structured outline from research/notes | must |
| /draft-post | Write full draft from outline | must |
| /seo-pass | Optimize title, headings, meta description | should |
| /publish-prep | Final validation, frontmatter, formatting check | must |
| /series-plan | Plan multi-part series structure and linking | should |

### Agents

| Name | Purpose | Priority |
|------|---------|----------|
| research-synthesizer | Gather, analyze, and synthesize research into usable notes | must |
| technical-editor | Review drafts for clarity, accuracy, and style | should |
| series-architect | Plan and maintain coherence across multi-part series | nice |

### Output Styles

| Name | Purpose | Priority |
|------|---------|----------|
| tutorial-format | Step-by-step with prerequisites, code blocks, outcomes | must |
| deep-dive-format | Analysis structure with context, exploration, insights | must |
| research-summary-format | Findings-focused with methodology, results, implications | should |
| dev-journal-format | Chronological with learnings, blockers, next steps | should |

### Hooks

| Name | Purpose | Priority |
|------|---------|----------|
| frontmatter-validator | Check required fields: title, date, tags, description | must |
| link-checker | Validate internal/external links are accessible | should |
| code-block-linter | Ensure code blocks have language tags, valid syntax | should |

### MCP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| - | No CMS integrations needed (local markdown) | - |

### LSP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| - | No custom LSP needed | - |

## Summary

| Category | Must | Should | Nice | Total |
|----------|------|--------|------|-------|
| Skills   | 3    | 1      | 0    | 4     |
| Commands | 4    | 4      | 0    | 8     |
| Agents   | 1    | 1      | 1    | 3     |
| Styles   | 2    | 2      | 0    | 4     |
| Hooks    | 1    | 2      | 0    | 3     |
| MCP      | 0    | 0      | 0    | 0     |
| LSP      | 0    | 0      | 0    | 0     |
| **Total**| 11   | 10     | 1    | 22    |
