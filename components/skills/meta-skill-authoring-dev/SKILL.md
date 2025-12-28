---
name: skill-authoring
description: Use when creating new skills, editing existing skills, initializing skill structure, packaging skills for distribution, or verifying skills work before deployment. This skill applies TDD methodology to documentation.
---

# Skill Authoring

## Overview

**Writing skills IS Test-Driven Development applied to process documentation.**

Write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**Official guidance:** For Anthropic's official skill authoring best practices, see anthropic-best-practices.md.

## What is a Skill?

A **skill** is a modular, self-contained package that extends Claude's capabilities with specialized knowledge, workflows, and tools. Skills transform Claude from a general-purpose agent into a specialized agent equipped with procedural knowledge.

**Skills are:** Reusable techniques, patterns, tools, reference guides
**Skills are NOT:** Narratives about how you solved a problem once

### Skill Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/     - Executable code
    ├── references/  - Documentation loaded as needed
    └── assets/      - Files used in output
```

### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude

## TDD Mapping for Skills

| TDD Concept | Skill Creation |
|-------------|----------------|
| **Test case** | Pressure scenario with subagent |
| **Production code** | Skill document (SKILL.md) |
| **Test fails (RED)** | Agent violates rule without skill |
| **Test passes (GREEN)** | Agent complies with skill present |
| **Refactor** | Close loopholes while maintaining compliance |

## When to Create a Skill

**Create when:**
- Technique wasn't intuitively obvious
- You'd reference this again across projects
- Pattern applies broadly (not project-specific)
- Others would benefit

**Don't create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in CLAUDE.md)

## Skill Creation Process

### Step 1: Understand with Concrete Examples

Understand how the skill will be used through examples:
- "What functionality should this skill support?"
- "What would a user say that should trigger this skill?"
- "Can you give examples of how this skill would be used?"

### Step 2: Plan Reusable Contents

Analyze each example to identify:
1. Scripts that would be rewritten repeatedly
2. References that would need rediscovery each time
3. Assets that would be copied or modified

### Step 3: Initialize the Skill

Run the initialization script:

```bash
python scripts/init_skill.py <skill-name> --path <output-directory>
```

The script creates:
- SKILL.md template with frontmatter
- Example directories: scripts/, references/, assets/

### Step 4: Write with TDD (RED-GREEN-REFACTOR)

**RED Phase - Baseline Testing:**
- Run pressure scenarios WITHOUT the skill
- Document exact failures and rationalizations verbatim
- Identify which pressures trigger violations

**GREEN Phase - Write Minimal Skill:**
- Address specific baseline failures observed
- Run same scenarios WITH skill
- Verify agent now complies

**REFACTOR Phase - Close Loopholes:**
- Capture new rationalizations verbatim
- Add explicit counters for each loophole
- Build rationalization table
- Re-test until bulletproof

See @testing-skills-with-subagents.md for complete testing methodology.

### Step 5: Package for Distribution

```bash
python scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

The script validates and creates a distributable .skill file.

### Step 6: Iterate

After testing on real tasks:
1. Notice struggles or inefficiencies
2. Identify needed updates
3. Apply TDD cycle again

## SKILL.md Structure

**Frontmatter (YAML):**
- `name`: Hyphen-case, max 64 characters
- `description`: Third-person, max 1024 characters, starts with "Use when..."

**CRITICAL: Description = When to Use, NOT What the Skill Does**

```yaml
# ❌ BAD: Summarizes workflow - Claude may follow this instead of reading skill
description: Use when executing plans - dispatches subagent per task with code review

# ✅ GOOD: Just triggering conditions
description: Use when executing implementation plans with independent tasks
```

**Body Structure:**
```markdown
# Skill Name

## Overview
Core principle in 1-2 sentences.

## When to Use
Symptoms and use cases (bullets)

## Core Pattern
Before/after comparison or workflow

## Quick Reference
Table for scanning common operations

## Common Mistakes
What goes wrong + fixes
```

## Claude Search Optimization (CSO)

### Rich Description Field
- Start with "Use when..."
- Include concrete triggers, symptoms, situations
- Write in third person
- **NEVER summarize the skill's workflow**

### Keyword Coverage
- Error messages: "Hook timed out", "race condition"
- Symptoms: "flaky", "hanging", "zombie"
- Tools: Actual commands, library names

### Token Efficiency

**Target word counts:**
- Frequently-loaded skills: <200 words
- Other skills: <500 words

**Techniques:**
- Reference --help for tool flags
- Cross-reference other skills
- Compress examples
- Eliminate redundancy

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

This applies to NEW skills AND EDITS to existing skills.

**No exceptions:**
- Not for "simple additions"
- Not for "just adding a section"
- Not for "documentation updates"

## Bundled Resources

### scripts/
Executable code for deterministic reliability or repeatedly rewritten tasks.

**Available scripts:**
- `scripts/init_skill.py` - Initialize new skill from template
- `scripts/package_skill.py` - Package skill for distribution
- `scripts/quick_validate.py` - Validate skill structure

### references/
Documentation loaded as needed into context.

**Available references:**
- `references/validation-checklist.md` - Complete validation checklist
- `references/workflows.md` - Workflow design patterns
- `references/output-patterns.md` - Output format patterns

### assets/
Files used in output (templates, images, fonts).

## Meta-Skill Derivatives

Meta-skills provide foundational patterns that language or domain-specific skills extend. This pattern enables knowledge reuse while allowing specialization.

### Meta-Skill Hierarchy

```
meta-<pattern>-<focus>           # Foundational patterns
└── <domain>-<pattern>-<focus>   # Specialized derivative
```

**Examples:**
| Meta-Skill | Derivatives |
|------------|-------------|
| `meta-sdk-patterns-eng` | `aws-sdk-dev`, `stripe-sdk-dev` |
| `meta-library-dev` | `rust-lib-dev`, `python-lib-dev` |
| `meta-cli-patterns-dev` | `rust-cli-dev`, `go-cli-dev` |

### Creating a Derivative Skill

**Step 1: Reference the Meta-Skill**

In the derivative's SKILL.md, explicitly reference the parent:

```markdown
## This Skill Extends

This skill extends `meta-library-dev` with Rust-specific patterns.
For foundational concepts (API design, versioning, testing strategies),
see the meta-skill first.

## This Skill Adds

- Rust-specific: Cargo.toml configuration, feature flags
- Rust idioms: Ownership patterns in public APIs
- Rust tooling: rustdoc, cargo publish, crates.io
```

**Step 2: Determine What to Add**

Derivatives should add domain-specific content in these categories:

| Category | What to Add |
|----------|-------------|
| **Tooling** | Package managers, build tools, linters |
| **Idioms** | Language-specific patterns and conventions |
| **Ecosystem** | Common libraries, registries, community practices |
| **Examples** | Code samples in the target language |
| **Gotchas** | Language-specific pitfalls and workarounds |

**Step 3: Avoid Duplication**

Do NOT repeat content from the meta-skill. Instead:
- Reference sections: "See `meta-library-dev` → Versioning Strategy"
- Extend with specifics: "In addition to semver (see meta-skill), Rust uses..."
- Override only when necessary: "Unlike the general pattern, Rust prefers..."

### Derivative Naming Convention

```
<domain>-<pattern>-<focus>

Where:
- domain   = language, platform, or service (rust, aws, k8s)
- pattern  = what the skill covers (lib, sdk, cli, api)
- focus    = audience (dev, ops, eng, nub, xec)
```

**Valid derivative names:**
- `rust-lib-dev` (Rust library development)
- `python-sdk-dev` (Python SDK development)
- `go-cli-ops` (Go CLI operations)

### Derivative Template

```markdown
---
name: <domain>-<pattern>-<focus>
description: Use when developing <domain> <pattern>s. Extends meta-<pattern>-<focus> with <domain>-specific tooling, idioms, and ecosystem patterns.
---

# <Domain> <Pattern> Development

<Domain>-specific patterns for <pattern> development. This skill extends
`meta-<pattern>-<focus>` with <domain> tooling, idioms, and ecosystem practices.

## This Skill Extends

- `meta-<pattern>-<focus>` - Foundational <pattern> patterns

## This Skill Adds

- <Domain> tooling: [list tools]
- <Domain> idioms: [list patterns]
- <Domain> ecosystem: [list libraries, registries]

## <Domain>-Specific Tooling

[Package manager, build tools, testing frameworks]

## <Domain> Idioms

[Language-specific patterns that differ from general guidance]

## Ecosystem

[Common libraries, registries, community practices]

## Quick Reference

| Task | <Domain> Command |
|------|------------------|
| Create project | `<command>` |
| Build | `<command>` |
| Test | `<command>` |
| Publish | `<command>` |

## References

- `meta-<pattern>-<focus>` - Foundational patterns
- [<Domain> documentation](url)
```

### When to Create Meta vs Derivative

| Create Meta-Skill When | Create Derivative When |
|------------------------|------------------------|
| Pattern applies across 3+ domains | Specializing for one domain |
| Core concepts are language-agnostic | Adding language-specific details |
| You're establishing a new pattern family | Extending existing meta-skill |

## Additional Resources

### Core Documentation
- **anthropic-best-practices.md** - Official Anthropic guidance
- **testing-skills-with-subagents.md** - TDD testing methodology
- **persuasion-principles.md** - Psychology of bulletproofing

### Visualization
- **graphviz-conventions.dot** - Graphviz style rules
- **render-graphs.js** - Render skill flowcharts to SVG

### Examples
- **examples/CLAUDE_MD_TESTING.md** - Full test campaign example

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Skill is obviously clear" | Clear to you ≠ clear to agents. Test it. |
| "It's just a reference" | References can have gaps. Test retrieval. |
| "Testing is overkill" | Untested skills have issues. Always. |
| "I'll test if problems emerge" | Test BEFORE deploying. |
| "Too tedious to test" | Less tedious than debugging in production. |

## Quick Reference

| Task | Command/Reference |
|------|-------------------|
| Initialize skill | `python scripts/init_skill.py <name> --path <path>` |
| Validate skill | `python scripts/quick_validate.py <skill_dir>` |
| Package skill | `python scripts/package_skill.py <skill_dir>` |
| Testing methodology | @testing-skills-with-subagents.md |
| Validation checklist | @references/validation-checklist.md |
| Workflow patterns | @references/workflows.md |
| Output patterns | @references/output-patterns.md |

## The Bottom Line

**Creating skills IS TDD for process documentation.**

Same Iron Law: No skill without failing test first.
Same cycle: RED (baseline) → GREEN (write skill) → REFACTOR (close loopholes).
Same benefits: Better quality, fewer surprises, bulletproof results.
