# [Title]: [Subtitle]

**Target Length:** [2500-4000] words
**Type:** [Original Research | Empirical Study | Novel Methodology | Survey/Taxonomy | Conceptual Framework | Technical Implementation]
**Tone:** "We hypothesized X, tested Y, found Z"

---

## Meta Requirements

### Research Engineer Alignment Checklist

Research Engineers blend research rigor with engineering delivery. Your writing should demonstrate:

- [ ] **Hypothesis-driven framing** — Start with a clear hypothesis or research question, not just "I built X"
- [ ] **Methodology transparency** — Describe how you did the work in enough detail for replication
- [ ] **Empirical grounding** — Support claims with data, experiments, or systematic observation
- [ ] **Intellectual honesty** — Acknowledge what you don't know, what didn't work, and where you're uncertain
- [ ] **Limitation awareness** — Explicitly state scope boundaries and what conclusions you cannot draw
- [ ] **Open questions** — Demonstrate you see beyond your current work to unsolved problems
- [ ] **Engineering pragmatism** — Ground abstractions in concrete implementations and real-world applicability

**Research Engineer Voice Examples:**

- ✅ "We hypothesized that graph-based memory would outperform vector retrieval. Our experiments on N conversations showed..."
- ✅ "This approach has significant limitations: we tested only on English text and cannot conclude..."
- ✅ "An open question remains: how does this scale beyond our test corpus?"
- ❌ "I built a cool thing and it works great!"
- ❌ "This is the definitive solution to X."
- ❌ "Trust me, it's better."

---

### Citation Requirements (Zotero Setup)

#### Zotero Configuration Checklist

- [ ] Zotero desktop installed with browser connector
- [ ] Zotero account created for sync (optional but recommended)
- [ ] Better BibTeX plugin installed for export
- [ ] Citation style configured (IEEE or ACM recommended for technical blogs)

#### Zotero Workflow

1. **Collect sources** as you research using browser connector
2. **Organize** in a collection named after your blog post
3. **Annotate** key papers with notes on relevance
4. **Export** bibliography when writing:
   - Right-click collection → Export Collection
   - Format: Better BibTeX or Better CSL JSON
   - Or use Zotero Word/Google Docs plugin for inline citations

#### Citation Format Example (IEEE Style)

```text
[1] K. Greshake et al., "Not What You've Signed Up For: Compromising Real-World
    LLM-Integrated Applications with Indirect Prompt Injection," arXiv:2302.12173, 2023.
```

#### Citation Checklist for This Post

- [ ] Foundational papers in the domain cited
- [ ] Prior work acknowledged (even if you're extending/critiquing it)
- [ ] Tools/libraries credited with versions
- [ ] All claims backed by citation or marked as hypothesis/observation
- [ ] Bibliography exported and formatted consistently

#### Citation Targets (Fill in for your post)

| Category | Sources to Cite |
|----------|-----------------|
| Foundational papers | [List key papers] |
| Prior work | [List related approaches] |
| Tools/libraries | [List with versions] |
| Datasets | [If applicable] |
| Documentation | [Official docs referenced] |

---

### Visual Requirements

Every research-oriented blog post should include visuals that aid comprehension. Plan these before writing.

#### Visual Targets Checklist

- [ ] **Architecture/Flow Diagram** — How components interact (Mermaid, draw.io, Excalidraw)
- [ ] **Data Visualization** — Results charts, comparison tables (matplotlib, Observable)
- [ ] **Code Blocks** — Key implementation snippets (syntax highlighted, annotated)
- [ ] **Tables** — Structured comparisons, metrics, summaries

#### Visual Targets for This Post

| Figure # | Type | Description | Tool |
|----------|------|-------------|------|
| Figure 1 | Diagram | [Describe what it shows] | [Mermaid/draw.io] |
| Figure 2 | Chart | [Describe data visualized] | [matplotlib/etc] |
| Table 1 | Table | [Describe comparison] | Markdown |
| Code 1 | Code | [Describe snippet purpose] | [Language] |

#### Visual Standards

- All figures should have captions explaining what to observe
- Charts should have labeled axes and legends
- Code blocks should be syntax highlighted and commented
- Diagrams should be readable without color (accessibility)

---

## Post Structure

Follow the **Problem → Approach → Experiment → Results → Limitations** flow.

---

### Abstract (150-200 words)

Write LAST, after the post is complete. Include:

- **Problem statement** — What gap or challenge does this address?
- **Approach summary** — What did you do? (1-2 sentences)
- **Key finding** — What's the headline result?
- **Scope acknowledgment** — What are the main limitations?

```text
[TEMPLATE]
[Problem]: [One sentence stating the gap/challenge]
[Approach]: [One sentence on methodology]
[Finding]: [One sentence on key result]
[Scope]: [One sentence on main limitations]
```

---

### 1. Introduction (400-500 words)

#### 1.1 Problem Statement

- What specific problem are you addressing?
- Why does this problem matter?
- Who is affected by this problem?

**Framing guidance:** Lead with the problem, not your solution. The reader should understand why this matters before learning what you did.

#### 1.2 Hypothesis or Research Question

- State your hypothesis explicitly
- Or frame as a research question if exploratory

```text
**Hypothesis:** [X will outperform Y because Z]
— OR —
**Research Question:** [How does X affect Y under conditions Z?]
```

#### 1.3 Contribution Summary

- What does this post contribute?
- Is it: new data, new methodology, new framework, new tool?
- What will the reader learn?

#### 1.4 Scope Statement

- What is IN scope?
- What is explicitly OUT of scope?
- What audience is this written for?

**[UNCERTAINTY CALLOUT]**
> ⚠️ **Uncertainty:** [State any major uncertainties about your framing, assumptions, or approach here. E.g., "This is early-stage research. We present preliminary findings, not validated conclusions."]

---

### 2. Background (400-600 words)

#### 2.1 Domain Context

- What does the reader need to know to understand your work?
- Define key terms
- Explain relevant concepts

#### 2.2 Prior Work

- What has been done before?
- What approaches exist?
- Where are the gaps?

**Citation target:** This section should be citation-heavy. Every claim about prior work needs a reference.

#### 2.3 Your Position in the Landscape

- How does your work relate to prior work?
- Are you extending, critiquing, or replacing?
- What's your unique angle?

---

### 3. Methodology / Approach (500-700 words)

#### 3.1 Approach Overview

- High-level description of your method
- Why this approach over alternatives?

#### 3.2 Implementation Details

- Technical specifics
- Configuration, parameters, environment
- Enough detail for replication

**[CODE BLOCK TARGET]**

```python
# Include key implementation code
# Annotate with comments explaining non-obvious choices
```

#### 3.3 Experimental Design (if applicable)

- What did you test?
- How did you structure trials?
- What controls did you use?

#### 3.4 Evaluation Criteria

- How do you measure success?
- What metrics? Why those metrics?
- What's the baseline for comparison?

**[VISUAL TARGET: Architecture/Flow Diagram]**
> Include diagram showing methodology flow here.

**[UNCERTAINTY CALLOUT]**
> ⚠️ **Uncertainty:** [Acknowledge methodological choices that might be questioned. E.g., "Our choice of X over Y may affect results. We did not test alternative configurations."]

---

### 4. Results (400-600 words)

#### 4.1 Primary Results

- Present main findings
- Use data, not just claims
- Compare to baseline/alternatives

**[VISUAL TARGET: Results Table/Chart]**

| Condition | Metric A | Metric B | Notes |
|-----------|----------|----------|-------|
| Baseline | X | X | |
| Your approach | X | X | |
| Alternative | X | X | |

#### 4.2 Analysis

- What do the results mean?
- Why did you observe these outcomes?
- What patterns emerge?

#### 4.3 Negative Results

- What didn't work?
- What surprised you?
- What results were inconclusive?

**Important:** Negative results are valuable. Report them honestly.

**[UNCERTAINTY CALLOUT]**
> ⚠️ **Uncertainty:** [Report confidence intervals, variance, or statistical significance limitations. E.g., "With N=50, our confidence interval is wide. These results should be considered preliminary."]

---

### 5. Discussion (300-400 words)

#### 5.1 Interpretation

- What's the significance of your results?
- How do they relate to your hypothesis?
- Did you confirm, refute, or complicate your initial assumptions?

#### 5.2 Implications

- What are the practical implications?
- Who should care about these findings?
- What actions do these results suggest?

#### 5.3 Comparison to Prior Work

- How do your results compare to existing approaches?
- Where do you agree/disagree with established findings?

---

### 6. Limitations

**⚠️ EXPLICIT LIMITATIONS SECTION — REQUIRED**

This section is mandatory. Skipping or minimizing limitations signals low research maturity.

#### 6.1 Scope Limitations

- What population/domain/context did you study?
- What can you NOT generalize to?

#### 6.2 Methodological Limitations

- What methodological choices might affect validity?
- What didn't you control for?
- What alternative approaches might yield different results?

#### 6.3 Data Limitations

- Sample size issues
- Data quality concerns
- Representativeness questions

#### 6.4 What We Cannot Conclude

- Explicitly state conclusions you CANNOT draw
- What would be needed to draw those conclusions?

**Template sentences:**

- "We tested only [X], so cannot conclude about [Y]."
- "Our sample of N=[X] limits statistical power for [Y]."
- "We did not evaluate [X], which may affect [Y]."
- "These results should not be interpreted as [X]."

---

### 7. Open Questions

**⚠️ OPEN QUESTIONS SECTION — REQUIRED**

This section demonstrates intellectual depth. You should identify 5-10 questions your work raises or leaves unanswered.

#### Questions for Future Work

- [ ] [Open question 1]
- [ ] [Open question 2]
- [ ] [Open question 3]
- [ ] [Open question 4]
- [ ] [Open question 5]

**Template:**

- "How does [X] scale to [larger context]?"
- "What is the relationship between [X] and [Y]?"
- "Can [approach] be adapted for [different domain]?"
- "What explains the [unexpected observation]?"
- "How do we measure [concept that lacks clear metrics]?"

---

### 8. Conclusion (150-200 words)

- Restate problem and contribution (1-2 sentences)
- Summarize key findings (1-2 sentences)
- Acknowledge limitations (1 sentence)
- Point to future directions (1-2 sentences)

**Avoid:**

- Overstating conclusions
- Introducing new information
- Excessive hedging (be appropriately confident in what you DID find)

---

### References

Use Zotero export. Format consistently (IEEE or ACM style).

```text
[1] Author, A. et al. (Year). "Title." Venue/Journal. DOI/URL.
[2] ...
```

---

### Appendix (Optional)

Include supplementary material that supports but doesn't fit in main text:

- Extended methodology details
- Full data tables
- Additional code examples
- Raw results

---

## Writing Notes

### Tone Guidelines

| Do | Don't |
|----|-------|
| "We observed X" | "X is true" |
| "Our results suggest Y" | "This proves Y" |
| "Under our test conditions" | "Always" / "Never" |
| "One limitation is Z" | [Omitting limitations] |
| "An open question is W" | "This solves everything" |

### Structure Guidelines

- **Lead with findings in each section.** Don't bury the lead.
- **Use topic sentences.** First sentence of each paragraph should convey the main point.
- **Break up walls of text.** Use bullets, tables, code blocks, and visuals.
- **Be specific.** "37% improvement" not "significant improvement."

### Research Engineer Voice

You're demonstrating that you:

1. Can formulate testable hypotheses
2. Design rigorous evaluations
3. Report results honestly (including failures)
4. Acknowledge limitations without excessive hedging
5. See beyond current work to open problems

### Pre-Publication Checklist

- [ ] Abstract written last and accurately summarizes content
- [ ] All claims either cited or marked as hypothesis/observation
- [ ] All figures have captions
- [ ] Code blocks are tested and syntactically correct
- [ ] Limitations section is substantive (not perfunctory)
- [ ] Open questions section included
- [ ] Proofread for clarity and concision
- [ ] Title is specific and informative (not clickbait)

---

## Metadata (for blog frontmatter)

```yaml
---
title: "[Title]"
subtitle: "[Subtitle]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - [tag1]
  - [tag2]
  - [tag3]
type: [research | methodology | implementation | survey]
status: draft
word_count_target: [X]
---
```
