# Reverse Engineering [Target]: [What You Discovered]

**Target Length:** [2500-4000] words
**Type:** Reverse Engineering Analysis
**Tone:** "I investigated X, discovered Y, here's how"

---

## Meta Requirements

### Reverse Engineering Alignment Checklist

Reverse engineering posts document the process of understanding systems you didn't build. Your writing should:

- [ ] **Document the journey** — Show your investigation process, not just conclusions
- [ ] **Reproducible methodology** — Others could follow your steps
- [ ] **Evidence-based claims** — Every assertion backed by data/observation
- [ ] **Tooling transparency** — What tools you used and why
- [ ] **Ethical framing** — Clear about authorization and responsible disclosure
- [ ] **Actionable findings** — What can readers do with this knowledge?

**Reverse Engineering Voice Examples:**

- ✅ "I noticed [anomaly], which led me to investigate [area]..."
- ✅ "Using [tool], I extracted [data], which revealed..."
- ✅ "This behavior is undocumented. I verified by [method]..."
- ❌ "I hacked into..." (implies unauthorized access)
- ❌ "Obviously, this means..." (without showing evidence)
- ❌ "Trust me, I checked" (without methodology)

---

### Legal/Ethical Section Requirements

- [ ] Authorization statement (your own software, CTF, bug bounty, etc.)
- [ ] Responsible disclosure status if applicable
- [ ] No exploitation details that enable harm without defense context

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Hex dumps | Show raw data | When discussing binary structure |
| Disassembly | Show code | When analyzing compiled code |
| Network captures | Show protocols | When analyzing communications |
| Diagrams | Show structure | For complex systems/formats |
| Screenshots | Show tools/UI | When demonstrating analysis process |
| Annotated images | Highlight details | When pointing out specific features |

---

## Post Structure

Follow the **Target → Approach → Investigation → Findings → Implications** flow.

---

### Title

Use descriptive, intriguing titles:

- "Reverse Engineering [Target]: [Key Discovery]"
- "Inside [System]: How [Feature] Actually Works"
- "Dissecting [Protocol/Format]: A Deep Dive"
- "What I Found Inside [Target]"

---

### Abstract (100-150 words)

- Target: What you analyzed
- Motivation: Why you investigated
- Method: High-level approach
- Finding: Key discovery (spoiler is fine)
- Scope: What's covered/not covered

---

### 1. Introduction (200-300 words)

#### 1.1 The Target

- What system/software/protocol did you analyze?
- Why is it interesting or important?

#### 1.2 Motivation

- What question were you trying to answer?
- What triggered the investigation?

#### 1.3 Authorization Statement

- How did you have permission to analyze this?
- CTF, your own software, authorized research, etc.

#### 1.4 Scope

- What's covered in this analysis
- What's explicitly out of scope
- Required background knowledge

---

### 2. Reconnaissance (300-400 words)

#### 2.1 Initial Observations

- What did you observe before deeper analysis?
- Surface-level behaviors, documentation, prior research

#### 2.2 Hypothesis Formation

- What did you expect to find?
- What questions guided your investigation?

#### 2.3 Tooling Setup

- What tools did you use?
- Environment configuration

```bash
# Example: Tool setup
# [Include actual commands you ran]
```

---

### 3. Analysis Methodology (400-600 words)

#### 3.1 Approach Overview

- Static vs. dynamic analysis
- Why this approach for this target

#### 3.2 Phase 1: [First Analysis Step]

- What you did
- What you found
- Evidence (hex, disassembly, captures)

```text
# Include actual data/code
# Annotate significant portions
```

#### 3.3 Phase 2: [Second Analysis Step]

- Building on previous findings
- Deeper investigation
- Evidence

#### 3.4 Phase 3: [Continue as needed]

- Follow the trail
- Document dead ends too

**[METHODOLOGY NOTE]**
> If you hit a dead end, document it. Dead ends are valuable information for others.

---

### 4. Findings (500-700 words)

#### 4.1 Primary Discovery

- Main finding with evidence
- How you verified it

#### 4.2 Secondary Findings

- Other interesting observations
- Unexpected behaviors

#### 4.3 Undocumented Behavior

- Things not in official documentation
- Hidden features or quirks

#### 4.4 Security Implications (if applicable)

- Vulnerabilities discovered
- Risk assessment
- Responsible disclosure status

**[EVIDENCE BLOCK]**

```text
# Include raw evidence
# Hex dump, disassembly, packet capture, etc.
```

---

### 5. Verification (200-300 words)

#### 5.1 How You Confirmed Findings

- Reproducibility
- Multiple verification methods

#### 5.2 Edge Cases Tested

- Boundary conditions
- Error handling

#### 5.3 Confidence Level

- What you're certain about
- What remains uncertain

---

### 6. Discussion (300-400 words)

#### 6.1 Interpretation

- What do findings mean?
- Why might the system work this way?

#### 6.2 Comparison to Documentation

- Where docs are accurate
- Where docs are wrong or incomplete

#### 6.3 Practical Applications

- How can others use this knowledge?
- Defensive applications
- Development implications

---

### 7. Limitations (150-200 words)

**EXPLICIT LIMITATIONS — REQUIRED**

- What you couldn't analyze
- Time/resource constraints
- Access limitations
- Version-specific findings

---

### 8. Tools and Resources (100-150 words)

#### Tools Used

- [Tool 1]: [Purpose]
- [Tool 2]: [Purpose]

#### Helpful Resources

- Documentation consulted
- Prior research referenced
- Related work

---

### 9. Conclusion (100-150 words)

- Summary of key findings
- Significance
- Potential follow-up investigation

---

### Appendix

- Extended hex dumps
- Full disassembly listings
- Complete packet captures
- Scripts used in analysis

---

## Writing Notes

### Reverse Engineering Guidelines

| Do | Don't |
|----|-------|
| Show your process | Just present conclusions |
| Include raw evidence | Describe without showing |
| Document dead ends | Pretend you found everything immediately |
| Explain tool choices | Assume familiarity |
| State authorization | Imply unauthorized access |
| Consider ethics | Provide exploitation guides |

### Evidence Presentation

- Hex dumps: Annotate significant bytes
- Disassembly: Comment non-obvious instructions
- Packet captures: Highlight relevant fields
- Screenshots: Circle/annotate key areas

### Ethical Considerations

- Default to responsible disclosure
- Redact sensitive information
- Consider dual-use implications
- Focus on defense, not offense

---

## Metadata

```yaml
---
title: "Reverse Engineering [Target]: [Discovery]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - reverse-engineering
  - [target-type]
  - [technology]
type: reverse-engineering
authorization: [ctf | personal | bounty | research]
disclosure_status: [n/a | disclosed | pending]
status: draft
---
```
