---
name: blog/persona/review
description: Test a persona against sample content and validate consistency
argument-hint: <path>
arguments:
  - name: path
    description: Path to the persona file to review
    required: true
---

# Persona Review

Evaluate a persona for clarity, consistency, and usability by generating sample content.

## Behavior

1. **Load persona** from provided path

2. **Load checklist** from `.templates/review-checklists/persona.md`

3. **Evaluate each criterion**:
   - Mark as pass, warn, or fail
   - Provide brief justification

4. **Generate sample content**:
   - Create a paragraph (100-150 words) that matches the persona
   - Create a paragraph that deliberately violates the persona

5. **Interactive validation** (optional):
   - Present both samples unlabeled
   - Ask user to identify which matches
   - Confirm understanding of persona

6. **Generate consistency score**:
   - Based on checklist results
   - Note any ambiguous areas

## Output

```text
## Persona Review: <name>

### Checklist Evaluation

#### Voice Clarity
- [x] Voice characteristics are specific — pass
- [x] Voice examples demonstrate style — pass
- [x] Voice is distinct from others — pass/warn/fail

#### Tone Consistency
- [x] Tone descriptors are clear — pass
- [x] Tone matches intended audience — pass
- [x] No contradictory tone elements — pass

#### Expertise Authenticity
- [x] Expertise level is defined — pass
- [x] Expertise indicators are realistic — pass
- [x] Writing can credibly demonstrate expertise — pass

#### Examples Quality
- [x] Good example clearly matches persona — pass
- [x] Bad example clearly violates persona — pass
- [x] Examples are distinct — pass

#### Practical Usability
- [x] Review criteria are testable — pass
- [x] Persona can be applied consistently — pass
- [x] No ambiguous guidance — pass

### Sample Content Test

**Sample A:**
"<generated paragraph matching persona>"

**Sample B:**
"<generated paragraph violating persona>"

Which sample matches the persona? [User identifies A or B]

### Summary

- Pass: X
- Warn: Y
- Fail: Z

Review: [passed | needs refinement]
```

## Example

**Input**: `blog:persona:review .templates/personas/skeptical-engineer.md`

**Output**:

```text
## Persona Review: skeptical-engineer

### Checklist Evaluation

#### Voice Clarity
- [x] Voice characteristics are specific — pass: "direct, questioning, evidence-based" is actionable
- [x] Voice examples demonstrate style — pass: examples show skepticism clearly
- [x] Voice is distinct from others — pass: different from educator/practitioner

#### Tone Consistency
- [x] Tone descriptors are clear — pass
- [x] Tone matches intended audience — pass: appropriate for technical readers
- [x] No contradictory tone elements — pass

#### Expertise Authenticity
- [x] Expertise level is defined — pass: senior engineer level clear
- [x] Expertise indicators are realistic — pass
- [x] Writing can credibly demonstrate expertise — pass

#### Examples Quality
- [x] Good example clearly matches persona — pass
- [x] Bad example clearly violates persona — pass
- [x] Examples are distinct — pass

#### Practical Usability
- [x] Review criteria are testable — pass
- [x] Persona can be applied consistently — pass
- [~] No ambiguous guidance — warn: "cautiously critical" could be clearer

### Sample Content Test

**Sample A:**
"I've tested this approach in three production systems. The benchmarks look
impressive, but I'm not convinced about the failure modes. What happens when
the network partitions? Show me the rollback plan before we go further."

**Sample B:**
"This revolutionary paradigm shift will transform how we architect distributed
systems. By leveraging cutting-edge methodologies, organizations can achieve
unprecedented scalability and unlock new value streams."

Which sample matches the persona? A ✓

### Summary

- Pass: 14
- Warn: 1
- Fail: 0

Review: passed
```
