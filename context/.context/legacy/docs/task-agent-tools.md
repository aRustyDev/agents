# Task/Agent Tools

I consider the Task tool to be Claude's most powerful tool.

It enables Claude to efficiently delegate tasks to sub-agents such as: basic file reads and writes, code searches, file analysis, bash operations, and research tasks.

Due to the main agent being interactive and carrying various overheads it can be slow to perform tasks. Having to wait for human responses creates latency, while switching between different types of operations reduces execution efficiency.

I have observed Claude utilises sub-agents in a reserved manner primarily for operations like reading files, fetching web content, searching for specific text patterns, etc. This cautious approach is likely to avoid potential conflicts from parallel write operations.

To maximize sub-agent usage you have to provide Claude with explicit steps including details which steps will be delegated to sub-agents. This is quite similar to programming to utilise multi-threads. The better you can orchestrate your steps the faster your overall workflow will complete.

However, you must balance token costs with performance gains. Grouping related tasks together is often more efficient than creating separate agents for every operation.

Simplified Illustrative CLAUDE.md for task splitting:

```markdown
## Feature Implementation System Guidelines

### Feature Implementation Priority Rules

- IMMEDIATE EXECUTION: Launch parallel Tasks immediately upon feature requests.
- NO CLARIFICATION: Skip asking what type of implementation unless absolutely critical.
- PARALLEL BY DEFAULT: Always use 7-parallel-Task method for efficiency.

### Parallel Feature Implementation Workflow

1. **Component:** Create main component file.
2. **Styles:** Create component styles/CSS.
3. **Tests:** Create test files.
4. **Types:** Create type definitions.
5. **Hooks:** Create custom hooks/utilities.
6. **Integration:** Update routing, imports, exports.
7. **Remaining:** Update package.json, documentation, configuration files.
8. **Review and Validation:** Coordinate integration, run tests, verify build, check for conflicts.

### Context Optimization Rules

- Strip out all comments when reading code files for analysis.
- Each task handles ONLY specified files or file types.
- Task 7 combines small config/doc updates to prevent over-splitting.

### Feature Implementation Guidelines

- **CRITICAL:** Make MINIMAL CHANGES to existing patterns and structures.
- **CRITICAL:** Preserve existing naming conventions and file organization.
- Follow project's established architecture and component patterns.
- Use existing utility functions and avoid duplicating functionality.
```

### Multi-Threading Mindset

Like programming with threads, explicit orchestration of which steps get delegated to sub-agents yields the best results. Claude uses Task agents cautiously unless you provide detailed delegation instructions.
