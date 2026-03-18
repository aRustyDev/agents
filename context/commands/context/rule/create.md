---
description: Create a new Claude Code rule file with proper structure
argument-hint: <rule-name> [--location project|context]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), AskUserQuestion, Glob
---

# Create Rule

Create a new rule file that provides persistent instructions to Claude Code.

## Arguments

- `$1` - Rule name (lowercase, hyphenated). Example: `commit-conventions`
- `--location` - Where to create the rule:
  - `project` (default): `.claude/rules/<rule-name>.md`
  - `context`: `context/rules/<category>/<rule-name>.md`

## Rule vs Command vs Skill

| Use Rule When | Use Command When | Use Skill When |
|---------------|------------------|----------------|
| Always-on guidance | User-triggered workflow | Auto-triggered by context |
| Project conventions | Parameterized actions | Complex domain knowledge |
| Constraints/policies | One-off tasks | Pattern-based activation |
| Style preferences | Multi-step processes | Teachable behavior |

## Workflow

### Step 1: Parse and Validate

1. Extract rule name from `$1`
2. Validate format: `^[a-z][a-z0-9-]{0,46}[a-z0-9]$`
3. Parse `--location` (default: `project`)
4. Determine target path
5. Check if rule exists — ask to overwrite

### Step 2: Gather Rule Information

Use AskUserQuestion to collect:

1. **Rule Purpose**: What behavior does this rule enforce? (1-2 sentences)
2. **Rule Type**: What kind of rule is this?
   - Convention (naming, formatting, structure)
   - Constraint (what NOT to do)
   - Preference (how to approach tasks)
   - Integration (external tool usage)
3. **Scope**: When does this rule apply?
   - Always
   - Specific file types
   - Specific directories
   - Specific actions

### Step 3: Check for Related Rules

Search for existing rules that might overlap:

```text
Glob: .claude/rules/*.md
Glob: context/rules/**/*.md
```

If related rules found, ask if this should:

- Extend an existing rule
- Replace an existing rule
- Be a new standalone rule

### Step 4: Create Directory

```bash
mkdir -p "$(dirname "<target-path>")"
```

### Step 5: Generate Rule File

Write the rule based on type:

#### Convention Rule Template

````markdown
# <Rule Title>

<Brief description of what this rule enforces>

## When This Applies

<Scope description>

## Convention

<Clear statement of the convention>

### Examples

**Do:**

```text
<good example>
```

**Don't:**

```text
<bad example>
```

## Rationale

<Why this convention exists>
````

### Constraint Rule Template

````markdown
# <Rule Title>

<Brief description of what this rule prevents>

## Constraints

| Action | Allowed | Notes |
|--------|---------|-------|
| <action> | ❌ | <why not> |
| <action> | ✅ | <when ok> |

## Exceptions

<When constraints can be relaxed>

## Rationale

<Why these constraints exist>
````

#### Preference Rule Template

````markdown
# <Rule Title>

<Brief description of the preference>

## Preference

<Clear statement of preferred approach>

## Alternatives

| Approach | When to Use |
|----------|-------------|
| Preferred | <default case> |
| Alternative | <exception case> |

## Examples

<Concrete examples of applying the preference>
````

#### Integration Rule Template

````markdown
# <Rule Title>

<Brief description of the integration>

## Tool/Service

<What external tool this rule covers>

## Usage

### When to Use

<Triggers for using this tool>

### How to Use

<Step-by-step usage>

### Configuration

<Any required setup>

## Examples

<Common usage patterns>
````

### Step 6: Validate

1. Check markdown structure is valid
2. Verify no placeholder text remains
3. Confirm examples are concrete

### Step 7: Report

```text
## Rule Created

| Field | Value |
|-------|-------|
| Rule | <rule-name> |
| Location | <path> |
| Type | <convention/constraint/preference/integration> |

**Next steps:**
1. Review and refine the rule
2. Test that Claude follows the rule
3. Run `/context:rule:review <path>` to check quality
```

## Examples

```bash
# Create a project rule
/context:rule:create commit-conventions

# Create a shared rule in context/
/context:rule:create api-error-handling --location context

# Create a constraint rule
/context:rule:create no-force-push
```

## Common Rule Patterns

### File-Scoped Rules

```markdown
## When This Applies

Files matching:

- `*.py` in `src/`
- `*.ts` in `lib/`
```

### Action-Scoped Rules

```markdown
## When This Applies

When performing:

- Git commits
- Code review
- File creation
```

### Always-On Rules

```markdown
## When This Applies

Always active for this project.
```

## Related Commands

- `/context:rule:review` - Review rule quality
- `/context:rule:refine` - Improve rule based on feedback
- `/context:command:create` - Create user-triggered command
