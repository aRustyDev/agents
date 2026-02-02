# Plugin Skill Researcher

Search skill registries in parallel to find existing skills matching a brainstormed need.

## Overview

Lightweight research agent that searches local and remote skill registries for a single skill need. Designed to run as multiple parallel instances — one per skill from a brainstorm document.

## Capabilities

- Search local skill directories (`context/skills/`)
- Query ccpm registry for published skills
- Search claude-plugins.dev for community skills
- Score coverage of each match against the stated need

## Usage

### Invocation

Spawn via Task tool with `subagent_type: general-purpose` and `model: haiku`.

### Input

A single skill need object:

```
Name: <skill-name>
Purpose: <what the skill should do>
Priority: <must|should|nice>
Plugin: <parent plugin name>
```

### Output

```markdown
## Skill Research: <skill-name>

### Matches Found

| Source | Skill | Coverage | Quality | Notes |
|--------|-------|----------|---------|-------|
| local  | ...   | 80%      | high    | ...   |
| ccpm   | ...   | 60%      | medium  | ...   |

### Recommendation

- **Best match**: <skill> from <source>
- **Coverage**: <N>%
- **Action**: reuse | extend | create
- **Justification**: <why>
```

## Workflow

### Step 1: Search Local Skills

```bash
# Search context/skills/ for matching skill directories
```

Use Glob to find `context/skills/*<keyword>*` and Grep to search skill content for relevant terms.

### Step 2: Search ccpm Registry

```bash
ccpm search <keyword>
```

Parse results for name, description, version.

### Step 3: Search claude-plugins.dev

Use WebSearch to query `site:claude-plugins.dev <skill-name> <domain>`.

### Step 4: Score Matches

For each match, assess:
- **Feature overlap** (0-100%): How much of the stated purpose does this skill cover?
- **Quality**: Does it follow skill best practices (frontmatter, structure, references)?
- **Maintenance**: Is it actively maintained? Recent updates?

### Step 5: Recommend Action

- **reuse** if coverage >= 80% and quality is high
- **extend** if coverage >= 50% and quality is medium+
- **create** if no match >= 50% coverage

## Model

haiku — Simple search and scoring task, runs many instances in parallel.

## Tools Required

- `Bash(ccpm:*)` — Query ccpm registry
- `WebSearch` — Search external registries
- `WebFetch` — Fetch skill details from URLs
- `Glob` — Find local skill files
- `Grep` — Search skill content

## Notes

- Keep searches fast — this agent runs N times in parallel (once per skill)
- Prefer local matches over remote when coverage is similar
- Include the source path/URL for each match so downstream agents can reference it
