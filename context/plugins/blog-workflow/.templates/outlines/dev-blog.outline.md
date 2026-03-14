# [Project Name]: [What You Built/Shipped]

**Target Length:** [1000-2000] words
**Type:** Development Blog / Project Update
**Tone:** "Here's what we shipped and what we learned"

---

## Meta Requirements

### Dev Blog Alignment Checklist

Development blogs share project progress, decisions, and learnings. Your writing should:

- [ ] **Show, don't just tell** — Include code, screenshots, demos
- [ ] **Context for newcomers** — Don't assume readers followed your last post
- [ ] **Decision rationale** — Explain why, not just what
- [ ] **Honest about tradeoffs** — What you sacrificed for what you gained
- [ ] **Lessons transferable** — Readers should learn something applicable to their work
- [ ] **Progress over perfection** — Share work-in-progress, not just polished results

**Dev Blog Voice Examples:**

- ✅ "We shipped X this week. Here's why we made these choices..."
- ✅ "This didn't work the way we expected. Here's what we learned..."
- ✅ "If you're building something similar, watch out for..."
- ❌ "Everything went perfectly according to plan."
- ❌ "We're excited to announce..." (marketing speak)
- ❌ "Stay tuned for more updates!" (without substance)

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Screenshots | Show UI/output | When describing user-facing changes |
| Code diffs | Show what changed | When explaining refactors or fixes |
| Architecture diagrams | Show structure | When introducing new components |
| GIFs/demos | Show interactions | For features best understood in motion |
| Metrics charts | Show impact | When quantifying improvements |

---

## Post Structure

Follow the **Context → What We Built → How We Built It → What We Learned** flow.

---

### Title

Use descriptive, specific titles:

- "[Project]: Shipping [Feature] in [Timeframe]"
- "Building [X]: Week [N] Update"
- "How We [Accomplished X] in [Project]"
- "[Project] Dev Log: [Specific Topic]"

---

### Opening Hook (50-100 words)

- What shipped or changed?
- Why should the reader care?
- Quick preview of what they'll learn

---

### Context (100-200 words)

#### Where We Started

- Brief recap of project state
- Link to previous post if applicable
- What problem we were solving

#### Goals for This Phase

- What we set out to accomplish
- Success criteria

---

### What We Built (300-500 words)

#### Feature/Change Overview

- High-level description
- Screenshot or demo

#### Key Components

- Break down major pieces
- Code snippets for interesting parts

```[language]
# Include actual code
# Comment on non-obvious parts
```

#### User Impact

- What users can now do
- Before/after comparison if applicable

---

### How We Built It (300-500 words)

#### Technical Approach

- Architecture decisions
- Tools and libraries chosen
- Why this approach over alternatives

#### Interesting Challenges

- Problems we hit
- How we solved them
- Code examples where helpful

#### What We Changed Our Minds About

- Initial assumptions that were wrong
- Pivots during development
- Why we made different choices

---

### Results (150-250 words)

#### Metrics (if available)

- Performance improvements
- User adoption
- Bug counts, test coverage

#### Qualitative Outcomes

- User feedback
- Team observations
- What feels better/worse

---

### What We Learned (200-300 words)

#### Technical Lessons

- Insights about tools, patterns, approaches
- What would you do differently?

#### Process Lessons

- Team workflow observations
- Communication that helped or hurt

#### Advice for Others

- "If you're building something similar..."
- Common pitfalls to avoid

---

### What's Next (100-150 words)

- Upcoming work
- Open questions
- How readers can get involved (if applicable)

---

## Writing Notes

### Dev Blog Guidelines

| Do | Don't |
|----|-------|
| Share work-in-progress | Wait for perfection |
| Include actual code | Describe code abstractly |
| Admit mistakes | Pretend everything went smoothly |
| Explain decisions | Just show end results |
| Link to previous context | Assume readers remember |
| Show metrics when available | Make vague claims |

### Tone Calibration

- More casual than research posts
- First person ("I" or "we") is fine
- Technical but accessible
- Enthusiastic without being promotional

### Frequency Considerations

- Regular cadence builds audience
- Shorter, more frequent > longer, sporadic
- Summarize previous posts briefly for new readers

---

## Metadata

```yaml
---
title: "[Project]: [What You Built]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - dev-log
  - [project-name]
  - [technology]
type: dev-blog
project: [project-name]
series: [series-name if applicable]
status: draft
---
```
