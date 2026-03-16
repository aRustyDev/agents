# Review Checklists

Quality gates between workflow phases ensure content meets standards before proceeding.

## Checklist Purpose

- **Consistency**: Same criteria applied to all content
- **Completeness**: Nothing important is missed
- **Quality**: Catch issues early
- **Guidance**: Clear expectations for each phase

## Phase Checklists

### Idea Review Checklist

Before proceeding from idea to research:

- [ ] Topic is clearly defined and scoped
- [ ] Target audience is identified
- [ ] Post type is selected and appropriate
- [ ] Unique angle or perspective is clear
- [ ] Not duplicating existing content
- [ ] Feasible to research and write
- [ ] Aligns with blog goals/themes

### Research Review Checklist

Before proceeding from research to content planning:

- [ ] Research questions are answered
- [ ] Sources are credible and cited
- [ ] Multiple perspectives considered
- [ ] Gaps identified and acknowledged
- [ ] Key findings summarized
- [ ] Sufficient depth for post type
- [ ] No major contradictions unresolved

### Content Review Checklist

Before proceeding from planning to drafting:

- [ ] Outline covers all key points
- [ ] Logical flow from section to section
- [ ] Introduction hooks the reader
- [ ] Conclusion provides closure
- [ ] Appropriate depth per section
- [ ] No obvious gaps
- [ ] Matches selected post type structure

### Post Review Checklist

Before proceeding to publish phase:

- [ ] Title is compelling and accurate
- [ ] Introduction engages quickly
- [ ] Content matches outline
- [ ] Code examples are tested and work
- [ ] Images/diagrams are clear
- [ ] Voice is consistent throughout
- [ ] No unfinished sections (TODO, TBD)
- [ ] Proofread for grammar/spelling
- [ ] Technical accuracy verified
- [ ] Links work and are relevant

### SEO Review Checklist

Before publishing:

- [ ] Title under 60 characters
- [ ] Meta description 150-160 characters
- [ ] Focus keyword in title and H1
- [ ] Keyword in first paragraph
- [ ] Headings use appropriate hierarchy
- [ ] Images have alt text
- [ ] Internal links to related content
- [ ] External links to authoritative sources
- [ ] URL slug is readable and keyword-rich
- [ ] Open Graph image is set

### Pre-Publish Checklist

Final checks before publish:

- [ ] Frontmatter is complete and valid
- [ ] Date is correct
- [ ] Author is set
- [ ] Tags are appropriate
- [ ] Draft flag is false (or ready to be)
- [ ] No broken internal links
- [ ] Build succeeds locally
- [ ] Renders correctly in preview
- [ ] Series membership is correct (if applicable)
- [ ] Relationships are set (if applicable)

## Using Checklists

### Via Commands

Each review command applies the relevant checklist:

```bash
/blog/idea/review content/_projects/<name>/idea.md
# Applies idea review checklist

/blog/post/review content/_projects/<name>/drafts/v1.md
# Applies post review checklist
```

### Checklist Output

Reviews produce structured feedback:

```markdown
## Review: idea.md

### Passed

- [x] Topic is clearly defined
- [x] Target audience identified
- [x] Post type selected

### Failed

- [ ] Unique angle not clear
  - Suggestion: What makes this different from existing tutorials?

### Warnings

- [ ] Scope may be too broad
  - Consider: Focus on ownership only, defer lifetimes to part 2

### Verdict: Needs Revision

Address failed items before proceeding.
```

## Customizing Checklists

### Project-Level Override

Create custom checklists in your project:

```text
content/_templates/review-checklists/
└── my-custom-checklist.md
```

### Checklist Template Format

```markdown
---
name: custom-post-review
phase: post
---

# Custom Post Review

## Required

- [ ] Item 1
- [ ] Item 2

## Recommended

- [ ] Item 3

## Optional

- [ ] Item 4
```

### Item Categories

| Category | Meaning |
|----------|---------|
| Required | Must pass to proceed |
| Recommended | Should pass, but can proceed with justification |
| Optional | Nice to have |

## Type-Specific Additions

Some post types have additional checklist items:

### Tutorial Additions

- [ ] Prerequisites are listed
- [ ] Learning objectives are stated
- [ ] Steps are numbered and clear
- [ ] Expected outcomes are shown

### Research Additions

- [ ] Methodology is described
- [ ] Data is presented clearly
- [ ] Conclusions follow from data
- [ ] Limitations are acknowledged

### Review Additions

- [ ] Criteria are explicit
- [ ] Both pros and cons included
- [ ] Rating is justified
- [ ] Recommendation is clear

See [Review Fields Reference](../reference/review-fields.md) for type-specific requirements.
