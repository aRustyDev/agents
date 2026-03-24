---
name: content-structure-patterns
description: Blog structure patterns for tutorials, deep-dives, research summaries, and development journals
created: 2025-02-19
updated: 2025-02-19
tags: [blog, structure, templates, content-patterns]
source: blog-workflow-plugin
---

# Content Structure Patterns

Organizational patterns for different types of technical blog posts.

## Overview

This skill provides structural templates for the four primary blog post types: tutorials, deep-dives, research summaries, and development journals. Each pattern is optimized for its specific purpose and reader expectations.

**This skill covers:**

- Structure templates for 4 blog post types
- Section ordering and purpose
- Length guidelines per section
- Reader journey mapping

**This skill does NOT cover:**

- Writing style and voice (see technical-writing-style)
- Code example formatting (see code-example-best-practices)
- SEO optimization

## Post Types

| Type | Purpose | Typical Length | Reader Goal |
|------|---------|----------------|-------------|
| Tutorial | Teach a skill | 1500-3000 words | Complete a task |
| Deep-dive | Explain concepts | 2000-4000 words | Understand deeply |
| Research Summary | Synthesize findings | 1000-2000 words | Learn key insights |
| Dev Journal | Share experience | 800-1500 words | Learn from journey |

## Pattern: Tutorial

Tutorials guide readers through completing a specific task.

### Structure

```text
# Title: "How to [Action] [Thing] [Context]"

## Introduction (100-150 words)
- What you'll build/learn
- Prerequisites
- Time estimate

## [Setup/Prerequisites] (if significant)
- Required tools
- Environment setup
- Starting point

## Step 1: [First Action]
- Single focused action
- Code example
- Expected result

## Step 2: [Second Action]
- Single focused action
- Code example
- Expected result

## [Additional Steps...]

## [Troubleshooting] (optional)
- Common errors
- Solutions

## Conclusion (50-100 words)
- What was accomplished
- Next steps
- Related resources
```

### Key Principles

1. **One action per step** — Never combine multiple actions
2. **Show expected output** — Let readers verify progress
3. **Provide escape hatches** — Link to troubleshooting for complex steps
4. **Number steps** — Clear progression helps readers track position

### Example Titles

- "How to Set Up CI/CD with GitHub Actions"
- "How to Build a REST API with FastAPI"
- "How to Deploy a Next.js App to Vercel"

## Pattern: Deep-Dive

Deep-dives explain concepts, architectures, or technologies in depth.

### Structure

```text
# Title: "[Concept]: [Subtitle with Hook]"

## Introduction (150-200 words)
- Hook: Why this matters
- What you'll learn
- Who this is for

## Background/Context
- History or motivation
- Problem being solved
- Prior approaches (optional)

## Core Concept 1
- Explanation
- Diagrams/visuals
- Examples

## Core Concept 2
- Explanation
- How it relates to Concept 1
- Examples

## [Additional Concepts...]

## Practical Application
- How to apply this knowledge
- Code examples
- Real-world scenarios

## Trade-offs and Considerations
- When to use this
- When NOT to use this
- Alternatives

## Conclusion (100-150 words)
- Key takeaways (bullet points)
- Further reading
```

### Key Principles

1. **Build understanding progressively** — Each section builds on the previous
2. **Use analogies** — Connect new concepts to familiar ones
3. **Include visuals** — Diagrams aid conceptual understanding
4. **Be honest about trade-offs** — Credibility comes from nuance

### Example Titles

- "Event Sourcing: Building Systems That Remember Everything"
- "Understanding WebAssembly: From Browser to Server"
- "The Actor Model: Concurrency Without Shared State"

## Pattern: Research Summary

Research summaries synthesize multiple sources into actionable insights.

### Structure

```text
# Title: "[Topic]: [Key Finding or Trend]"

## Key Takeaways (100 words)
- 3-5 bullet points
- Most important findings
- Actionable insights

## Introduction (100-150 words)
- Research question or topic
- Why it matters now
- Scope of research

## Findings

### Finding 1: [Headline]
- Evidence/data
- Source attribution
- Implications

### Finding 2: [Headline]
- Evidence/data
- Source attribution
- Implications

## Analysis
- Patterns across findings
- What this means
- Remaining questions

## Recommendations
- Actionable next steps
- Who should care
- Timeline considerations

## Methodology (brief)
- Sources reviewed
- Time period
- Limitations

## Sources
- Linked references
```

### Key Principles

1. **Lead with conclusions** — Key takeaways at the top
2. **Cite sources consistently** — Build credibility
3. **Synthesize, don't summarize** — Add analysis beyond sources
4. **Be transparent about methodology** — Let readers assess validity

### Example Titles

- "State of JavaScript 2024: The Frameworks Developers Actually Use"
- "Database Performance: Benchmarking PostgreSQL vs MySQL"
- "Remote Work Tools: What Engineering Teams Are Using"

## Pattern: Development Journal

Dev journals share personal experiences building or learning something.

### Structure

```text
# Title: "[What I Did/Learned]: [Context or Outcome]"

## TL;DR (50 words)
- What happened
- Key lesson

## Context (100 words)
- What I was trying to do
- Why it mattered
- Starting point

## The Journey

### Challenge 1
- What went wrong
- What I tried
- What worked

### [Additional Challenges...]

## What I Learned
- Key insights (bulleted)
- What I'd do differently
- Resources that helped

## Next Steps (optional)
- What's next
- Open questions
```

### Key Principles

1. **Be authentic** — Share real struggles, not just wins
2. **Extract lessons** — Make it valuable for others
3. **Show your thinking** — The process matters more than the result
4. **Keep it focused** — One project/experience per post

### Example Titles

- "Debugging a Memory Leak: A 3-Day Investigation"
- "What I Learned Building My First Rust CLI"
- "Migrating 10GB of Data: Lessons from Production"

## Section Guidelines

### Introductions

| Element | Purpose | Length |
|---------|---------|--------|
| Hook | Grab attention | 1-2 sentences |
| Value proposition | Why read this | 1 sentence |
| Prerequisites/scope | Set expectations | 1-2 sentences |
| Overview | What's coming | 1 sentence or list |

### Conclusions

| Element | Purpose |
|---------|---------|
| Summary | Reinforce key points |
| Next steps | Guide further learning |
| CTA | Encourage action (subscribe, try, share) |

### Code Sections

See `code-example-best-practices` skill for detailed guidance.

## See Also

- `technical-writing-style` skill - Voice and clarity guidelines
- `code-example-best-practices` skill - Code snippet standards
- `tutorial-format` style - Tutorial output style
- `deep-dive-format` style - Deep-dive output style
