# Agents

Agents are specialized assistants that handle specific workflow tasks.

## Available Agents

The blog-workflow plugin includes these agents:

| Agent | Purpose |
|-------|---------|
| [Research Synthesizer](./research-synthesizer.md) | Synthesize research findings |
| [Series Architect](./series-architect.md) | Plan multi-part series |
| [Technical Editor](./technical-editor.md) | Review technical accuracy |

## What is an Agent?

An agent is a specialized role that:

- Focuses on specific workflow tasks
- Has defined inputs and outputs
- Follows consistent patterns
- Can be invoked during workflow phases

## Using Agents

Agents are invoked during specific workflow phases:

### Research Synthesizer

Used after research gathering:

- Input: Raw sources and notes
- Output: Structured synthesis document
- Phase: Research → Content Planning

### Series Architect

Used when planning multi-part content:

- Input: Topic and scope
- Output: Series structure and part breakdown
- Phase: Idea → Research (for series)

### Technical Editor

Used during review:

- Input: Draft content
- Output: Technical accuracy feedback
- Phase: Post Review

## Agent Invocation

Agents are invoked via workflow commands:

```bash
# Invoke research synthesizer
/blog/research/draft <project>

# Invoke series architect
/blog/series/create <name>

# Invoke technical editor
/blog/post/review <draft> --agent technical-editor
```

## Agent Structure

Each agent definition includes:

1. **Role** - What the agent does
2. **Inputs** - Required information
3. **Outputs** - Expected deliverables
4. **Process** - How the agent works
5. **Quality Criteria** - Success measures

## Creating Custom Agents

To create a custom agent:

1. Create agent file in `agents/`
2. Define role, inputs, outputs
3. Document process steps
4. Add quality criteria

Example agent structure:

```markdown
---
name: fact-checker
role: Verify factual claims in content
---

## Inputs

- Draft content with factual claims
- Source references

## Process

1. Identify factual claims
2. Verify against sources
3. Flag unverified claims
4. Suggest corrections

## Outputs

- List of verified claims
- List of unverified claims
- Correction suggestions

## Quality Criteria

- All claims checked
- Sources cited
- Clear verification status
```

## See Also

- [Research Synthesizer](./research-synthesizer.md)
- [Series Architect](./series-architect.md)
- [Technical Editor](./technical-editor.md)
