# Context Inspection

The /context command is a new feature which dropped in v1.0.86 which allows you to see an approximation of your context usage across different components:

    System Prompt - Core instructions and behavior definitions.
    System tools - Built-in Claude Code functionality.
    MCP tools - Model Context Protocol server integrations.
    Memory files - CLAUDE.md and project context.
    Custom Agents - Specialized sub-agent definitions.
    Messages - Current conversation history.

It shows how many tokens are used and what percentage of your context window is remaining.

    This is the ultimate tool for Context Engineers.

### Strategic Context Engineering

I am particularly interested in the ease of access to metrics about [Custom agents](https://claudelog.com/mechanics/custom-agents/) and [MCP tools](https://claudelog.com/claude-code-mcps/). Given the existence of [context window based performance depletion](https://claudelog.com/mechanics/context-window-depletion/), it is important for us as context engineers to craft the context as efficiently as possible.

We can now tactically enable/disable MCP tool functions with full knowledge about how many tokens are being consumed. No more guessing whether that MCP server functions are worth the context overhead.

The same principle applies to Custom Agents which are designed by Anthropic to be easily discovered, shared, downloaded and invoked. As I mentioned in [Agent Engineering](https://claudelog.com/mechanics/agent-engineering/), it is important to refine your agents so that they can easily be activated but also so that they are context efficient. The /context command allows us to have better introspection into how efficient our Custom Agents are.

### MCP Server Optimization with /context

Starting in v2.0.10, you can enable/disable MCP servers dynamically using /mcp or @mention commands. Use /context to monitor the context window impact of each MCP server and make data-driven decisions about which servers to keep active.

#### Context Optimization Workflow:

1. Run /context to see MCP tool context consumption.
1. Identify MCP servers consuming context space but not actively needed.
1. Disable unused servers with @server-name disable or via /mcp.
1. Run /context again to verify context savings.
1. Re-enable servers when needed for specific tasks.

#### Context Space Benefits:

Disabling unused MCP servers frees up valuable context space for:

- Extended conversation history.
- Larger code file analysis.
- More complex reasoning tasks.
- Additional Custom Agent definitions.

I disable MCP servers when approaching context window limits during long coding sessions or performing large refactoring operations where maximum context space is needed.

### Current Limitations and Future Potential

Initial use has flagged that the accuracy for context calculations can sometimes be off. However, I believe the value lies more in engineering what is fundamentally in your context, which affects your baseline performance. I anticipate the accuracy of the tool improving over time as Anthropic makes subtle adjustments to the way context is computed.

A potential upgrade of this user interface would be being able to use the arrow keys to navigate through the items and toggle them on/off so we can effectively free up space within the context. This would likely require a Claude reload but it would create a more seamless Context Engineering experience.

### Integration with Other Mechanics

This tool in combination with features like the Micro compact feature which automatically frees up space within the context window related to tool calls helps create a more streamlined experience for managing context efficiently throughout long sessions.

### Interactive Context Analysis

A cool thing I explored is after generating the context data, I asked Claude:

> Where is my context potentially inefficient?

And he provided suggestions about how the context could be engineered to be more efficient. This creates a feedback loop where you can identify bottlenecks and optimize accordingly.

##### Mechanic Benefits:

- Token visibility: Clear breakdown of context consumption across all components.
- Strategic optimization: Data-driven decisions about MCP tools and Custom Agents.
- Performance engineering: Identify context bloat before it impacts response quality.
- Baseline awareness: Understand your fundamental context overhead for better planning.
- Interactive analysis: Ask Claude to review and suggest context improvements.

### Context Engineering

Ask Claude to review your context usage and suggest optimizations. Use [Plan Mode](https://claudelog.com/mechanics/plan-mode/) combined with [ultrathink](https://claudelog.com/faqs/what-is-ultrathink/) for comprehensive analysis: "Where is my context potentially inefficient and how can I optimize it?"
