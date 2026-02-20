---
name: seo-for-developers
description: SEO fundamentals for technical blog posts — meta tags, structured data, keyword placement, and readability optimization
created: 2025-02-19
updated: 2025-02-19
tags: [blog, seo, meta-tags, structured-data, technical-writing]
source: blog-workflow-plugin
---

# SEO for Developers

Practical SEO techniques for technical blog posts without compromising content quality.

## Overview

This skill provides actionable SEO guidance specifically for technical content. It focuses on techniques that improve discoverability while maintaining the depth and accuracy that technical readers expect.

**This skill covers:**

- Meta tag optimization (title, description)
- Heading structure for SEO
- Keyword placement strategies
- Structured data for technical content
- Internal linking best practices

**This skill does NOT cover:**

- General marketing SEO tactics
- Link building strategies
- Social media optimization
- Paid promotion

## Quick Reference

### Meta Tag Targets

| Element | Target | Notes |
|---------|--------|-------|
| Title tag | 50-60 chars | Include primary keyword |
| Meta description | 150-160 chars | Call to action or value prop |
| URL slug | 3-5 words | Hyphenated, no stop words |
| H1 | 1 per page | Match or vary title slightly |

### Content Checklist

| Check | Target |
|-------|--------|
| Primary keyword in title | Yes |
| Primary keyword in first 100 words | Yes |
| Keyword in at least one H2 | Yes |
| Internal links | 2-5 per post |
| External links | 1-3 authoritative sources |
| Image alt text | All images |

## Title Tag Optimization

### Structure

```text
[Primary Keyword]: [Benefit/Hook] | [Site Name]
```

**Examples:**

- "Event Sourcing in Python: A Practical Guide | DevBlog"
- "How to Set Up GitHub Actions: CI/CD in 10 Minutes | DevBlog"
- "Understanding WebAssembly: From Browser to Server | DevBlog"

### Guidelines

1. **Front-load keywords** — Put the most important words first
2. **Include benefit** — Why should someone click?
3. **Stay under 60 chars** — Longer titles get truncated
4. **Match search intent** — Use "how to", "guide", or "tutorial" for instructional content

## Meta Description

### Structure

```text
[What the post covers]. [Key benefit or outcome]. [Call to action].
```

**Examples:**

- "Learn how to implement event sourcing in Python with practical code examples. Build an audit log that never loses data. Start building today."
- "Step-by-step guide to GitHub Actions CI/CD. Deploy your code automatically in under 10 minutes. No DevOps experience required."

### Guidelines

1. **150-160 characters** — Longer descriptions get truncated
2. **Include primary keyword** — Helps with relevance
3. **Add a CTA** — "Learn how", "Get started", "See examples"
4. **Unique per page** — Never duplicate descriptions

## Heading Structure

### SEO-Optimized Structure

```markdown
# Primary Keyword: Descriptive Title (H1)

## Introduction keyword phrase (H2)

### Supporting topic (H3)

## Second main keyword variation (H2)

### Supporting topic (H3)

## Conclusion with keyword (H2)
```

### Guidelines

1. **One H1 per page** — Usually the post title
2. **Keywords in H2s** — Natural variations of primary keyword
3. **Logical hierarchy** — H2 > H3 > H4, no skipping levels
4. **Descriptive headings** — Tell readers what's in each section

## Keyword Placement

### Natural Placement Points

| Location | Priority | Notes |
|----------|----------|-------|
| Title (H1) | High | Primary keyword |
| First paragraph | High | Within first 100 words |
| At least one H2 | High | Natural variation |
| URL slug | Medium | Exact or close match |
| Image alt text | Medium | When relevant |
| Throughout body | Low | Natural usage only |

### Keyword Research for Technical Content

Focus on:

1. **Problem-based queries** — "how to debug memory leaks"
2. **Comparison queries** — "postgres vs mysql for..."
3. **Tutorial queries** — "python websocket tutorial"
4. **Version-specific** — "react 18 server components guide"

### Avoid

- Keyword stuffing (unnatural repetition)
- Exact match in every heading
- Forced keyword placement that hurts readability

## Structured Data

### Article Schema

Add to post frontmatter or page template:

```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Post Title",
  "description": "Meta description",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2025-02-19",
  "dateModified": "2025-02-19",
  "publisher": {
    "@type": "Organization",
    "name": "Site Name"
  }
}
```

### HowTo Schema (for tutorials)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [Do Something]",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step 1 title",
      "text": "Step 1 description"
    }
  ]
}
```

## Internal Linking

### Best Practices

1. **Link to related posts** — 2-5 internal links per post
2. **Use descriptive anchor text** — "learn about event sourcing" not "click here"
3. **Link early** — Important links in first half of post
4. **Create content clusters** — Group related posts with cross-links

### Link Placement

```markdown
For more on this topic, see our [guide to event sourcing](/posts/event-sourcing-guide).

As we covered in the [previous tutorial](/posts/python-basics), ...

Related: [Understanding CQRS](/posts/cqrs-explained)
```

## Image Optimization

### Alt Text Guidelines

- **Describe the image** — What does it show?
- **Include context** — How does it relate to the content?
- **Keep it concise** — Under 125 characters
- **Include keywords** — When natural and relevant

**Examples:**

- "Diagram showing event sourcing data flow from command to event store"
- "Terminal output of successful pytest run with 15 passing tests"
- "Architecture diagram comparing monolith vs microservices"

### File Naming

```text
event-sourcing-architecture-diagram.png
github-actions-workflow-screenshot.png
performance-comparison-chart.png
```

## URL Structure

### Guidelines

```text
/blog/event-sourcing-python/
/tutorials/github-actions-setup/
/deep-dives/webassembly-explained/
```

1. **Short and descriptive** — 3-5 words
2. **Use hyphens** — Not underscores
3. **Include keyword** — Primary keyword in URL
4. **No dates** — Unless content is time-sensitive
5. **Lowercase** — Consistent casing

## Common Mistakes

### Over-Optimization

- Keyword density targets (outdated)
- Exact match keywords everywhere
- Sacrificing readability for SEO

### Under-Optimization

- Missing meta descriptions
- Generic titles ("Post 1")
- No internal links
- Missing alt text on images

### Technical Issues

- Duplicate content across URLs
- Missing canonical tags
- Slow page load (affects rankings)
- Non-mobile-friendly layout

## See Also

- `technical-writing-style` skill - Writing quality content
- `/seo-pass` command - Apply SEO optimization to drafts
- `seo-specialist` agent - Full SEO analysis
