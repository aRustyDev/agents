# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Important

- ALL instructions within this document MUST BE FOLLOWED, these are not optional unless explicitly stated.
- ASK FOR CLARIFICATION If you are uncertain of any of thing within the document.
- DO NOT edit more code than you have to.
- DO NOT WASTE TOKENS, be succinct and concise.

## Task Cost and Usage Information Retrieval

- IMPERATIVE: ANY time the user mentions "task stats", "get task stats", "last task stats", or similar variations, IMMEDIATELY use the automated task stats script without question.

### Task Stats Script Usage:

**Primary Command**: `bash "/path/to/project/.claude/functions/task/task_stats.sh"`

**Script Options:**

- `bash .claude/functions/task/task_stats.sh` - Auto-detects and analyzes most recent Task session
- `bash .claude/functions/task/task_stats.sh session_id.jsonl` - Analyzes specific session file

### IMPORTANT RULES:

- Execute the task_stats.sh script immediately when task stats are requested
- The script auto-detects the most recent Task session or accepts a specific session file
