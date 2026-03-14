# [Accessible Title]: [What We Actually Found]

**Target Length:** [1500-2500] words
**Type:** Conference Paper → Blog Translation
**Tone:** "We published [paper] at [venue]. Here's what it means in plain language"

---

## Meta Requirements

### Paper-to-Blog Translation Checklist

Conference paper blogs make academic work accessible. Your writing should:

- [ ] **Plain language first** — Lead with intuition, save formalism for links
- [ ] **Motivation prominence** — Why should non-specialists care?
- [ ] **Result clarity** — What did you actually find? What does it mean?
- [ ] **Honest limitations** — Don't oversell; academics will check the paper
- [ ] **Depth available** — Link to full paper for those who want details
- [ ] **Broader context** — Where does this fit in the field?

**Paper-to-Blog Voice Examples:**

- ✅ "Our paper shows that [plain language finding]. Here's the intuition..."
- ✅ "The key insight is [simple explanation]. The paper formalizes this as..."
- ✅ "We tested this on [benchmarks]. The results: [accessible summary]..."
- ❌ [Copy-pasted abstract]
- ❌ "In this paper we propose a novel framework for..." (academic jargon)
- ❌ "Our method achieves state-of-the-art results" (without explaining what that means)

---

### Audience Calibration

This post serves multiple audiences:

- **General tech readers**: Want the gist and why it matters
- **Adjacent researchers**: Want positioning and key insights
- **Domain experts**: Will read the paper, want highlights
- **Media/industry**: Want quotable takeaways

Lead accessible, layer in technical depth.

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Hero figure | Visual summary | Always—from paper or new |
| Intuition diagram | Explain approach | For complex methods |
| Result highlights | Key numbers | Always—quantify claims |
| Comparison simplified | Show improvement | For comparative work |

---

## Post Structure

Follow the **Hook → Problem → Insight → Results → Implications** flow.

---

### Title

**Paper title:** [Formal paper title]

**Blog title:** Make it accessible and intriguing:

- "[Plain Language Finding]"
- "We [Discovered/Built/Showed] [What]: Here's Why It Matters"
- "[Question We Answered]"
- "What [Finding] Means for [Audience]"

---

### The Hook (100-150 words)

- Start with why someone should care
- Use concrete example or surprising fact
- Don't start with "In our paper..."

**Example hooks:**

- "Every time you [common activity], [surprising fact about inefficiency/risk/opportunity]."
- "The standard approach to [X] assumes [Y]. We found that's wrong."
- "[Statistic that motivates the problem]."

---

### The Paper (50-100 words)

Brief formal context:

```text
📄 **Paper:** [Full Title]
📍 **Venue:** [Conference/Journal], [Year]
👥 **Authors:** [Names]
🔗 **Links:** [Paper PDF] | [Code] | [Video] | [Slides]
```

---

### The Problem (200-300 words)

#### In Plain Terms

- What's the problem we tackled?
- Why does it matter?
- Who is affected?

**Use concrete example:**
> Imagine you're [scenario]. Currently, [problem manifestation]. This causes [consequence].

#### The Technical Gap

- For readers who want more detail
- What was missing from prior work?
- What made this hard?

---

### The Key Insight (300-400 words)

**This is the heart of the blog post.**

#### The Intuition

**[FIGURE: Visual explanation of the insight]**

In plain language:

- What's the core idea?
- Why does it work?
- What's the "aha" moment?

> 💡 **Key Insight:** [One-sentence insight that drives the paper]

#### A Bit More Detail

- For technically curious readers
- How does this translate to a method?
- What's the approach at a high level?

```text
[Simple pseudocode or diagram if helpful]
```

#### Why This Wasn't Obvious

- What made this non-trivial?
- What did we have to figure out?
- Why didn't people do this before?

---

### What We Did (200-300 words)

#### The Approach

- High-level method description
- No equations—link to paper for those
- Focus on "what" not "how"

**[FIGURE: Method overview from paper]**

#### The Evaluation

- What did we test on?
- How did we measure success?
- Why these benchmarks/metrics?

---

### What We Found (300-400 words)

**Lead with the headline results.**

#### Key Results

**[FIGURE: Main results visualization]**

| Metric | Prior Best | Our Result | Improvement |
|--------|------------|------------|-------------|
| [Metric 1] | X | Y | +Z% |
| [Metric 2] | X | Y | +Z% |

**In plain terms:** [What these numbers mean for practitioners]

#### What Worked Well

- Where did the approach shine?
- Best-case scenarios

#### What We Learned

- Surprising findings
- Unexpected insights
- Things that didn't work as expected

#### Caveats

- Where results are weaker
- Conditions for these results
- What we haven't tested

---

### What This Means (200-300 words)

#### For Practitioners

- Can you use this today?
- What would change in your workflow?
- When would you apply this?

#### For Researchers

- What does this enable?
- What questions does it raise?
- Where do we go from here?

#### The Bigger Picture

- How does this fit in the field?
- What trend is this part of?
- What's the long-term implication?

---

### Limitations (100-150 words)

**Be honest—your credibility depends on it.**

- What doesn't this work for?
- What assumptions are we making?
- What didn't we test?
- What's the scope of these claims?

---

### Try It Yourself (100-150 words)

*(If applicable)*

- Code availability
- Demo link
- How to reproduce

```bash
# Quick start
git clone [repo]
pip install [package]
python [script] --example
```

---

### FAQ (Optional)

**Q: [Anticipated question]?**
A: [Concise answer]

**Q: [Another anticipated question]?**
A: [Concise answer]

---

### Learn More

- 📄 **Full paper:** [PDF link]
- 💻 **Code:** [GitHub link]
- 📊 **Data:** [Dataset link]
- 🎥 **Talk:** [Video link]
- 📑 **Slides:** [Slides link]

**Citation:**

```bibtex
@inproceedings{...}
```

---

### Acknowledgments

- Co-authors
- Funding
- Collaborators
- Reviewers

---

## Writing Notes

### Paper-to-Blog Guidelines

| Do | Don't |
|----|-------|
| Lead with motivation | Lead with method |
| Use plain language | Use jargon without explanation |
| Show, don't tell (figures) | Describe abstractly |
| Be honest about limitations | Oversell results |
| Link to paper for depth | Try to include everything |
| Make it standalone | Assume paper familiarity |

### Translating Academic Content

**Abstract → Hook + Problem**

- Extract the "why care" from abstract
- Make it concrete and vivid

**Method → Key Insight**

- Find the core idea
- Explain intuition before mechanism

**Results → What We Found**

- Lead with headline number
- Translate to plain language meaning

**Related Work → Background (light)**

- Only what readers need
- Link to paper for full context

### Balancing Audiences

- **First 30%:** Accessible to all
- **Middle 40%:** Technical but explained
- **Last 30%:** For those who want depth + links

### Avoiding Overclaiming

- "We show [X] in [conditions]" not "We prove [X]"
- "On [benchmarks]" not "in general"
- "Improves over [baseline]" not "solves [problem]"

### Social Media Excerpts

Prepare tweetable/shareable snippets:

- One-sentence finding
- Key figure with caption
- Surprising statistic

---

## Metadata

```yaml
---
title: "[Accessible Title]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - research
  - [topic]
  - [venue-tag]
type: paper-blog
paper_title: "[Formal Paper Title]"
venue: [Conference/Journal]
year: [YYYY]
paper_url: [URL]
code_url: [URL or null]
coauthors:
  - [Name 1]
  - [Name 2]
status: draft
---
```
