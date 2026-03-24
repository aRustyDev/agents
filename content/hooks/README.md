# Claude Code Hooks

Hooks that enhance Claude Code with automated skill gap detection and feedback.

## Available Hooks

### skill-feedback.sh

**Purpose**: Log session data for offline skill effectiveness analysis.

**Events**: `Stop`, `SessionEnd`

**Features**:
- Logs session end timestamps
- Tracks pending skill gap issues
- Non-blocking (always exits 0)

### skill-feedback.settings.json

**Purpose**: Template for prompt-based skill analysis hooks.

**Contains configurations for**:

1. **Stop Hook (Skill Review)**
   - Runs LLM analysis at task completion
   - Identifies which skills were used
   - Detects unused context (over-broad skills)
   - Notes missing information (coverage gaps)
   - Suggests improvements

2. **UserPromptSubmit Hook (Gap Detection)**
   - Analyzes user prompts for domains
   - Checks skill coverage for each domain
   - Flags gaps before task begins
   - Can output warnings to user

## Installation

### 1. Copy hook script

```bash
cp components/hooks/skill-feedback.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/skill-feedback.sh
```

### 2. Configure settings

Add relevant sections from `skill-feedback.settings.json` to your Claude Code settings:

**Option A: Project-level** (`.claude/settings.json`)
```bash
# Copy and merge into project settings
cat components/hooks/skill-feedback.settings.json
```

**Option B: User-level** (`~/.claude/settings.json`)
```bash
# Add to personal settings for all projects
```

### 3. Verify installation

```bash
# Test the command hook
echo '{}' | ~/.claude/hooks/skill-feedback.sh
cat ~/.claude/logs/skill-feedback.log
```

## Configuration Options

### Prompt-Based Hooks

The `type: "prompt"` hooks use LLM analysis for intelligent decisions:

```json
{
  "type": "prompt",
  "prompt": "Your analysis prompt with $ARGUMENTS placeholder",
  "timeout": 30
}
```

**Response format** (JSON):
```json
{
  "decision": "allow",           // or "block"
  "reason": "Why this decision",
  "output": "Optional user message",
  // Custom fields for logging
  "skills_used": [...],
  "gaps": [...]
}
```

### Command-Based Hooks

The `type: "command"` hooks run bash scripts:

```json
{
  "type": "command",
  "command": "${WORKSPACE}/.claude/hooks/script.sh",
  "timeout": 5
}
```

**Exit codes**:
- `0` = Allow (continue)
- `2` = Block (stop)

## Log Files

Logs are written to `~/.claude/logs/`:

| File | Content |
|------|---------|
| `skill-feedback.log` | Session events, timestamps |
| `skill-gaps.json` | Pending gap issues to create |

## Integration with Rules & Skills

This hook system works with:

- **Rule**: `rules/skill-gap-detection.md` - Always-loaded trigger
- **Skill**: `meta-skill-gaps-dev` - Detailed methodology

The hooks automate what the rule describes; the skill provides the methodology when deeper analysis is needed.

## Customization

### Adjust Prompt Analysis

Edit the `prompt` field in settings to:
- Change domain detection patterns
- Modify response format
- Add project-specific domains

### Add Custom Logging

Extend `skill-feedback.sh` to:
- Log to external services
- Create GitHub issues automatically
- Send notifications

### Disable Specific Hooks

Comment out or remove hook configurations you don't need:
- Remove `UserPromptSubmit` if gap detection is too noisy
- Remove `Stop` prompt hook if review is too slow
- Keep only command hook for lightweight logging
