---
description: Search for plugins matching a domain or capability need
argument-hint: '"<purpose>" [--local] [--top N]'
allowed-tools: Read, Glob, Grep, Bash(jq:*)
---

# Search Plugins

Find plugins matching a stated domain or capability need. Searches local plugins and the marketplace registry.

## Arguments

- `$1` - Purpose description in quotes. Example: `"infrastructure as code development"`
- `--local` - Search only local project plugins
- `--top N` - Number of results to return (default: 5)

## Workflow

### Step 1: Search Marketplace Registry

If `.claude-plugin/marketplace.json` exists:

```bash
cat .claude-plugin/marketplace.json | jq '.plugins[] | select(.description | test("<keywords>"; "i"))'
```

### Step 2: Search Local Plugins

Search for plugins in the project:

```text
Glob: content/plugins/*/plugin.json
Glob: content/plugins/*/.claude-plugin/plugin.json
```

For each plugin found:

1. Read the manifest (name, description, keywords)
2. Score based on keyword matches

### Step 3: Analyze Plugin Contents

For promising matches, inventory their components:

```text
Glob: content/plugins/<name>/skills/*/SKILL.md
Glob: content/plugins/<name>/commands/*.md
Glob: content/plugins/<name>/agents/*.md
```

### Step 4: Rank Results

Score each match:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Description match | 30 pts | Purpose keywords in description |
| Keyword match | 25 pts | Purpose keywords in manifest keywords |
| Component coverage | 25 pts | Has relevant skills/commands |
| Maintenance | 20 pts | Recent version, author info |

Sort by total score descending. Take top N.

### Step 5: Present Results

```markdown
## Plugin Search: "<purpose>"

### Matches

#### 1. <plugin-name> (<score>/100)

| Field | Value |
|-------|-------|
| Path | <path> |
| Version | <version> |
| Description | <desc> |
| Keywords | <keywords> |

**Components**:

- Skills: N
- Commands: N
- Agents: N

---

(repeat for each result)

### Summary

| Rank | Plugin | Score | Components | Match Reason |
|------|--------|-------|------------|--------------|
| 1    | ...    | 85    | 5 skills   | Keyword match|
| 2    | ...    | 72    | 3 commands | Description  |
```

## Examples

```bash
/context:plugin:search "terraform development"
/context:plugin:search "blog content creation" --local
/context:plugin:search "security compliance" --top 10
```

## Related Commands

- `/context:plugin:create` - Create a new plugin
- `/context:plugin:review` - Review plugin quality
