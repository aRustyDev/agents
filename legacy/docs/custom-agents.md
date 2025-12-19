# Custom Agents

Sub-agents were always one of Claude Code's greatest strengths. However, the expectation for users to know when to invoke them manually and remember what expertise to give them always held back the functionality for normal users. No longer...

Custom agents are specialized agents that can be utilized to solve specific tasks. They are automatically invoked by Claude in a similar manner to how Tools are invoked automatically!

This approach brings incredible potential! Given how reliable and well-developed the MCP tools ecosystem has become, I envision a thriving future where we collaboratively build, share, and exchange agents. If you have cool agents or want to iterate on existing ones, be sure to head over to [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/).

Unlike traditional sub-agents, they have their own custom system prompt, tools, and context window separate from their delegating agent. Custom agents are engineered to be specialized, isolated and efficient. Their configuration is integrated natively within Claude Code, effectively removing the need for third-party persona orchestration tools.

### The Game Will Never Be The Same

- **Automatic Delegation** - This mechanic is powerful and scalable because of the automatic delegation of tasks to specialized isolated agents. The integration process is seamless and builds on Claude's reliability when using tools. Claude delegates tasks based on the task description in your request, the description field in agent configurations, the current context, and available tools.
- **No Manual Invocation Required** - You no longer need to remember which role sub-agent to use or when. Claude intelligently routes tasks to the appropriate specialist, just like how it automatically selects the right tools. However, you will need to benchmark how reliable the task routing is within your setup, especially if you flood Claude with too many custom agent options.

### Core Benefits

- **Separate Context Windows** - Each custom agent operates with its own context window, separate from the delegating agent. This allows larger tasks to be completed without concerning the delegating agent with every detail, preventing different tasks from [poisoning the context](https://claudelog.com/mechanics/poison-context-awareness/) while maintaining peak performance.
- **Specialized System Prompts** - Individual custom agent system prompts can be scoped precisely, avoiding the inheritance of redundant context, thus preserving the limited context window.
- **Role-Specific Tools** - Agents can be configured with specific tools, helping prevent security issues by only allowing trusted agents to perform certain tasks. Specific agents can be tested and evaluated for reliability at their role. This first-party level of integration takes the concept of [Split role sub-agents](https://claudelog.com/mechanics/split-role-sub-agents/) to the next level!
- **Community Sharing** - Once refined, custom agents can be shared across projects, among teams, or even in [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/), creating a collaborative ecosystem of ever-evolving specialized agents.

### Quick Start Guide

Custom agents were introduced in Claude Code [v1.0.60](https://claudelog.com/claude-code-changelog/#v1060)

1. Open the Custom Agents Interface
   `/agents`

2. Select 'Create New Agent' Choose whether to create a project-level or user-level custom agent.

3. Define Your Agent
   - **Recommended**: Generate with Claude first, then customize to make it yours.
   - Describe your agent in detail and when it should be used.
   - Select specific tools or leave blank to inherit all tools.
   - Edit the system prompt to define role, capabilities, and approach.
   - Pick the color of your agent.
   - Review the configuration of your `custom agent`.

4. Save and Use Your custom agent is now available! Claude will use it automatically when appropriate, or you can invoke it explicitly: Use the algorithmic complexity specialist agent to analyze this function.

#### File Format:

```markdown
---
name: your-agent-name
description: Description of when this agent should be invoked
tools: tool1, tool2, tool3 # Optional - inherits all tools if omitted
model: sonnet # Optional - sonnet, opus, or haiku. Inherits if omitted
---

Your agent's system prompt goes here. Define the role, capabilities,
and approach to solving problems. Include specific instructions,
best practices, and any constraints the agent should follow.
```

#### Basic Usage

Automatic Invocation - Once created, your custom agents work automatically. Claude will select and use the appropriate agent based on your request and the agent's description.

**Manual Invocation** - You can also explicitly request a specific agent:

```markdown
Use the algorithmic complexity specialist agent to analyze this function.
```

**Task Delegation** - Claude intelligently routes tasks to specialized isolated agents, similar to how it automatically selects tools for different operations.

### Configuration

Custom agents are stored as Markdown files with YAML frontmatter in two possible locations:

| Type           | Location            | Scope                         | Priority |
| -------------- | ------------------- | ----------------------------- | -------- |
| Project agents | `.claude/agents/`   | Available in current project  | Highest  |
| User agents    | `~/.claude/agents/` | Available across all projects | Lower    |

When agent names conflict, project-level agents take precedence over user-level agents.

### Configuration Fields

| Field       | Required | Description                                                                                 |
| ----------- | -------- | ------------------------------------------------------------------------------------------- |
| name        | Yes      | Unique identifier using lowercase letters and hyphens                                       |
| description | Yes      | Natural language description of the agent's purpose                                         |
| tools       | No       | Comma-separated list of specific tools. If omitted, inherits all tools from the main thread |
| model       | No       | Model to use for this agent: sonnet, opus, or haiku. If omitted, inherits model             |

### Best Practices

    Start with Claude Generation - Generate your initial agent with Claude, then customize it to make it your own.

    Separation of Concerns - Like with programming, better separation of concerns in your custom agents leads to better performance, maintainability, inspectability, and shareability.

    Provide Examples - Include positive/negative examples in your system prompts. LLMs excel at pattern recognition and repetition, so be sure to provide a sufficient amount of distinct instances.

    Progressive Tool Expansion - Begin with a carefully scoped set of tools for your custom agent and progressively expand the tool scope as you validate its behavior and identify additional capabilities needed for optimal performance.

### Community Vision

I'm beyond excited for the future of agentic workflows! We should all work together to refine optimal instances of various agents and share them among each other. This kind of initiative is much more viable with automatic delegation since users don't need to understand when to activate agents.

Sharing custom agents is as simple as copying a single Markdown file. For example, a code-reviewer.md agent created for one project can be instantly shared with teammates or the community:

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: opus # Alternative: model: haiku for 3x cost savings with 90% capability
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:

1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:

- Code is simple and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed
- Time complexity of algorithms analyzed
- Licenses of integrated libraries checked

Provide feedback organized by priority:

- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

Your goal should be to build a comprehensive collection of battle-tested custom agents from different domains, allowing you to effectively tackle any task.

Official Documentation: [Sub-agents Documentation](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

#### Community Collaboration

The true power of custom agents emerges through community sharing and iteration. Build upon others' agents, share your specialized creations, and contribute to a growing ecosystem of battle-tested specialists. Visit r/ClaudeAI to discover, share, and refine agents collaboratively.

#### Token Cost Awareness

Each custom agent invocation carries a variable initialization cost based on tool count and configuration complexity. Design your agents thoughtfully to ensure they provide sufficient value to justify this overhead, focusing on specialized tasks that benefit from dedicated context and expertise.

#### Model Selection Strategy

Claude Haiku 4.5 (October 2025) delivers 90% of Sonnet 4.5's agentic coding performance at 2x speed and 3x cost savings ($1/$5 vs $3/$15). This makes Haiku 4.5 the optimal choice for lightweight agents requiring frequent invocation. Access via --model claude-haiku-4-5 or model: haiku in agent configuration. Reserve Sonnet 4.5 for orchestration, quality validation, and tasks where the 10% capability gap matters. See Agent Engineering for detailed cost-benefit analysis.

#### Specialized Intelligence

Custom agents act like specialized team members - each with domain expertise, specific tools, and focused responsibilities. This creates a collaborative AI environment where the right specialist handles each task.
