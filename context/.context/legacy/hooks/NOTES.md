---
title: Notes on AI Hooks
description: This document holds my miscellaneous notes on AI Hooks.
---

# Hooks

## Observations

### Hooks are triggered in different levels

- Stage
  - `PreToolUse`
  - `Notification`
  - `Stop`
  - `PostToolUse`
  - `userpromptsubmit`
  - `SessionStart`
- Matcher
  - `Write|Edit|MultiEdit|TodoWrite`
  - `startup|resume|clear`
  - `mcp__.*`

Q: are these stages universal between all models/client tools?

### Hooks don't have a reliable way to scope based on MCP context

> ie the hook can't tell if an MCP server is external or not, and theres not a way to scope this in any configuration.
