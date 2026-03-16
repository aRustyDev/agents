# 2. Post Type Taxonomy Design

Date: 2026-03-16

## Status

Accepted

## Context

The blog-workflow plugin needed a systematic way to classify blog posts. Without clear post types, content becomes inconsistent in structure, voice, and reader expectations. Users asked questions like "what kind of post should this be?" without clear guidance.

Key requirements identified:

- Cover common technical blog content patterns
- Distinguish by purpose, voice, and structure
- Support progressive complexity (tutorials vs deep dives)
- Handle temporal relationships (planning → retrospective)
- Allow living documents vs static snapshots

## Decision

We adopt a **19-type taxonomy** organized across multiple dimensions:

### Post Types

1. **Tutorial** - Authoritative teaching
2. **Walk-through** - Exploratory process documentation
3. **Deep Dive** - Industry-oriented technical depth
4. **Research** - Academic-style investigation
5. **Study Review** - Learning reflection
6. **Review** - External evaluation (with subtypes)
7. **Comparison** - Side-by-side analysis
8. **Problems** - Issue crystallization
9. **Open Questions** - Possibility exploration
10. **Planning** - Pre-work goal setting
11. **Retrospective** - Post-work reflection
12. **Updates** - Progress narrative
13. **Opinions** - Personal perspective
14. **Dev Blog** - Evergreen practitioner wisdom
15. **Announcement** - Declaration
16. **Reference** - Curated collection
17. **ELI5** - Simplified explanation
18. **5 Levels** - Progressive complexity explanation

### Dimensions

- **Formality** (1-4): Casual → Structured → Formal → Academic
- **Complexity** (1-5): Accessible → Introductory → Intermediate → Advanced → Expert
- **Temporality**: Before, During, After, Atemporal, Point-in-time
- **Living**: Per-post toggle for maintained documents

### Relationships

Posts connect via explicit frontmatter relationships:

- `series` - Ordered sequence membership
- `project-arc` - Planning → Updates → Retrospective
- `responds-to` - Response to another post
- `supersedes` / `superseded-by` - Replacement relationship
- `see-also` - Curated related content

### Series as First-Class Entity

Series exist independently in `content/_series/` with their own metadata. Posts declare membership; the build system aggregates.

### Review Subtypes

Reviews use a hybrid approach:

- Built-in subtypes: course, tool, library, book, policy
- Custom subtypes in `content/_templates/reviews/`
- Universal fields + subtype-specific fields

## Consequences

### Easier

- **Choosing post type**: Decision tree guides selection
- **Consistent structure**: Templates per type
- **Reader expectations**: Clear type signals format
- **Living documents**: Explicit support for maintained content
- **Series navigation**: Built-in part ordering
- **Content relationships**: Explicit linking between posts

### More Difficult

- **Learning curve**: 19 types + dimensions to understand
- **Template maintenance**: More templates to maintain
- **Edge cases**: Some content may not fit cleanly
- **Validation complexity**: More fields to validate
- **Migration**: Existing posts need type assignment

### Mitigations

- Decision tree and type guide documentation
- Sensible defaults (formality: 2, complexity: 2)
- Allow untyped posts during migration
- Clear "when to use" guidance per type
