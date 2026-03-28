---
name: technical-writing-style
description: Style guide for technical blog posts covering voice, tone, clarity, and consistency standards
created: 2025-02-19
updated: 2025-02-19
tags: [blog, writing, style-guide, technical-writing]
source: blog-workflow-plugin
---

# Technical Writing Style Guide

Style and voice guidelines for creating clear, engaging technical blog content.

## Overview

This skill provides standards for technical blog writing that balances accessibility with technical depth. It covers voice, tone, sentence structure, and language choices that make technical content engaging and easy to follow.

**This skill covers:**

- Voice and tone standards for technical content
- Sentence structure and clarity guidelines
- Terminology consistency practices
- Reader engagement techniques

**This skill does NOT cover:**

- Content structure and organization (see content-structure-patterns)
- Code example formatting (see code-example-best-practices)
- SEO optimization

## Quick Reference

### Voice Guidelines

| Principle | Do | Don't |
|-----------|-----|-------|
| Active voice | "Run the command" | "The command should be run" |
| Direct address | "You can configure..." | "One can configure..." |
| Present tense | "This function returns..." | "This function will return..." |
| Confident tone | "Use X for Y" | "You might want to use X" |

### Clarity Checklist

| Check | Target |
|-------|--------|
| Sentence length | Under 25 words |
| Paragraph length | 3-4 sentences |
| Jargon ratio | Define or avoid 80%+ |
| Passive voice | Less than 10% |

## Principles

### 1. Write for Scanners First

Technical readers scan before reading. Support this:

- Use descriptive headings that convey meaning
- Lead paragraphs with the key point
- Use bullet points for lists of 3+ items
- Bold key terms on first introduction

### 2. One Idea Per Paragraph

Each paragraph should:

- Start with a topic sentence
- Support that single idea
- Transition smoothly to the next

**Example:**

> Caching reduces database load by storing frequently accessed data in memory. When a request arrives, the cache checks for existing data before querying the database. This simple pattern can reduce response times by 90% for read-heavy workloads.

### 3. Explain, Then Show

Follow this pattern:

1. State what something does
2. Explain why it matters
3. Show how to use it

**Example:**

> Environment variables separate configuration from code. This lets you deploy the same application to different environments without code changes. Set them in your shell:
>
> ```bash
> export DATABASE_URL="postgres://..."
> ```

### 4. Respect Reader Time

- Get to the point quickly
- Cut filler words ("basically", "actually", "just")
- Remove redundant phrases ("in order to" → "to")
- Use concrete words over abstract ones

## Tone Guidelines

### Technical but Accessible

Write as a knowledgeable peer, not a textbook:

| Textbook | Peer |
|----------|------|
| "It is necessary to initialize the configuration prior to execution" | "Initialize the config before running" |
| "The aforementioned methodology" | "This approach" |
| "Utilize" | "Use" |

### Confident but Humble

- Be direct about what works
- Acknowledge trade-offs and alternatives
- Admit when something is complex
- Avoid oversimplifying difficult concepts

### Engaging but Professional

- Use "you" to address the reader
- Vary sentence structure
- Include occasional personality, but prioritize clarity
- Avoid jokes that might confuse non-native speakers

## Common Issues

### Hedging Language

**Problem:** Excessive hedging weakens authority.

| Weak | Strong |
|------|--------|
| "You might want to consider using..." | "Use..." |
| "It's probably a good idea to..." | "..." (just state it) |
| "This could potentially cause..." | "This causes..." |

**When hedging IS appropriate:**

- Genuinely uncertain outcomes
- Multiple valid approaches
- Environment-specific behavior

### Jargon Without Context

**Problem:** Assumes knowledge readers may not have.

**Solution:** Define on first use or link to explanation:

> GraphQL uses **resolvers**—functions that fetch the data for each field in your schema.

### Passive Voice Overuse

**Problem:** Obscures who does what.

| Passive | Active |
|---------|--------|
| "The error is thrown when..." | "The function throws an error when..." |
| "Configuration must be provided" | "You must provide configuration" |
| "The file is read by the parser" | "The parser reads the file" |

## Formatting Standards

### Headings

- Use sentence case: "Setting up authentication"
- Be specific: "Configuring Redis" > "Configuration"
- Limit nesting to 3 levels (H2, H3, H4)

### Lists

- Use bullets for unordered items
- Use numbers for sequences or rankings
- Start each item with the same part of speech
- Keep items parallel in structure

### Emphasis

- **Bold** for key terms on first introduction
- `code` for commands, functions, file names
- *Italics* sparingly, for emphasis or titles
- Never use ALL CAPS for emphasis

## See Also

- `content-structure-patterns` skill - Blog organization patterns
- `code-example-best-practices` skill - Code snippet guidelines
- `seo-specialist` agent - SEO optimization
