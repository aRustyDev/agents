---
name: blog/template/plan
description: Refine a template with detailed guidance, examples, and word counts
argument-hint: <path>
arguments:
  - name: path
    description: Path to the template file to refine
    required: true
---

# Template Plan

Refine an existing template draft with detailed section guidance, examples, and common mistakes.

## Behavior

1. **Load existing template** from provided path

2. **Add word count guidance**:
   - Set target word count per section
   - Set total target range
   - Note which sections can flex

3. **Add example content snippets**:
   - Provide 1-2 sentence examples for each section
   - Show what good content looks like
   - Demonstrate expected depth/style

4. **Add "Common Mistakes" notes**:
   - List pitfalls for each section
   - Include scope creep warnings
   - Note tone/style issues to avoid

5. **Add section dependencies**:
   - Note which sections reference others
   - Identify setup/payoff relationships
   - Mark sections that should be written together

6. **Update timestamps**:
   - Set `updated` to current ISO 8601

## Output

```text
Refined template: <path>

Added:
- Word count targets (total: X-Y words)
- Example snippets for Z sections
- X common mistake warnings
- Section dependency notes

Next: Run `blog:template:review <path> "sample topic"` to dry-run
```

## Example

**Input**: `blog:template:plan .templates/outlines/case-study.outline.md`

**Output**:

```text
Refined template: .templates/outlines/case-study.outline.md

Added:
- Word count targets (total: 1800-2700 words)
- Example snippets for 5 sections
- 4 common mistake warnings
- 3 section dependency notes

Word Counts:
- Problem Statement: 200-300 (required)
- Context & Constraints: 300-400 (required)
- Technical Approach: 500-800 (required, main body)
- Alternative Approaches: 200-300 (optional)
- Results & Metrics: 300-400 (required)
- Lessons Learned: 200-300 (required)
- Future Improvements: 100-200 (optional)

Common Mistakes Added:
1. Problem Statement: Don't bury the problem in context
2. Technical Approach: Avoid implementation details without explaining why
3. Results: Numbers without context are meaningless
4. Lessons Learned: "We should have planned better" is not actionable

Dependencies:
- Results must reference metrics promised in Problem Statement
- Lessons Learned should connect to Context & Constraints
- Alternative Approaches should explain why Technical Approach was chosen

Next: Run `blog:template:review .templates/outlines/case-study.outline.md "Migrating to Kubernetes"` to dry-run
```
