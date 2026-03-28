# [How to X] | [Building Y] | [Getting Started with Z]

**Target Length:** [1500-3000] words
**Type:** Tutorial / How-To Guide
**Tone:** Practical, instructional, "follow along with me"

---

## Meta Requirements

### Tutorial Alignment Checklist

Tutorials teach readers to accomplish a specific task. Your writing should:

- [ ] **Clear outcome** — Reader knows exactly what they'll be able to do after completing
- [ ] **Prerequisite transparency** — State what knowledge/tools are needed upfront
- [ ] **Reproducible steps** — Every step tested and verifiable
- [ ] **Progressive complexity** — Start simple, add complexity incrementally
- [ ] **Error anticipation** — Address common mistakes before readers hit them
- [ ] **Working code** — All code blocks tested and copy-paste ready
- [ ] **Checkpoint verification** — Reader can verify progress at each stage

**Tutorial Voice Examples:**

- ✅ "By the end of this tutorial, you'll have a working X that does Y."
- ✅ "If you see error Z, check that you've completed step 3."
- ✅ "Let's verify this worked before moving on. Run `command` and you should see..."
- ❌ "Obviously, you should know how to..."
- ❌ "Just do X" (without explaining what X is)
- ❌ "This is trivial..."

---

### Prerequisites Section Requirements

- [ ] Required knowledge explicitly stated
- [ ] Required tools with versions
- [ ] Required accounts/access
- [ ] Estimated time to complete
- [ ] Difficulty level indicated

---

### Code Requirements

- [ ] All code blocks tested immediately before publishing
- [ ] Language specified for syntax highlighting
- [ ] Comments explain non-obvious lines
- [ ] Copy-paste ready (no invisible characters, correct escaping)
- [ ] Output shown where helpful
- [ ] Error handling included where appropriate

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Screenshots | Show UI state | When describing UI interactions |
| Terminal output | Show expected results | After commands that produce output |
| Architecture diagrams | Show system structure | Before diving into components |
| Annotated screenshots | Highlight specific elements | When directing attention |
| GIFs/videos | Show interactions | For complex multi-step UI flows |

---

## Post Structure

Follow the **Setup → Steps → Verification → Next Steps** flow.

---

### Title

Use action-oriented titles:

- "How to [Accomplish X] with [Tool Y]"
- "Building [X]: A Step-by-Step Guide"
- "Getting Started with [X]: From Zero to [Outcome]"
- "[X] Tutorial: [Specific Outcome] in [Timeframe]"

---

### Introduction (150-250 words)

#### What You'll Build/Learn

- Concrete outcome in 1-2 sentences
- Screenshot or demo of end result if applicable

#### Why This Matters

- When would you need this?
- What problem does it solve?

#### Prerequisites

```markdown
**Prerequisites:**

- [ ] [Knowledge requirement 1]
- [ ] [Tool requirement with version: e.g., "Python 3.10+"]
- [ ] [Account/access requirement]
- [ ] ~[X] minutes to complete
- [ ] Difficulty: [Beginner | Intermediate | Advanced]
```

#### What We'll Cover

- Numbered list of major sections
- Helps readers assess scope and skip ahead if needed

---

### Setup (Variable length)

#### Environment Setup

- Installation commands
- Configuration steps
- Verification that setup worked

```bash
# Example: Install dependencies
pip install package-name==1.2.3

# Verify installation
package-name --version
# Expected output: package-name 1.2.3
```

#### Project Scaffolding

- File structure to create
- Starter code if applicable

```text
project/
├── src/
│   └── main.py
├── tests/
├── config.yaml
└── README.md
```

**[CHECKPOINT]**
> ✅ **Verify:** Run `[command]`. You should see `[expected output]`. If not, check [common issue].

---

### Step 1: [First Major Task] (Variable length)

#### What We're Doing

- One sentence explaining the goal of this step

#### The Code/Commands

```python
# Step 1: [Description]
# [Code with comments]
```

#### Explanation

- Why this code/approach?
- What each part does (for non-obvious sections)

#### Expected Result

- What should happen?
- Screenshot or output if applicable

**[CHECKPOINT]**
> ✅ **Verify:** [How to confirm this step worked]

**[COMMON ERROR]**
> ⚠️ **If you see `[error]`:** [Solution or explanation]

---

### Step 2: [Second Major Task]

[Repeat structure from Step 1]

---

### Step 3: [Third Major Task]

[Repeat structure from Step 1]

---

### [Continue for all steps...]

---

### Putting It All Together

#### Complete Code

- Full working example
- Reader can compare against their implementation

```python
# Complete implementation
# [Full code here]
```

#### Running the Final Result

```bash
# Run the complete application
python main.py

# Expected output:
# [Show full expected output]
```

**[FINAL CHECKPOINT]**
> ✅ **Success:** You should now have [working outcome]. Test it by [verification method].

---

### Troubleshooting (Required)

Common issues readers may encounter:

#### Issue: [Error message or symptom]

**Cause:** [Why this happens]
**Solution:** [How to fix]

#### Issue: [Another common problem]

**Cause:** [Why this happens]
**Solution:** [How to fix]

#### Issue: [Third common problem]

**Cause:** [Why this happens]
**Solution:** [How to fix]

---

### Next Steps

#### Extending This Tutorial

- [ ] [Enhancement 1]: [Brief description]
- [ ] [Enhancement 2]: [Brief description]
- [ ] [Enhancement 3]: [Brief description]

#### Related Tutorials

- [Link to related tutorial 1]
- [Link to related tutorial 2]

#### Further Reading

- [Official documentation]
- [Deeper dive on concept X]

---

### Conclusion (50-100 words)

- Recap what was accomplished
- Encourage reader
- Invite questions/feedback

---

## Writing Notes

### Tutorial-Specific Guidelines

| Do | Don't |
|----|-------|
| Test every command before publishing | Assume code works |
| Show expected output | Leave reader guessing if it worked |
| Anticipate errors | Assume smooth path |
| Use numbered steps | Use vague sequences |
| Include verification points | Rush to the end |
| Specify versions | Say "install X" without version |

### Code Block Standards

```python
# ✅ Good: Commented, tested, shows output
result = function(param)  # Returns processed data
print(result)
# Output: {'status': 'success', 'data': [...]}

# ❌ Bad: Unexplained, no output shown
result = function(param)
```

### Checkpoint Frequency

- After every setup step
- After every major code addition
- Before any step that depends on prior steps
- At the end of each major section

### Pre-Publication Checklist

- [ ] All code blocks tested in clean environment
- [ ] All prerequisites listed
- [ ] Screenshots current (UI may have changed)
- [ ] Links verified working
- [ ] Estimated time is accurate
- [ ] Troubleshooting section populated with real issues
- [ ] Proofread by someone unfamiliar with the topic

---

## Metadata

```yaml
---
title: "[Action] [Topic]: [Outcome]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - tutorial
  - [technology]
  - [topic]
type: tutorial
difficulty: [beginner | intermediate | advanced]
time_to_complete: "[X] minutes"
prerequisites:
  - [prereq 1]
  - [prereq 2]
status: draft
---
```
