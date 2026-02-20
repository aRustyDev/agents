---
description: Apply SEO optimization to a blog post draft
argument-hint: <draft-file> [--keywords "keyword1, keyword2"]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# SEO Pass

Apply SEO best practices to a blog post draft.

## Arguments

- `$1` - Path to draft file. Example: `posts/_drafts/event-sourcing.md`
- `--keywords` - Target keywords (optional, will infer from content if not provided)

## Output

Updates the draft file in place with SEO optimizations.

## Workflow

### Step 1: Analyze Current State

Read the draft and assess:

| Element | Current State |
|---------|---------------|
| Title length | X chars |
| Description | present/missing |
| H1 | keyword present? |
| First 100 words | keyword present? |
| H2 structure | keyword variations? |
| Internal links | count |
| Image alt text | complete? |

### Step 2: Identify Keywords

If `--keywords` not provided:

1. Extract topic from title and content
2. Identify primary keyword (main topic)
3. Identify secondary keywords (related terms)

### Step 3: Apply Optimizations

#### Title Tag

Current: `[current title]`
Optimized: `[Primary Keyword]: [Benefit] | [Site]`

- [ ] Under 60 characters
- [ ] Primary keyword at start
- [ ] Includes benefit or hook

#### Meta Description

Current: `[current or missing]`
Optimized: `[What post covers]. [Key benefit]. [CTA]`

- [ ] 150-160 characters
- [ ] Primary keyword included
- [ ] Call to action present

#### Heading Structure

| Heading | Contains Keyword | Recommendation |
|---------|------------------|----------------|
| H1 | yes/no | [suggestion] |
| H2 #1 | yes/no | [suggestion] |
| H2 #2 | yes/no | [suggestion] |

#### Content Optimization

- First 100 words: [add keyword naturally if missing]
- Keyword density: [current %] → [target ~1-2%]
- Internal links: [add N links to related content]

#### Images

| Image | Alt Text Status | Suggestion |
|-------|-----------------|------------|
| image1.png | missing | [suggested alt] |
| diagram.png | generic | [improved alt] |

### Step 4: Update Draft

Apply optimizations:

1. Update frontmatter (title, description)
2. Adjust headings if needed
3. Add keyword to first paragraph if missing
4. Add internal links
5. Update image alt text

### Step 5: Report

```text
## SEO Pass Complete

| Element | Before | After |
|---------|--------|-------|
| Title | X chars | Y chars |
| Description | missing | added |
| H1 keyword | no | yes |
| First 100 words | no keyword | added |
| Internal links | 0 | 3 |
| Alt text | 1/3 | 3/3 |

**Primary keyword**: [keyword]
**Secondary keywords**: [keywords]

**Additional recommendations**:
- [Manual improvement 1]
- [Manual improvement 2]
```

## Examples

```text
/seo-pass posts/_drafts/event-sourcing.md
/seo-pass posts/_drafts/ci-cd-guide.md --keywords "github actions, ci/cd, automation"
```

## SEO Checklist (Applied)

- [ ] Title under 60 chars with keyword
- [ ] Description 150-160 chars with CTA
- [ ] Keyword in H1
- [ ] Keyword in first 100 words
- [ ] Keyword variation in at least one H2
- [ ] 2-5 internal links
- [ ] All images have descriptive alt text
- [ ] URL is short and includes keyword

## See Also

- `seo-for-developers` skill - Full SEO guidelines
- `/publish-prep` command - Final validation before publishing
