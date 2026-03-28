# Skill Validation Checklist

**Load this reference when:** finalizing a skill before deployment, reviewing skill quality, or validating structure.

## Quick Validation

Run the validation script:

```bash
python scripts/quick_validate.py <skill_directory>
```

## Structure Validation

- [ ] SKILL.md file exists with valid YAML frontmatter
- [ ] Frontmatter has `name` and `description` fields
- [ ] Name is hyphen-case (lowercase letters, digits, hyphens only)
- [ ] Name is max 64 characters
- [ ] Description is max 1024 characters
- [ ] Markdown body is present and substantial
- [ ] Referenced files actually exist

## Description Quality

- [ ] Uses third person ("This skill should be used when...")
- [ ] Includes specific trigger phrases users would say
- [ ] Lists concrete scenarios ("create X", "configure Y")
- [ ] **Does NOT summarize the skill's workflow** (see CSO principles)
- [ ] Not vague or generic

**Good Description Examples:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events.
```

**Bad Description Examples:**
```yaml
description: Use this skill when working with hooks.  # Wrong person, vague
description: Load when user needs hook help.  # Not third person
description: Provides hook guidance.  # No trigger phrases
description: Use for TDD - write test first, watch it fail...  # Summarizes workflow!
```

## Content Quality

- [ ] SKILL.md body uses imperative/infinitive form
- [ ] Body is focused and lean (1,500-2,000 words ideal, <5k max)
- [ ] Detailed content moved to references/
- [ ] Examples are complete and working
- [ ] Scripts are executable and documented

### Writing Style Check

**Correct (imperative):**
```
To create a hook, define the event type.
Configure the MCP server with authentication.
Validate settings before use.
```

**Incorrect (second person):**
```
You should create a hook by defining the event type.
You need to configure the MCP server.
You must validate settings before use.
```

## Progressive Disclosure

- [ ] Core concepts in SKILL.md (~500 lines max)
- [ ] Detailed docs in references/
- [ ] Working code in examples/
- [ ] Utilities in scripts/
- [ ] SKILL.md references these resources clearly

## Testing (TDD)

- [ ] **RED phase completed**: Ran baseline scenarios WITHOUT skill
- [ ] **Rationalizations documented**: Captured exact failure patterns
- [ ] **GREEN phase completed**: Skill addresses specific failures
- [ ] **REFACTOR phase completed**: Loopholes closed
- [ ] Skill triggers on expected user queries
- [ ] Content is helpful for intended tasks
- [ ] No duplicated information across files

## Common Mistakes

### Mistake 1: Weak Trigger Description

❌ **Bad:**
```yaml
description: Provides guidance for working with hooks.
```
Why bad: Vague, no specific trigger phrases, not third person

✅ **Good:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events.
```

### Mistake 2: Too Much in SKILL.md

❌ **Bad:**
```
skill-name/
└── SKILL.md  (8,000 words - everything in one file)
```

✅ **Good:**
```
skill-name/
├── SKILL.md  (1,800 words - core essentials)
└── references/
    ├── patterns.md (2,500 words)
    └── advanced.md (3,700 words)
```

### Mistake 3: Second Person Writing

❌ **Bad:**
```markdown
You should start by reading the configuration file.
You need to validate the input.
```

✅ **Good:**
```markdown
Start by reading the configuration file.
Validate the input before processing.
```

### Mistake 4: Missing Resource References

❌ **Bad:**
```markdown
# SKILL.md
[Core content with no mention of references/ or examples/]
```

✅ **Good:**
```markdown
# SKILL.md
[Core content]

## Additional Resources
- **`references/patterns.md`** - Detailed patterns
- **`examples/script.sh`** - Working example
```

### Mistake 5: Workflow Summary in Description

❌ **Bad:**
```yaml
description: Use when executing plans - dispatches subagent per task with code review between tasks
```
Why bad: Claude may follow the description instead of reading the full skill

✅ **Good:**
```yaml
description: Use when executing implementation plans with independent tasks
```

## Quality Hierarchy

| Priority | Check |
|----------|-------|
| **Critical** | Valid frontmatter, name/description present |
| **Important** | Third-person description, trigger phrases |
| **Recommended** | Progressive disclosure, lean SKILL.md |
| **Nice-to-have** | Utility scripts, comprehensive examples |
