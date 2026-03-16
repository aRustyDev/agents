# Blog Workflow Concepts

The blog-workflow plugin provides a structured approach to creating, organizing, and publishing blog content. This document introduces the core concepts.

## Overview

```text
                    ┌─────────────┐
                    │   Idea      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Research   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Content   │
                    │   Planning  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Post     │
                    │   Writing   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Publish   │
                    └─────────────┘
```

## Core Concepts

### Project

A **project** is the internal workspace for developing one or more blog posts. Projects track:

- Ideas and brainstorming
- Research artifacts
- Draft iterations
- Review feedback

Projects live in `content/_projects/<name>/` and are separate from the published content.

### Post Type

Every post has a **type** that determines its structure, voice, and purpose. There are 19 post types including Tutorial, Deep Dive, Review, and Walk-through. See [Post Types](./taxonomy/post/types.md).

### Series

A **series** is an ordered collection of related posts. Series are reader-facing and exist independently of the projects that produce them. See [Series](./taxonomy/series.md).

### Persona

A **persona** defines writing style and voice characteristics. Personas help maintain consistency across posts. Default personas include Practitioner and Educator.

### Template

**Templates** provide starting structures for different content types:

- Outline templates (18 types)
- Research plan templates
- Review checklists
- Post specifications

### Relationships

Posts connect through **relationships**:

- Series membership
- Project lifecycle (Planning → Updates → Retrospective)
- Response chains (responds-to, supersedes)
- Curated links (see-also)

### Dimensions

Posts vary along several **dimensions**:

- **Formality**: Casual → Academic
- **Complexity**: Accessible → Expert
- **Temporality**: Before, during, or after work
- **Living**: Static snapshot vs maintained over time

---

## Workflow Phases

### 1. Idea Phase

Transform raw concepts into structured ideas.

Commands: `/blog/idea/brainstorm`, `/blog/idea/review`, `/blog/idea/refine`

Outputs:

- Idea artifact with scope, audience, and approach
- Initial project structure

### 2. Research Phase

Gather and synthesize information.

Commands: `/blog/research/spec/*`, `/blog/research/draft`, `/blog/research/review`

Outputs:

- Research plan
- Source collection
- Research synthesis

### 3. Content Planning Phase

Structure the content.

Commands: `/blog/content/draft`, `/blog/content/plan`, `/blog/content/review`

Outputs:

- Content outline
- Section breakdown
- Key points per section

### 4. Post Writing Phase

Write and refine the post.

Commands: `/blog/post/spec`, `/blog/post/draft`, `/blog/post/review`, `/blog/post/refine`

Outputs:

- Post draft
- Review feedback
- Final draft

### 5. Publish Phase

Prepare and publish.

Commands: `/blog/publish/seo-review`, `/blog/publish/pre-check`, `/blog/publish/promote`, `/blog/publish/validate`

Outputs:

- SEO-optimized post
- Published post
- Build validation

---

## Directory Structure

```text
content/
├── _projects/              # Development workspaces
│   └── <project-name>/
│       ├── index.md        # Project metadata
│       ├── idea.md         # Idea artifact
│       ├── research/       # Research artifacts
│       └── drafts/         # Post drafts
│
├── _drafts/                # Ready-for-publish drafts
│   └── <slug>.md
│
├── _series/                # Series definitions
│   └── <series-name>/
│       └── index.md
│
└── _templates/             # Project-local templates
    ├── personas/
    ├── outlines/
    ├── research-plans/
    └── review-checklists/

src/data/blog/              # Published posts (Astro)
└── <slug>.md
```

---

## Getting Started

1. **Initialize** the workflow in your project:

   ```text
   /blog/init
   ```

2. **Start with an idea**:

   ```text
   /blog/idea/brainstorm "Understanding Rust ownership"
   ```

3. **Follow the phases** through research, planning, writing, and publishing.

4. **Use templates** for consistency and completeness.

---

## Concept Deep Dives

- [Post Types](./taxonomy/post/types.md) - All 19 types explained
- [Dimensions](./taxonomy/dimensions.md) - Formality, complexity, temporality
- [Relationships](./taxonomy/relationships.md) - How posts connect
- [Series](./taxonomy/series.md) - Multi-part content
- [Frontmatter Schema](./taxonomy/schema.md) - Complete field reference

## Workflow Details

- [Choosing a Post Type](./workflow/choosing-type.md)
- [Project Lifecycle](./workflow/project-lifecycle.md)
- [Review Checklists](./workflow/review-checklists.md)
- [Publishing Process](./workflow/publishing.md)
