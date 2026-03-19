---
name: blog:template:review
description: Dry-run a template against a sample topic to validate fit
argument-hint: <path> "<topic>"
arguments:
  - name: path
    description: Path to the template file to review
    required: true
  - name: topic
    description: Sample topic to test the template against
    required: true
---

# Template Review

Validate a template by applying it to a sample topic and checking for fit issues.

## Behavior

1. **Load template** from provided path

2. **Apply to sample topic**:
   - Fill each section with example content for the topic
   - Write 2-3 sentences per section (not full content)
   - Show how the topic maps to structure

3. **Evaluate section fit**:
   - Does each section make sense for this topic?
   - Are required sections appropriate?
   - Do optional sections add value?

4. **Check flow and transitions**:
   - Does the structure create logical progression?
   - Are there gaps in the narrative?
   - Do sections connect naturally?

5. **Identify improvements**:
   - Sections that could be split
   - Sections that could be combined
   - Missing sections for this topic type
   - Sections that feel forced

6. **Generate fit score**:
   - Good fit, Adequate fit, or Poor fit
   - Recommendations for template updates

## Output

```text
## Template Dry-Run: <template name>
Topic: "<sample topic>"

### Section Fit Analysis

| Section | Fit | Notes |
|---------|-----|-------|
| <section> | good/adequate/poor | <notes> |

### Sample Content

#### <Section 1>
<2-3 sentences showing how topic maps to this section>

#### <Section 2>
...

### Flow Analysis

- [x] Logical progression — pass/fail
- [x] No narrative gaps — pass/fail
- [x] Natural transitions — pass/fail

### Suggestions

1. <improvement suggestion>
2. <improvement suggestion>

### Summary

Fit: [Good | Adequate | Poor]
Recommended: [Use as-is | Minor tweaks | Significant revision]
```

## Example

**Input**: `blog:template:review .templates/outlines/case-study.outline.md "Migrating 10M users from MySQL to PostgreSQL"`

**Output**:

```text
## Template Dry-Run: case-study.outline.md
Topic: "Migrating 10M users from MySQL to PostgreSQL"

### Section Fit Analysis

| Section | Fit | Notes |
|---------|-----|-------|
| Problem Statement | good | Clear problem: need to migrate |
| Context & Constraints | good | Can cover scale, downtime limits, team size |
| Technical Approach | good | Migration strategy, tooling, testing |
| Alternative Approaches | good | Why not stay? Why not different DB? |
| Results & Metrics | good | Performance, downtime, data integrity |
| Lessons Learned | good | What would you do differently |
| Future Improvements | adequate | May feel thin for a migration |

### Sample Content

#### Problem Statement
Our MySQL 5.7 instance was hitting performance limits at 10M users. Query
times degraded during peak hours, and we'd exhausted vertical scaling options.
We needed a path to PostgreSQL without significant downtime.

#### Context & Constraints
Zero data loss tolerance. Maximum 4 hours downtime. Team of 3 engineers.
Existing application used MySQL-specific features. Budget for managed services.

#### Technical Approach
Dual-write architecture with pgloader for initial sync. Feature flags for
gradual traffic shift. Extensive shadow testing before cutover...

### Flow Analysis

- [x] Logical progression — pass: problem → context → solution → results
- [x] No narrative gaps — pass: each section sets up the next
- [~] Natural transitions — warn: jump from Technical to Alternative may feel abrupt

### Suggestions

1. Consider adding "Risk Mitigation" subsection under Technical Approach
2. "Future Improvements" could be folded into "Lessons Learned" for migrations
3. Add optional "Timeline" section for multi-phase migrations

### Summary

Fit: Good
Recommended: Use as-is (minor transition smoothing)
```
