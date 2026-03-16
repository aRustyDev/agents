# Research Plan Templates

Research plan templates structure the information gathering phase.

## Default Template

The standard research plan template covers:

```markdown
---
name: standard
description: General-purpose research plan
---

# Research Plan: {{topic}}

## Research Questions

Primary question:

- {{main-question}}

Secondary questions:

- {{question-1}}
- {{question-2}}

## Source Categories

### Primary Sources

- [ ] Official documentation
- [ ] Source code/repositories
- [ ] Original papers/specs

### Secondary Sources

- [ ] Blog posts and tutorials
- [ ] Video content
- [ ] Community discussions

### Tertiary Sources

- [ ] Aggregator sites
- [ ] Curated lists
- [ ] Social media

## Search Strategy

### Keywords

- {{keyword-1}}
- {{keyword-2}}

### Sites to Search

- GitHub
- Official docs
- Stack Overflow
- {{relevant-communities}}

## Verification Criteria

How to validate information:

- [ ] Cross-reference multiple sources
- [ ] Check dates (is it current?)
- [ ] Verify author credentials
- [ ] Test claims if possible

## Expected Outputs

- [ ] List of verified facts
- [ ] Key concepts explained
- [ ] Open questions remaining
- [ ] Source bibliography

## Timeline

- Day 1: Primary sources
- Day 2: Secondary sources
- Day 3: Synthesis and gaps
```

## Using Research Plans

### Create from Template

```bash
/blog/research/spec/draft <project>
```

This creates a research plan from the template.

### Execute the Plan

1. Work through source categories systematically
2. Record findings in `research/sources.md`
3. Synthesize in `research/synthesis.md`
4. Review against criteria

### Review the Research

```bash
/blog/research/review content/_projects/<name>/research/synthesis.md
```

## Customizing Research Plans

### For Technical Topics

Add:

- Code repository analysis
- API documentation review
- Performance benchmarks
- Compatibility matrix

### For Comparisons

Add:

- Feature matrix template
- Pricing research
- Community sentiment analysis
- Migration considerations

### For Tutorials

Add:

- Prerequisites verification
- Step verification (does it work?)
- Common errors research
- Alternative approaches

## Research Artifacts

The research phase produces:

| Artifact | Purpose |
|----------|---------|
| `plan.md` | Research strategy |
| `sources.md` | Collected sources with notes |
| `synthesis.md` | Findings summary |
| `gaps.md` | Unanswered questions |

## Best Practices

1. **Start with primary sources** - Official docs, source code
2. **Date everything** - Note when sources were accessed
3. **Capture quotes** - Direct quotes with page/link
4. **Note credibility** - Author expertise, source reliability
5. **Track time** - Don't rabbit-hole; timebox research
6. **Accept gaps** - Some questions may remain unanswered

## See Also

- [Research Commands](../reference/commands.md#research-phase-commands)
- [Project Lifecycle](../workflow/project-lifecycle.md)
