# Agents

Agents come in two flavors:

1. Markdown: These are used dynamically discovered and used by Claude Code as Tasks.
2. Executable: These are used programmatically, to execute specific tasks. These are heavily preferential to API Usage > Claude Subscriptions.

```asciidoc
.claude/agents/
└─ <foo-agent>/
    ├─ data/
    │   ├─ agent.json   # The context data shared between different sub-agents (ie issue #, session id, etc)
    │   ├─ baz.json     # The context data for 'baz' sub-agent
    │   └─ bar.json     # The context data for 'bar' sub-agent
    ├─ src/
    │   ├─ bar.py       # module to do 'bar' operations
    │   ├─ baz.py       # module to do 'baz' operations
    │   └─ init.py
    ├─ <bar-subagent>/
    │   ├─ prompt.md    # The prompt for this specific sub-agent
    │   └─ config.yml   # allowed_tools, model, included_skills
    ├─ <baz-subagent>/
    │   ├─ prompt.md    # The prompt for this specific sub-agent
    │   └─ config.yml   # allowed_tools, model, included_skills
    ├─ main.py
    └─ README.md
```

## CLI

- Agents should have `--tui` option, for interactive mode.
  - Use `cement` TUI library
  - https://builtoncement.com/
  - https://github.com/datafolklabs/cement
- Agents must emit `OpenTelemetry` traces/metrics/logs for monitoring and debugging.
- Agents should include `langsmith` support
