# Experiment 3: crawl4ai Debug and Verification

## Metadata

```yaml
experiment:
  id: "exp-003-crawl4ai-debug"
  title: "Debug crawl4ai MCP and verify functionality"
  created: "2026-03-08"
  status: "pending"
  prerequisite: "crawl4ai MCP server running"
  hypothesis: "crawl4ai can handle JS-rendered sites better than WebFetch"
```

## Objective

Debug the "Invalid request parameters" error from Phase 1 and verify crawl4ai works for:
1. Basic markdown extraction
2. JavaScript-rendered pages
3. Structured data extraction

## Tools Under Test

| Tool | Endpoint | Purpose |
|------|----------|---------|
| `mcp__crawl4ai__md` | Markdown extraction | Primary content fetch |
| `mcp__crawl4ai__html` | HTML extraction | Schema building |
| `mcp__crawl4ai__crawl` | Batch crawling | Multiple URLs |
| `mcp__crawl4ai__execute_js` | JS execution | Dynamic content |

## Test Cases

### Test 1: Basic Markdown Extraction

```yaml
test_id: "c4a-001-basic-md"
target: "https://buildwithclaude.com/"
tool: "mcp__crawl4ai__md"
parameters:
  url: "https://buildwithclaude.com/"
  f: "fit"
expected:
  - Returns markdown content
  - Status: success
  - Contains skill/plugin listings
```

### Test 2: JS-Rendered Page (mcp.so)

```yaml
test_id: "c4a-002-js-render"
target: "https://mcp.so/"
tool: "mcp__crawl4ai__md"
parameters:
  url: "https://mcp.so/"
  f: "fit"
expected:
  - Renders JavaScript content
  - Returns MCP server listings
  - Better results than WebFetch
```

### Test 3: BM25 Filtered Search

```yaml
test_id: "c4a-003-bm25"
target: "https://buildwithclaude.com/skills"
tool: "mcp__crawl4ai__md"
parameters:
  url: "https://buildwithclaude.com/skills"
  f: "bm25"
  q: "typescript"
expected:
  - Returns filtered content
  - TypeScript-related skills highlighted
```

### Test 4: Batch Crawl

```yaml
test_id: "c4a-004-batch"
tool: "mcp__crawl4ai__crawl"
parameters:
  urls:
    - "https://buildwithclaude.com/skills"
    - "https://buildwithclaude.com/agents"
    - "https://buildwithclaude.com/commands"
expected:
  - All 3 URLs crawled
  - Returns structured results
```

### Test 5: JavaScript Execution

```yaml
test_id: "c4a-005-js-exec"
target: "https://mcp.so/"
tool: "mcp__crawl4ai__execute_js"
parameters:
  url: "https://mcp.so/"
  scripts:
    - "document.querySelectorAll('.server-card').length"
expected:
  - Returns count of server cards
  - Proves JS execution works
```

## Success Criteria

- [ ] All 5 tests complete without "Invalid request parameters"
- [ ] JS-rendered content extracted from mcp.so
- [ ] Batch crawl returns all 3 URLs
- [ ] BM25 filtering produces relevant results
- [ ] Clear documentation of working parameters

## Output Files

- `analysis/results/crawl4ai-debug/test-001-basic-md.yaml`
- `analysis/results/crawl4ai-debug/test-002-js-render.yaml`
- `analysis/results/crawl4ai-debug/test-003-bm25.yaml`
- `analysis/results/crawl4ai-debug/test-004-batch.yaml`
- `analysis/results/crawl4ai-debug/test-005-js-exec.yaml`
