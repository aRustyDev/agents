# Personas Concept

A persona defines the voice, tone, and style characteristics for your writing. Personas help maintain consistency across posts and make style decisions explicit rather than implicit.

## Why Use Personas?

### Consistency

Without a persona, writing style drifts:

- Some posts formal, some casual
- Inconsistent use of "I" vs "we" vs passive voice
- Varying levels of technical jargon

### Intentional Voice

A persona makes you think about:

- Who am I writing as?
- How do I want to come across?
- What's my relationship with the reader?

### Reusability

Define once, apply to many posts. Switch personas for different contexts.

## Persona Components

### Voice Characteristics

- **Tone**: Casual, professional, academic
- **Perspective**: First person (I), first plural (we), second person (you)
- **Formality**: Contractions? Colloquialisms?

### Style Guidelines

- **Sentence structure**: Short and punchy? Complex and nuanced?
- **Vocabulary level**: Beginner-friendly? Expert assumed?
- **Technical detail**: Explain everything? Assume knowledge?

### Example Phrases

Concrete examples of how the persona writes:

- How to introduce a topic
- How to explain something
- How to conclude

## Built-in Personas

### Practitioner

The experienced professional sharing what works:

- First person ("I use...", "In my experience...")
- Practical focus
- Battle-tested advice

See [Practitioner Persona](./practitioner.md)

### Educator

The patient teacher explaining concepts:

- Second person ("You'll want to...", "Notice how...")
- Step-by-step guidance
- Anticipates confusion

See [Educator Persona](./educator.md)

## Creating Custom Personas

Create new personas in `content/_templates/personas/`:

```markdown
---
name: researcher
description: Academic voice for research-oriented content
---

## Voice

- Third person, passive voice acceptable
- Formal, precise language
- Citations expected

## Style

- Complex sentence structures okay
- Define terms formally
- Hedge appropriately ("suggests", "indicates")

## Examples

- "The results indicate that..."
- "This finding aligns with prior work by..."
- "Further investigation is warranted."
```

## Applying Personas

Specify persona when drafting:

```bash
/blog/post/draft --persona practitioner
```

Or set in project configuration for all posts in a project.
