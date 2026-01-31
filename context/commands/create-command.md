---
description: Create a new Claude Code slash command with proper structure and frontmatter
argument-hint: <command-name> [--location project|personal] [--model haiku|sonnet|opus]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), AskUserQuestion, TodoWrite
---

# Create Claude Code Slash Command

Create a new slash command with proper YAML frontmatter, argument handling, and content structure.

## Arguments

- `$1` - Command name (lowercase, hyphenated, max 32 chars). Example: `review-pr`
- `--location` - Where to create the command:
  - `project` (default): `.claude/commands/<command-name>.md`
  - `personal`: `~/.claude/commands/<command-name>.md`
- `--model` - Execution model override (optional):
  - `haiku` - Fast, simple tasks
  - `sonnet` - Balanced (default behavior)
  - `opus` - Complex reasoning

## Command vs Skill

Before creating a command, confirm this is the right choice:

| Use Command When | Use Skill When |
|------------------|----------------|
| User explicitly triggers with `/` | Claude should auto-invoke based on context |
| Parameters vary each invocation | Behavior is consistent |
| Standardized multi-step workflow | Complex, context-aware behavior |
| One-off or occasional use | Frequent, implicit use |

## Workflow

### Phase 1: Parse and Validate

**Use TodoWrite to track progress.**

1. **Parse command name from $1**:
   - Extract name (everything before flags)
   - Validate: lowercase, hyphenated, max 32 chars
   - Pattern: `^[a-z][a-z0-9-]{0,30}[a-z0-9]$`
   - Convention: `verb-noun` format (e.g., `review-pr`, `fix-lint`, `deploy-staging`)

2. **Parse optional flags**:
   - `--location`: Default to `project`
   - `--model`: Optional, omit from frontmatter if not specified

3. **Determine target path**:
   ```bash
   case "$LOCATION" in
     project)  CMD_PATH=".claude/commands/$CMD_NAME.md" ;;
     personal) CMD_PATH="$HOME/.claude/commands/$CMD_NAME.md" ;;
   esac
   ```

4. **Check if command exists**:
   - If file exists, ask to overwrite or choose different name

### Phase 2: Gather Command Information

Use AskUserQuestion to collect:

1. **Command Purpose**: What does this command do? (1-2 sentences)
   - This becomes the `description` field
   - Keep under 100 characters for autocomplete display

2. **Arguments** (optional):
   - How many arguments? (0-3 recommended)
   - For each: name, required/optional, description
   - Example: `pr-number` (required), `--verbose` (optional flag)

3. **Tool Restrictions** (optional):
   - Should this command have limited tool access?
   - Common patterns:
     - Read-only: `Read, Glob, Grep`
     - Git operations: `Read, Write, Bash(git:*)`
     - Full access: Omit `allowed-tools` (default)

4. **Destructive Operations**:
   - Does this command modify files, push to remote, or deploy?
   - If yes, include confirmation step in content

### Phase 3: Create Directory

```bash
# Create commands directory if needed
mkdir -p "$(dirname "$CMD_PATH")"
```

### Phase 4: Generate Command File

#### 4.1 Frontmatter

```yaml
---
description: <purpose - max 100 chars>
argument-hint: <arg1> [arg2] [--flag]
allowed-tools: <tool1>, <tool2>, Bash(pattern:*)
model: <haiku|sonnet|opus>  # Only if specified
---
```

**Frontmatter field reference:**

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Shown in autocomplete, max ~100 chars |
| `argument-hint` | If args | Documents expected arguments |
| `allowed-tools` | Optional | Restricts available tools |
| `model` | Optional | Override default model |

#### 4.2 Content Structure

```markdown
# <Command Title>

<Brief description of what this command does>

## Arguments

- `$1` - <description> (required/optional)
- `$2` - <description> (optional)
- `$ARGUMENTS` - <for capturing all args>

## Workflow

### Step 1: <Action>
<Instructions in imperative form>

### Step 2: <Action>
<Instructions in imperative form>

## Examples

```
/<command-name> <example-args>
```

## Notes

<Any additional context or caveats>
```

#### 4.3 Content Guidelines

1. **Write for Claude, not humans**: Commands contain instructions *to* Claude
2. **Use imperative form**: "Read the file", "Run the tests", "Create a PR"
3. **Be explicit**: Specify exact steps, don't assume behavior
4. **Include validation**: Check inputs before acting
5. **Confirm destructive actions**: Ask before push, deploy, delete
6. **Provide examples**: Show concrete usage with realistic arguments

### Phase 5: Validate

1. **Check frontmatter syntax**:
   - Valid YAML between `---` markers
   - Required `description` field present

2. **Check content structure**:
   - Has clear workflow steps
   - Uses imperative form
   - No placeholder text (e.g., `<TODO>`, `[PLACEHOLDER]`)

3. **Verify file location**:
   - Correct directory for chosen location
   - File has `.md` extension

### Phase 6: Report

```
## Command Created

| Field | Value |
|-------|-------|
| Command | `/<command-name>` |
| Location | `<path>` |
| Description | `<description>` |

**Test your command:**
```
/<command-name> <example-args>
```

**Next steps:**
1. Test the command with various inputs
2. Refine workflow based on testing
3. Add to project documentation
```

## Common Patterns

### Read-Only Analysis

```yaml
---
description: Analyze codebase for <pattern>
allowed-tools: Read, Glob, Grep
---

# Analyze <Pattern>

## Workflow

1. Search for files matching pattern
2. Read and analyze each file
3. Report findings without modifying anything
```

### Git Operations

```yaml
---
description: <Git workflow description>
allowed-tools: Read, Write, Bash(git:*)
---

# <Git Command>

## Workflow

1. Check git status
2. Perform git operations
3. Confirm before push
```

### Deployment

```yaml
---
description: Deploy to <environment>
allowed-tools: Read, Bash(*)
---

# Deploy

## Workflow

1. Run pre-flight checks
2. **Ask for confirmation before deploying**
3. Execute deployment
4. Verify deployment succeeded
```

### Code Generation

```yaml
---
description: Generate <component>
argument-hint: <name> [--type type]
---

# Generate <Component>

## Arguments

- `$1` - Component name (required)
- `--type` - Component type (optional, default: basic)

## Workflow

1. Validate inputs
2. Determine template based on type
3. Generate files
4. Report created files
```

## Argument Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| `$1` | First argument | `/cmd foo` → `$1 = "foo"` |
| `$2`, `$3` | Positional args | `/cmd foo bar` → `$2 = "bar"` |
| `$ARGUMENTS` | All arguments | `/cmd foo bar baz` → `"foo bar baz"` |
| Flags | Convention only | Parse manually in workflow |

## Tool Permission Patterns

| Pattern | Tools | Use Case |
|---------|-------|----------|
| Read-only | `Read, Glob, Grep` | Analysis, review |
| Write files | `Read, Write, Glob` | Code generation |
| Git only | `Read, Write, Bash(git:*)` | Version control |
| Specific command | `Bash(npm:*)` | Package management |
| Full access | *(omit field)* | Unrestricted |

## Troubleshooting

**Command not appearing in autocomplete:**
- Ensure file is in `.claude/commands/` or `~/.claude/commands/`
- Check file has `.md` extension
- Verify frontmatter syntax is valid YAML

**Arguments not substituting:**
- Use `$1`, `$2`, `$3` or `$ARGUMENTS`
- Check argument is passed when invoking

**Tool permission errors:**
- Verify `allowed-tools` includes needed tools
- Use `Bash(pattern:*)` for specific commands

## Related Commands

- `/create-skill` - Create a model-invoked skill (for auto-triggered behavior)
- `/validate-command` - Validate an existing command structure

## Notes

- Commands are simpler than skills - prefer commands for explicit user actions
- Keep commands focused on a single purpose
- Test with edge cases (no args, invalid args, etc.)
