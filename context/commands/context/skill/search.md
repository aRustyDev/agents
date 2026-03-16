---
description: Search for skills matching a purpose or capability need
argument-hint: '"<purpose>" [--local] [--top N]'
allowed-tools: Read, Glob, Grep, Bash(sqlite3:*), Task
---

# Search Skills

Find skills matching a stated purpose or capability need. Searches local project skills first, then the knowledge graph.

## Arguments

- `$1` - Purpose description in quotes. Example: `"terraform infrastructure patterns"`
- `--local` - Search only local project skills
- `--top N` - Number of results to return (default: 5)

## Workflow

### Step 1: Search Local Skills

Search for skills in the current project:

```text
Glob: .claude/skills/*/SKILL.md
Glob: context/skills/*/SKILL.md
Glob: context/plugins/*/skills/*/SKILL.md
```

For each SKILL.md found:

1. Read the frontmatter (name, description, triggers)
2. Grep for keywords from the purpose string
3. Score based on keyword matches

### Step 2: Search Knowledge Graph (unless --local)

If `.data/mcp/knowledge-graph.db` exists, query it:

```bash
sqlite3 -json .data/mcp/knowledge-graph.db "
  SELECT e.id, e.type, e.name, e.description, e.path
  FROM entities e
  JOIN entities_fts f ON e.id = f.rowid
  WHERE e.type = 'skill' AND entities_fts MATCH '<keywords>'
  ORDER BY rank
  LIMIT 20;
"
```

### Step 3: Search Context Library

Search the shared context library:

```text
Glob: context/.context/*/skills/*/SKILL.md
Glob: context/skills/*/SKILL.md
```

### Step 4: Rank Results

Score each match:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Name match | 30 pts | Purpose keywords in skill name |
| Description match | 25 pts | Purpose keywords in description |
| Trigger match | 25 pts | Purpose keywords in triggers |
| Content match | 20 pts | Purpose keywords in body |

Sort by total score descending. Take top N.

### Step 5: Present Results

```markdown
## Skill Search: "<purpose>"

### Matches

#### 1. <skill-name> (<score>/100)

| Field | Value |
|-------|-------|
| Path | <path> |
| Description | <desc> |
| Triggers | <triggers> |

---

(repeat for each result)

### Summary

| Rank | Skill | Score | Path | Match Reason |
|------|-------|-------|------|--------------|
| 1    | ...   | 85    | ...  | Name match   |
| 2    | ...   | 72    | ...  | Trigger match|
```

## Examples

```bash
/context:skill:search "kubernetes deployment patterns"
/context:skill:search "code conversion between languages" --local
/context:skill:search "terraform best practices" --top 10
```

## Related Commands

- `/context:skill:create` - Create a new skill
- `/context:skill:review` - Review skill quality
