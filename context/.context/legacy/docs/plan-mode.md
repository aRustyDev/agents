Plan Mode

Plan mode is a feature in Claude Code that separates research and analysis from execution, significantly improving the safety.

When activated, Claude will not edit files, run commands, or change anything until you approve the plan.

You activate it by pressing shift+tab twice. To exit Plan Mode you can press shift+tab again. (I must say the UX of Claude Code is seamless, well done Anthropic)

This feature dropped (in stealth in v1.0.16) one month after I was using Claude Code daily and yet it instantly changed my workflow especially when working with Claude 4 Opus.

### Prior to Plan Mode

I would frequently start or end prompts with:

> Do not code, just make suggestions

And generally speaking this worked. However, when Claude did provide suggestions it was unfortunately inconsistent in format and verbosity.

Other folks on r/ClaudeAI have mentioned similar inconsistent results when requesting inaction from Claude. This led to an unpredictable UX and feedback loop.

### With Plan Mode

Plan Mode not only provides security but it 'forces' Claude to deliver consistently formatted responses in a reasonable verbosity.

When I asked for suggestions on improving shader time complexity, Claude elegantly provided multiple numbered options with clear benefits outlined for each approach (e.g. speed delta, amount of changes required). No more guessing whether Claude will edit files or just suggest. The output is structured, predictable, and you get to approve before execution.

I have also observed plan mode is incredibly fast! This in combination with the compactness of the plan's produced has made using Opus much more efficient in terms of speed and token usage.

### Opus Plan Mode - Intelligent Planning with Cost Efficiency

The latest enhancement to Plan Mode is the Opus Plan Mode option, which strategically uses Opus 4.1 for planning and research, then automatically switches to Sonnet 4 for execution. This hybrid approach delivers Opus-level intelligence where it matters most while maintaining cost efficiency.

### Key Benefits:

    Intelligent Planning - Leverage Opus 4.1's advanced reasoning for complex analysis and strategy.
    Cost Optimization - Avoid expensive Opus execution by switching to efficient Sonnet 4.
    Seamless Transition - Automatic model switching without user intervention.

Access Opus Plan Mode by selecting option 4 in the /model command: "Use Opus 4.1 in plan mode, Sonnet 4 otherwise"

This approach gives you the best of both worlds!

### Available Tools & Restricted Tools

In plan mode, Claude has access to read-only and research tools:

#### Available tools:

    Read - Files and content viewing.
    LS - Directory listings.
    Glob - File pattern searches.
    Grep - Content searches.
    Task - Research agents.
    TodoRead/TodoWrite - Task management.
    WebFetch - Web content analysis.
    WebSearch - Web searches.
    NotebookRead - Jupyter notebooks.

#### Restricted tools:

    Edit/MultiEdit - File edits.
    Write - File creation.
    Bash - Command execution.
    NotebookEdit - Notebook edits.
    MCP tools that modify state.

Claude can research and plan without touching anything until you approve.

### Plan Subagent Architecture

As of v2.0.28, Plan Mode now uses a dedicated Plan Subagent with enhanced capabilities:

    Claude can resume existing subagents instead of always creating new ones.
    Dynamic model selection - Claude intelligently chooses the best model for each subagent task.
    Improved efficiency through subagent resumption and reuse.

### Research with Explore Subagent

When researching in Plan Mode, Claude may automatically use the Explore Subagent - a Haiku-powered specialist that efficiently searches your codebase while saving context tokens. This automatic delegation happens when you need comprehensive code exploration.

### Extra Cautious

When exiting plan mode, Claude is extra cautious and will ask for additional confirmation about the task he is about to execute. It's a nice touch that further ensures safety is maintained.
