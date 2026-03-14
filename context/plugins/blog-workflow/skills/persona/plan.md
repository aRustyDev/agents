---
name: blog:persona:plan
description: Refine an existing persona with expanded examples and voice phrases
arguments:
  - name: path
    description: Path to the persona file to refine
    required: true
---

# Persona Plan

Refine an existing persona draft with expanded examples, voice phrases, and review criteria.

## Behavior

1. **Load existing persona** from provided path

2. **Expand Voice Phrases**:
   - Generate 5-10 characteristic expressions
   - Include sentence starters, transitions, and conclusions
   - Examples: "In my experience...", "The tradeoff here is...", "I've seen this fail when..."

3. **Expand Avoid Phrases**:
   - Generate 5-10 expressions to never use
   - Include jargon that breaks persona, wrong tone markers
   - Examples: "It is recommended that...", "Stakeholders should...", "Best practices dictate..."

4. **Generate additional examples**:
   - Create 3-5 good/bad example pairs
   - Cover different content types (intro, explanation, conclusion)
   - Show voice in technical and non-technical contexts

5. **Expand Review Criteria**:
   - Add specific testable questions
   - Include edge case considerations
   - Examples: "Would this persona use bullet points or prose?", "How would they handle admitting a mistake?"

6. **Update timestamps**:
   - Set `updated` to current ISO 8601

7. **Run self-review**:
   - Check against `.templates/review-checklists/persona.md`

## Output

```text
Refined persona: <path>

Added:
- X voice phrases (total: Y)
- X avoid phrases (total: Y)
- X example pairs (total: Y)
- X review criteria (total: Y)

Self-review: [passed | X issues found]

Next: Run `blog:persona:review <path>` to validate refinements
```

## Example

**Input**: `blog:persona:plan .templates/personas/skeptical-engineer.md`

**Output**:

```text
Refined persona: .templates/personas/skeptical-engineer.md

Added:
- 7 voice phrases (total: 9)
- 6 avoid phrases (total: 8)
- 4 example pairs (total: 5)
- 3 review criteria (total: 6)

Voice Phrases Added:
- "Before we go further, let's look at the failure modes..."
- "I've been burned by this exact pattern before..."
- "The benchmarks look good, but production is different..."
- "Show me the rollback plan first..."
- "What happens when this fails at 3am?"
- "I'm not saying don't do it, but..."
- "Let's see if this holds up under load..."

Self-review: passed

Next: Run `blog:persona:review .templates/personas/skeptical-engineer.md` to validate
```
