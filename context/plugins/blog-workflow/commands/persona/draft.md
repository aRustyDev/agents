---
name: blog:persona:draft
description: Create a new authorial persona through voice discovery conversation
argument-hint: [name]
arguments:
  - name: name
    description: Short name/slug for the persona (optional, will prompt if not provided)
    required: false
---

# Persona Draft

Create a new authorial persona through an interactive voice discovery conversation.

## Behavior

1. **Get persona name**:
   - If name provided as argument, use it
   - Otherwise prompt: "What should we call this persona? (e.g., 'skeptic', 'mentor', 'explorer')"

2. **Voice discovery conversation**:
   - "How do you want to sound? Formal, casual, technical, conversational?"
   - "What's your relationship with the reader? Peer, teacher, guide?"
   - "What pronouns? 'I/you', 'we', impersonal?"

3. **Tone discovery**:
   - "What emotional register? Confident, curious, cautious?"
   - "How do you handle uncertainty? Acknowledge it, hedge, or assert?"
   - "What's your attitude toward complexity? Embrace or simplify?"

4. **Expertise discovery**:
   - "What level of expertise are you demonstrating?"
   - "Do you reference personal experience? How?"
   - "How do you handle topics outside your expertise?"

5. **Generate persona** from `.templates/persona.md`:
   - Fill Voice, Tone, Expertise sections from conversation
   - Generate 2-3 Voice Phrases (characteristic expressions)
   - Generate 2-3 Avoid Phrases (expressions that break persona)
   - Create Review Criteria as questions

6. **Prompt for examples**:
   - "Give me an example sentence in this voice (or I'll generate one)"
   - "Give me an example of what this persona would NOT say"

7. **Run self-review** against `.templates/review-checklists/persona.md`:
   - Check fail items only
   - Report any issues

## Output

```text
Created persona: .templates/personas/<slug>.md

Voice: <summary>
Tone: <summary>
Expertise: <summary>

Self-review: [passed | X issues found]

Next steps:
1. Refine with more examples: blog:persona:plan .templates/personas/<slug>.md
2. Test against sample: blog:persona:review .templates/personas/<slug>.md
```

## Example

**Input**: `blog:persona:draft skeptical-engineer`

**Conversation**:

```text
Creating persona: skeptical-engineer

Voice Discovery:
> How do you want to sound?
"Direct and questioning. I want to sound like someone who's been burned before."

> What's your relationship with the reader?
"Peer. We're both figuring this out, but I've seen some things."

Tone Discovery:
> What emotional register?
"Cautiously optimistic. I want good solutions but I've seen too many fail."

...
```

**Output**:

```text
Created persona: .templates/personas/skeptical-engineer.md

Voice: Direct, questioning, evidence-based
Tone: Cautiously critical, pragmatic
Expertise: Senior engineer who's seen failures

Self-review: passed

Next steps:
1. Refine with more examples: blog:persona:plan .templates/personas/skeptical-engineer.md
2. Test against sample: blog:persona:review .templates/personas/skeptical-engineer.md
```
