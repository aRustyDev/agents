# Debugging [Error/Issue]: [Root Cause Summary]

**Target Length:** [1500-2500] words
**Type:** Debugging Journey / Root Cause Analysis
**Tone:** "I hit this wall, here's how I got past it"

---

## Meta Requirements

### Debug Post Alignment Checklist

Debug posts document the investigation process for problems. Your writing should:

- [ ] **Show the journey** — Include dead ends and wrong turns
- [ ] **Searchable symptoms** — Include exact error messages, stack traces
- [ ] **Reproducible setup** — Others can recreate the problem
- [ ] **Root cause clarity** — Explain WHY, not just what fixed it
- [ ] **Prevention focus** — How to avoid this in the future
- [ ] **Time investment visible** — Help readers know if this applies to them

**Debug Post Voice Examples:**

- ✅ "I spent 4 hours on this. Here's how to fix it in 5 minutes..."
- ✅ "The error message said X, but the actual problem was Y..."
- ✅ "I tried A, then B, then C. Only C worked because..."
- ❌ "Just do X" (without explaining why)
- ❌ "This is a simple fix" (dismissive of the struggle)
- ❌ [Solution without symptoms] (not searchable)

---

### SEO/Searchability Requirements

- [ ] Exact error message in title or first paragraph
- [ ] Stack trace included (sanitized if needed)
- [ ] Version numbers specified
- [ ] Environment details provided
- [ ] Common search terms included naturally

---

## Post Structure

Follow the **Symptoms → Investigation → Root Cause → Solution → Prevention** flow.

---

### Title

Use searchable, specific titles:

- "Debugging [Exact Error Message]"
- "Fix: [Error] in [Technology] [Version]"
- "[Error] When [Action]: Root Cause and Solution"
- "Why [Symptom] and How to Fix It"

---

### TL;DR (50-100 words)

For readers who just want the fix:

```markdown
**TL;DR:** [One-sentence root cause]. Fix: [Specific action].
```

```[language]
# The fix
[Minimal code/command to solve]
```

---

### 1. The Symptoms (200-300 words)

#### 1.1 What I Saw

- Error message (exact text)
- Behavior observed
- When it occurred

```text
# Exact error message or stack trace
[Paste actual error - sanitize sensitive info]
```

#### 1.2 Environment

- OS and version
- Language/runtime version
- Framework version
- Relevant dependencies
- Configuration

```text
# Version info
[Include version commands and output]
```

#### 1.3 What I Was Trying to Do

- The action that triggered the error
- Expected behavior
- Minimal reproduction steps

---

### 2. Investigation (400-600 words)

#### 2.1 First Hypothesis

- What I initially thought was wrong
- Why I thought that
- What I tried

```[language]
# What I tried first
[Code/commands]
```

- Result: Did it work? If not, what did I learn?

#### 2.2 Second Hypothesis

- Next theory based on new information
- Investigation steps
- Evidence gathered

```[language]
# What I tried next
[Code/commands]
```

- Result: Progress made or new dead end?

#### 2.3 The Breakthrough

- What finally pointed to the real problem
- The "aha" moment
- Key evidence that confirmed it

**[INVESTIGATION TIP]**
> Document your dead ends. They help others avoid the same rabbit holes and might be relevant for different root causes.

---

### 3. Root Cause (300-400 words)

#### 3.1 The Actual Problem

- What was actually wrong
- Why the symptoms appeared the way they did
- Why error messages were misleading (if applicable)

#### 3.2 Why It Happened

- Underlying cause (configuration, bug, misunderstanding)
- Contributing factors
- Why this wasn't obvious

#### 3.3 Why It Was Hard to Find

- What made debugging difficult
- Misleading symptoms
- Documentation gaps

---

### 4. The Solution (300-400 words)

#### 4.1 The Fix

- Exact steps to resolve

```[language]
# The solution
# Comment explaining each step
[Working code/commands]
```

#### 4.2 Verification

- How to confirm it's fixed
- Expected output

```text
# Expected output after fix
[Show what success looks like]
```

#### 4.3 Alternative Solutions

- Other approaches that might work
- Tradeoffs between options
- When to choose each

---

### 5. Prevention (200-300 words)

#### 5.1 How to Avoid This

- Configuration best practices
- Checks to add
- Documentation to read

#### 5.2 Early Detection

- Warning signs to watch for
- Tests to add
- Monitoring suggestions

#### 5.3 If You Hit This Again

- Quick diagnostic steps
- Key things to check first
- When this pattern recurs

---

### 6. Lessons Learned (150-200 words)

- What I learned about the technology
- What I learned about debugging
- How this changed my mental model

---

### Related Resources (Optional)

- Links to relevant documentation
- Related issues/bugs
- Similar problems and solutions

---

## Writing Notes

### Debug Post Guidelines

| Do | Don't |
|----|-------|
| Include exact error text | Paraphrase errors |
| Show dead ends | Skip to the solution |
| Explain root cause | Just show the fix |
| Include version info | Assume versions |
| Make it searchable | Use vague titles |
| Show verification | End at "try this" |

### Searchability Tips

- Include the exact error message early
- Use common phrasings people would search
- Include technology names and versions
- Consider what you searched for

### Time Investment Context

Help readers quickly assess relevance:

- "This took me 4 hours to debug"
- "Quick fix once you know the issue"
- "Obscure edge case affecting <1% of users"

### Sanitization

- Remove sensitive paths, tokens, passwords
- Replace with clear placeholders: `YOUR_TOKEN`, `/your/path`
- Keep enough context to reproduce

---

## Metadata

```yaml
---
title: "Debugging [Error]: [Root Cause]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - debugging
  - [technology]
  - [error-type]
type: debug-post
error_message: "[Exact error for search indexing]"
technologies:
  - name: [tech]
    version: [version]
time_to_debug: "[estimate]"
time_to_fix: "[estimate]"
status: draft
---
```
