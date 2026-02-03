---
name: MCP Server Usage Guidelines
description: When and how agents should use project MCP servers
scope: global
---

# MCP Server Usage Guidelines

This project has several MCP servers available. Use them appropriately based on the task.

## crawl4ai

**When to use:**
- Fetching web content that WebFetch cannot handle (JavaScript-rendered pages)
- Need screenshots or PDFs of web pages
- Batch crawling multiple URLs
- Extracting structured data from complex web pages

**When NOT to use:**
- Simple static pages (use WebFetch instead - faster)
- Already have the content locally

**Tools:** `md`, `html`, `screenshot`, `pdf`, `execute_js`, `crawl`

## devrag

**When to use:**
- Searching project documentation semantically
- Finding relevant agents, skills, commands, or rules
- Need context about how this project works
- Looking for similar patterns or examples in the codebase

**When NOT to use:**
- Searching for specific file paths (use Glob)
- Searching for exact text matches (use Grep)
- External documentation (use WebFetch or crawl4ai)

## smart-tree

**When to use:**
- Understanding directory structure
- Showing file organization to the user
- Exploring unfamiliar parts of the codebase

**When NOT to use:**
- Already know the file paths
- Only need specific files (use Glob)

## text-editor

**When to use:**
- Making precise edits to files
- Multi-cursor or complex text operations

**When NOT to use:**
- Simple edits (use Edit tool)
- Creating new files (use Write tool)

## mindmap / markmap

**When to use:**
- Visualizing hierarchical information
- Creating visual summaries for the user
- Explaining complex relationships

**When NOT to use:**
- Simple lists or tables suffice
- User hasn't requested visualization

## Knowledge Graph (kg-* commands)

**When to use:**
- `kg-search`: Finding semantically similar context components
- `kg-similar`: Finding entities related to a specific one
- `kg-stats`: Understanding what's indexed

**When NOT to use:**
- Looking for exact file names (use Glob)
- Need real-time file content (use Read)

## Priority Order for Web Content

1. **WebFetch** - Fast, simple static pages
2. **crawl4ai** - JavaScript-rendered or complex pages
3. **firecrawl** - Large-scale crawling with rate limiting

## Priority Order for Project Search

1. **Glob/Grep** - Exact matches, known patterns
2. **devrag** - Semantic search across docs
3. **kg-search** - Semantic search with embeddings (if populated)
