# Post Types

The blog-workflow supports 19 distinct post types, each with a specific purpose, voice, and structure.

## Type Overview

| Type | Voice | Formality | Temporality | Purpose |
|------|-------|-----------|-------------|---------|
| [Tutorial](#tutorial) | Authoritative | 2-3 | Atemporal | Teach a concept or skill |
| [Walk-through](#walk-through) | Exploratory | 1-2 | During | Show process of doing |
| [Deep Dive](#deep-dive) | Analytical | 2-3 | After | Industry-oriented depth |
| [Research](#research) | Academic | 3-4 | After | Hypothesis → findings |
| [Study Review](#study-review) | Reflective | 2 | After | What I learned + gaps |
| [Review](#review) | Evaluative | 2 | After | Assess external thing |
| [Comparison](#comparison) | Evaluative | 2-3 | After | A vs B analysis |
| [Problems](#problems) | Diagnostic | 2 | Before/During | Crystallize known issue |
| [Open Questions](#open-questions) | Speculative | 1-2 | Before | Explore possibilities |
| [Planning](#planning) | Intentional | 2 | Before | Goals + thought process |
| [Retrospective](#retrospective) | Reflective | 2 | After | Post-mortem on own work |
| [Updates](#updates) | Narrative | 1-2 | During | Project progress notes |
| [Opinions](#opinions) | Personal | 1-2 | Atemporal | My take on X |
| [Dev Blog](#dev-blog) | Practitioner | 2 | Atemporal | Evergreen tech wisdom |
| [Announcement](#announcement) | Declarative | 1-2 | Point-in-time | I made X, here it is |
| [Reference](#reference) | Neutral | 1-2 | Living | Curated index/collection |
| [ELI5](#eli5) | Pedagogical | 1-2 | Atemporal | Simplify complex topic |
| [5 Levels](#5-levels) | Pedagogical | 2-3 | Atemporal | Progressive complexity |

## Type Definitions

### Tutorial

**Purpose**: Teach a concept or skill with authoritative voice.

**Voice**: You know the material well and are teaching it.

**Structure**:

- Clear learning objectives
- Prerequisites
- Step-by-step instruction
- Code examples with explanations
- Summary and next steps

**Living variant**: Yes - APIs and tools change.

**Example topics**: "How to set up eBPF tracing", "Understanding Rust ownership"

---

### Walk-through

**Purpose**: Show the process of doing something, including discovery and mistakes.

**Voice**: Exploratory - you're learning alongside the reader.

**Structure**:

- Starting point and goal
- Step-by-step actions with reasoning
- Mistakes and corrections
- Observations and learnings
- Outcome

**Living variant**: No - captures a specific moment.

**Example topics**: "Debugging a memory leak in production", "My first CTF challenge"

---

### Deep Dive

**Purpose**: Industry-oriented in-depth analysis of a specific, scoped topic.

**Voice**: Analytical - thorough but accessible.

**Structure**:

- Scope definition
- Background context
- Detailed analysis
- Practical implications
- Conclusions

**Living variant**: No - publish editions (v2, v3) instead.

**Example topics**: "How Linux CFS scheduler works", "Inside the V8 garbage collector"

---

### Research

**Purpose**: Formal investigation with hypothesis, methodology, and findings.

**Voice**: Academic - rigorous and precise.

**Structure**:

- Abstract
- Introduction and hypothesis
- Methodology
- Results
- Discussion
- Conclusions
- References

**Living variant**: No - findings are snapshot; follow-up is new post.

**Example topics**: "Comparing container runtime performance", "Effect of cache size on query latency"

---

### Study Review

**Purpose**: Reflect on what was learned from studying a topic, book, or course.

**Voice**: Reflective - sharing your learning journey.

**Structure**:

- What was studied
- Key takeaways
- Gaps and unanswered questions
- How it connects to prior knowledge
- What's next

**Living variant**: No - captures learning at a moment.

**Example topics**: "After reading DDIA", "What I learned from the Rust book"

---

### Review

**Purpose**: Evaluate an external thing (course, tool, library, book, policy).

**Voice**: Evaluative - balanced assessment with clear criteria.

**Structure**: See [Review Subtypes](./review.md) for subtype-specific structure.

**Universal fields**:

- Rating (if applicable)
- Summary
- Pros
- Cons
- Recommendation
- Last evaluated date

**Living variant**: Optional - "Updated after 6 months" pattern.

**Example topics**: "Course review: MIT 6.824", "Tool review: Helix editor"

---

### Comparison

**Purpose**: Analyze alternatives side-by-side.

**Voice**: Evaluative - fair, criteria-driven comparison.

**Structure**:

- What's being compared and why
- Comparison criteria
- Analysis per criterion
- Summary table
- Recommendation by use case

**Living variant**: Yes - products evolve, rankings change.

**Example topics**: "Neovim vs Helix vs Zed", "PostgreSQL vs SQLite for embedded use"

---

### Problems

**Purpose**: Crystallize an identified problem with evidence.

**Voice**: Diagnostic - structured problem statement.

**Structure**:

- Problem statement
- Evidence and symptoms
- Root cause analysis (if known)
- Impact assessment
- Potential solutions (brief)

**Living variant**: Optional - as understanding evolves.

**Example topics**: "The N+1 query problem in our API", "Why our CI takes 45 minutes"

---

### Open Questions

**Purpose**: Explore possibilities when you don't have clear answers.

**Voice**: Speculative - thinking out loud.

**Structure**:

- The question
- Why it matters
- Possible answers/approaches
- Research paths to explore
- Current inclination (if any)

**Living variant**: Optional - add answers as discovered.

**Example topics**: "Could WASM replace containers?", "Is GraphQL worth the complexity?"

---

### Planning

**Purpose**: Document thought process and goals before starting work.

**Voice**: Intentional - future-focused.

**Structure**:

- What and why
- Goals and non-goals
- Constraints
- Approach options
- Risks and mitigations
- Success criteria

**Living variant**: No - becomes Retrospective later.

**Example topics**: "Planning: Rust rewrite of core service", "Planning: Blog migration to Astro"

---

### Retrospective

**Purpose**: Reflect on completed work - what worked, what didn't.

**Voice**: Reflective - honest post-mortem.

**Structure**:

- What was the goal
- What actually happened
- What went well
- What went poorly
- What I'd do differently
- Key learnings

**Living variant**: No - reflection on completed work.

**Example topics**: "Retro: 6 months of Rust in production", "Retro: Failed startup attempt"

---

### Updates

**Purpose**: Semi-structured progress notes on ongoing work.

**Voice**: Narrative - project diary.

**Structure**:

- What happened since last update
- Current status
- Blockers and challenges
- Next steps
- Learnings (optional)

**Living variant**: No - each update is a new entry.

**Example topics**: "Compiler project: Week 3", "Job search update: March 2026"

---

### Opinions

**Purpose**: Share personal perspective on a topic.

**Voice**: Personal - first-person, authentic.

**Structure**:

- The opinion (stated clearly)
- Why I hold it
- Counterarguments considered
- Caveats and nuance
- Call to action (optional)

**Living variant**: Rare - original take has value, but views evolve.

**Example topics**: "Why I stopped using Docker for local dev", "Monorepos are overrated"

---

### Dev Blog

**Purpose**: Evergreen technical wisdom grounded in experience.

**Voice**: Practitioner - "here's what works".

**Structure**:

- Context/problem
- The insight or recommendation
- Practical examples
- Trade-offs and caveats
- Summary

**Living variant**: Yes - toolkits and practices evolve.

**Example topics**: "My terminal setup in 2026", "Debugging strategies that actually work"

---

### Announcement

**Purpose**: Declare that something exists or happened.

**Voice**: Declarative - clear and direct.

**Structure**:

- What is it
- Why it matters
- How to use/access it
- What's next

**Living variant**: No - point-in-time by definition.

**Example topics**: "Launching my new CLI tool", "I passed the CKA exam"

---

### Reference

**Purpose**: Curated collection of resources, maintained over time.

**Voice**: Neutral - minimal opinion, maximum utility.

**Structure**:

- Scope and purpose
- Categories/organization
- Items with brief descriptions
- Last updated date

**Living variant**: Yes - core purpose is to stay current.

**Example topics**: "eBPF learning resources", "MCP servers I use"

---

### ELI5

**Purpose**: Explain complex topics using simple language and metaphors.

**Voice**: Pedagogical - patient, accessible.

**Structure**:

- The complex thing (named)
- The simple explanation
- Analogy or metaphor
- Where the analogy breaks down
- Going deeper (optional links)

**Living variant**: Optional - deepen as understanding grows.

**Example topics**: "ELI5: How does TLS work?", "ELI5: What is a monad?"

---

### 5 Levels

**Purpose**: Explain a topic at progressively increasing complexity.

**Voice**: Pedagogical - adapting to audience.

**Structure**:

- Level 1: Child (5-year-old)
- Level 2: Teenager (middle/high school)
- Level 3: Undergraduate
- Level 4: Graduate student
- Level 5: Expert/PhD

**Living variant**: Optional - deepen as understanding grows.

**Example topics**: "Cryptography at 5 levels", "Machine learning at 5 levels"

## Choosing a Type

Use this decision tree:

```text
Am I teaching something I know well?
├── Yes → Do I want progressive complexity?
│   ├── Yes → 5 Levels
│   └── No → Is it a simple concept?
│       ├── Yes → ELI5
│       └── No → Tutorial
└── No → Am I showing my process?
    ├── Yes → Is it learning/studying?
    │   ├── Yes → Study Review
    │   └── No → Walk-through
    └── No → Am I evaluating something?
        ├── Yes → Is it comparing alternatives?
        │   ├── Yes → Comparison
        │   └── No → Review
        └── No → (continue to other branches...)
```

See [Post Type Decision Guide](../workflow/choosing-type.md) for the complete decision tree.
