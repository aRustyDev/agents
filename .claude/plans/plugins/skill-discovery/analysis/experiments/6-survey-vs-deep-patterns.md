# Experiment 6: Survey vs Deep Download Patterns

## Metadata

```yaml
experiment:
  id: "exp-006-survey-deep"
  title: "Document optimal tool patterns for survey vs deep download"
  created: "2026-03-08"
  status: "pending"
  hypothesis: "Different tools/parameters needed for survey vs deep download"
```

## Objective

Establish clear patterns for two distinct use cases:

1. **Survey Mode**: Quick discovery of what exists
   - List all skills/agents/servers
   - Get counts and categories
   - Minimal detail per item

2. **Deep Mode**: Full download of specific components
   - Complete content extraction
   - All metadata fields
   - Source code/definition files

## Use Case Definitions

### Survey Mode Requirements

```yaml
survey_mode:
  goal: "Enumerate all components in a registry"
  time_budget: "< 30 seconds per registry"
  output_format: "List of items with basic metadata"
  required_fields:
    - name
    - url (to component)
    - type (skill/agent/etc)
  optional_fields:
    - description (brief)
    - author
    - stars/popularity

  success_criteria:
    - "Capture 80%+ of available items"
    - "Response in < 30s"
    - "Consistent format for aggregation"
```

### Deep Mode Requirements

```yaml
deep_mode:
  goal: "Extract complete component definition"
  time_budget: "< 10 seconds per component"
  output_format: "Full content + metadata"
  required_fields:
    - full_content (SKILL.md, agent.md, etc.)
    - all_metadata
    - dependencies
    - source_files (if applicable)

  success_criteria:
    - "Complete content extraction"
    - "Preserves structure/formatting"
    - "Includes linked resources"
```

## Test Scenarios

### Scenario 1: GitHub Survey

```yaml
scenario: "github-survey"
target: "Discover all claude-skill repositories"
tools_to_test:
  - tool: "gh api search/repositories"
    mode: "survey"
    query: "topic:claude-skills"
    parameters:
      per_page: 100
      sort: stars
    expected:
      - Returns 100+ repos
      - Includes stars, description
      - Paginated results

  - tool: "SearXNG"
    mode: "survey"
    query: "claude skills site:github.com"
    parameters:
      format: json
    expected:
      - Multi-engine aggregation
      - More comprehensive than single search
```

### Scenario 2: GitHub Deep

```yaml
scenario: "github-deep"
target: "Download complete skill from repository"
example: "alirezarezvani/claude-skills"
tools_to_test:
  - tool: "gh api repos/.../contents"
    mode: "deep"
    steps:
      1: "List contents of repo"
      2: "Identify SKILL.md or skills/ directory"
      3: "Download each skill file"
    expected:
      - Complete file content
      - Directory structure preserved

  - tool: "crawl4ai (crawl_url)"
    mode: "deep"
    parameters:
      url: "https://github.com/.../raw/main/SKILL.md"
    expected:
      - Raw file content
      - No HTML wrapper
```

### Scenario 3: Registry Survey

```yaml
scenario: "registry-survey"
target: "List all skills on buildwithclaude.com"
tools_to_test:
  - tool: "WebFetch"
    mode: "survey"
    url: "https://buildwithclaude.com/skills"
    prompt: "List all skill names with URLs"
    expected:
      - All 26 skills listed
      - URLs captured

  - tool: "crawl4ai (extract_links)"
    mode: "survey"
    url: "https://buildwithclaude.com/"
    expected:
      - Discovers all page URLs
      - Identifies skill pages
```

### Scenario 4: Registry Deep

```yaml
scenario: "registry-deep"
target: "Extract full skill detail from registry page"
tools_to_test:
  - tool: "crawl4ai (crawl_url)"
    mode: "deep"
    url: "https://buildwithclaude.com/skills/[specific-skill]"
    expected:
      - Full skill description
      - Install command
      - Author info

  - tool: "crawl4ai (extract_structured_data)"
    mode: "deep"
    url: "https://buildwithclaude.com/skills/[specific-skill]"
    expected:
      - Structured JSON output
      - Main content extracted
```

### Scenario 5: Search-Based Survey

```yaml
scenario: "search-survey"
target: "Discover Claude skill registries via search"
tools_to_test:
  - tool: "WebSearch"
    mode: "survey"
    query: "claude code skills marketplace registry"
    expected:
      - Discovers multiple registries
      - Limited to ~10 results

  - tool: "SearXNG"
    mode: "survey"
    url: "http://localhost:8888/search"
    parameters:
      q: "claude code skills marketplace"
      format: "json"
    expected:
      - Aggregates multiple engines
      - Most comprehensive results
```

### Scenario 6: MCP Server Survey

```yaml
scenario: "mcp-survey"
target: "List MCP servers from mcp.so"
tools_to_test:
  - tool: "WebFetch"
    mode: "survey"
    url: "https://mcp.so/"
    expected:
      - Likely fails (JS-heavy)

  - tool: "crawl4ai (crawl_url)"
    mode: "survey"
    expected:
      - Renders JS
      - Returns server list

  - tool: "crawl4ai (deep_crawl)"
    mode: "survey"
    expected:
      - Recursive crawling
      - Discovers all server pages
```

## Pattern Documentation Template

For each successful tool × mode combination:

```yaml
pattern:
  id: ""
  tool: ""
  mode: "survey|deep"
  target_type: "github|registry|search"

  when_to_use: |
    Describe the scenario where this pattern excels

  parameters:
    # Exact parameters to use

  example:
    input: ""
    output_sample: ""

  performance:
    avg_time_ms: 0
    success_rate: "X%"

  limitations:
    - ""

  alternatives:
    - tool: ""
      when: ""
```

## Success Criteria

- [ ] All 6 scenarios tested
- [ ] Survey patterns documented for each registry type
- [ ] Deep patterns documented for each source type
- [ ] Clear decision tree: "Use X tool when Y"
- [ ] Performance benchmarks captured

## Output Files

- `analysis/results/survey-deep/github-patterns.yaml`
- `analysis/results/survey-deep/registry-patterns.yaml`
- `analysis/results/survey-deep/search-patterns.yaml`
- `analysis/findings/survey-deep-recommendations.yaml`
