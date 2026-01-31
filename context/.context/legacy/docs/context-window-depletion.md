# Context Window Depletion

I have observed significant performance degradation during context window depletion. Generally I avoid running Claude to the limit, as response quality declines on tasks which touch multiple parts of a codebase.

I avoid the last fifth of the context window specifically for tasks which require editing multiple parts of the codebase, such medium-large refactors. During memory intensive tasks, Claude needs substantial working memory to maintain awareness of component relationships, naming patterns, architectural decisions, and cross-file references.

Memory-Intensive Tasks (Higher Context Sensitivity):

- Large-scale refactoring across multiple files.
- Feature implementation spanning several components.
- Debugging complex interaction patterns.
- Code review requiring architectural understanding.

Isolated Tasks (Lower Context Sensitivity):

- Single-file edits with clear scope.
- Independent utility function creation.
- Documentation updates.
- Simple bug fixes with localized impact.

To get reliable results whilst accommodating the context window limits, I strategically dice my tasks into smaller chunks so that they can be finished without entering the last fifth of the context window. This involves identifying natural breakpoints in complex workflows. For example, completing individual components before moving on to integration or finishing all research phases before beginning implementation. I lean towards getting Claude to make thorough notes at each checkpoint, e.g. 'Make notes on all the aspects which might be useful to remember when editing this file at a future date'.

**MCP Server Management** - Starting in v2.0.10, you can disable unused MCP servers to free up context space. Each enabled MCP server adds tool definitions to the system prompt, consuming part of your context window even when not actively used. Use /context to see MCP server context consumption, then disable unneeded servers with @server-name disable or via /mcp. This is particularly valuable when approaching context limits during long sessions or memory-intensive tasks.

The overhead of context switching between chunks is typically offset by the improved quality and consistency of responses when Claude operates within optimal memory constraints.

### Size doesn't matter

Claude may have a relatively small context window compared to other models, but Claude's uncanny ability to adhere to instructions is its greatest strength. Utilise the mechanics in this log to work around the limitations.
