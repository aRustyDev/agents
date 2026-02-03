## Graph neighborhood clustering example

**Imagine two agents**: code-reviewer and pr-analyzer. Their SKILL.md content is quite different — one talks about "code quality" and "best practices", the other about "pull request workflow" and "diff analysis". Vector similarity of their content: 0.4 (not very similar).

But look at their graph neighborhoods:

```asciidoc
  code-reviewer                    pr-analyzer
      │                                │
      ├── uses: eslint-mcp             ├── uses: eslint-mcp
      ├── uses: github-mcp             ├── uses: github-mcp
      ├── uses: code-index-mcp         ├── uses: code-index-mcp
      ├── extends: code-quality-rule   ├── extends: code-quality-rule
      └── output-style: technical      └── output-style: technical
```

**Neighborhood Jaccard similarity**: 5/5 = 1.0 (identical).

What this tells you: These agents are functionally redundant — they operate in the same ecosystem, use the same tools, follow the same rules. One should probably be deprecated or merged, despite their content looking different.

SQL approach (painful):
```sql
-- Get all neighbors of agent A
-- Get all neighbors of agent B
-- Compute intersection / union
-- Repeat for all agent pairs: O(n² * avg_degree)
```

Graph DB approach:
```cypher
MATCH (a:Agent)-[r1]->(shared)<-[r2]-(b:Agent)
WHERE a.id < b.id
WITH a, b, COUNT(DISTINCT shared) AS common,
      SIZE((a)--()) AS a_degree,
      SIZE((b)--()) AS b_degree
RETURN a.name, b.name,
        common * 1.0 / (a_degree + b_degree - common) AS jaccard
ORDER BY jaccard DESC
```

This is where a graph DB genuinely helps — not for the traversal itself, but for the neighborhood comparison operation.
