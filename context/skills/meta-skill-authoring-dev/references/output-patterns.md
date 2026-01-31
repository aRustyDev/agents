# Output Patterns

**Load this reference when:** designing skills that need consistent, high-quality output formats.

## Template Pattern

Provide templates for output format. Match the level of strictness to your needs.

### Strict Requirements

For API responses, data formats, or compliance needs:

```markdown
## Report structure

ALWAYS use this exact template structure:

# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```

### Flexible Guidance

When adaptation is useful:

```markdown
## Report structure

Here is a sensible default format, but use your best judgment:

# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]

## Recommendations
[Tailor to the specific context]

Adjust sections as needed for the specific analysis type.
```

## Examples Pattern

For skills where output quality depends on seeing examples, provide input/output pairs:

```markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

Follow this style: type(scope): brief description, then detailed explanation.
```

Examples help Claude understand the desired style and level of detail more clearly than descriptions alone.

## One Excellent Example Beats Many

**Do:**
- Choose most relevant language for the skill
- Provide complete, runnable code
- Include comments explaining WHY
- Show real-world scenario

**Don't:**
- Implement in 5+ languages
- Create fill-in-the-blank templates
- Write contrived examples

Claude can port patterns between languages - one great example is enough.

## Degrees of Freedom

Match specificity to task fragility:

| Freedom Level | When to Use | Example |
|--------------|-------------|---------|
| **High** | Multiple approaches valid, context-dependent | Code review process |
| **Medium** | Preferred pattern exists, some variation OK | Report generation with template |
| **Low** | Fragile operations, consistency critical | Database migration commands |

### High Freedom (Text Instructions)

```markdown
## Code review process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions
```

### Medium Freedom (Parameterized)

```markdown
## Generate report

Use this template and customize as needed:

```python
def generate_report(data, format="markdown", include_charts=True):
    # Process data
    # Generate output in specified format
    # Optionally include visualizations
```
```

### Low Freedom (Exact Commands)

```markdown
## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
```

Think of Claude as exploring a path:
- **Narrow bridge with cliffs**: Specific guardrails, exact instructions (low freedom)
- **Open field with no hazards**: General direction, trust Claude to navigate (high freedom)
