# Skill Structure Analysis

Analysis of convert-* skill structure based on manual sampling of 5 representative skills.

## Sample Set

| Skill | Direction | Family Transition | Lines |
|-------|-----------|-------------------|-------|
| convert-python-rust | Dynamic → Systems | Python → Rust | ~1871 |
| convert-python-haskell | Dynamic → ML-FP | Python → Haskell | ~1800 |
| convert-c-cpp | Systems → Systems | C → C++ | ~1672 |
| convert-elixir-erlang | BEAM → BEAM (bidirectional) | Elixir ↔ Erlang | ~1203 |
| convert-python-fsharp | Dynamic → ML-FP | Python → F# | ~837 |

## Observed Sections

All sampled skills follow a consistent structure derived from `meta-convert-dev`:

### 1. YAML Frontmatter
```yaml
---
name: convert-<source>-<target>
description: <one-line description with context and use cases>
---
```
- **Purpose**: Metadata for skill discovery and cataloging
- **Pattern**: All skills include name and description
- **Notes**: Bidirectional skills use `↔` in description

### 2. Title (H1)
```markdown
# Convert <Source> to <Target>
# OR
# <Source> ↔ <Target> Conversion
```
- **Purpose**: Human-readable title
- **Pattern**: Bidirectional skills indicate both directions

### 3. Introduction Paragraph
- **Purpose**: Brief overview of the conversion
- **Content**: Source/target characteristics, difficulty level, key challenges
- **Pattern**: 2-4 sentences summarizing the conversion

### 4. This Skill Extends
```markdown
## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)
```
- **Purpose**: Declares parent skill dependency
- **Pattern**: All convert-* skills extend meta-convert-dev
- **Content**: Reference to parent with brief description

### 5. This Skill Adds
```markdown
## This Skill Adds

- **Type mappings**: Source types → Target types
- **Idiom translations**: Source patterns → Target idioms
- **Error handling**: Source model → Target model
- ...
```
- **Purpose**: Lists unique contributions of this skill
- **Pattern**: Bulleted list with bold category labels
- **Typical Categories**:
  - Type mappings
  - Idiom translations
  - Error handling patterns
  - Async/concurrency patterns
  - Memory/ownership patterns (for systems languages)
  - Tooling differences

### 6. This Skill Does NOT Cover
```markdown
## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- <Source> language fundamentals - see `lang-<source>-dev`
- <Target> language fundamentals - see `lang-<target>-dev`
- Reverse conversion - see `convert-<target>-<source>`
```
- **Purpose**: Explicit scope boundaries (negative patterns)
- **Pattern**: Bulleted list with cross-references to related skills
- **Value for IR**: Defines what the skill explicitly excludes

### 7. Quick Reference (Table)
```markdown
## Quick Reference

| <Source> | <Target> | Notes |
|----------|----------|-------|
| `int` | `i32` | Fixed-size integer |
| `list` | `Vec<T>` | Dynamic array |
```
- **Purpose**: At-a-glance type mapping reference
- **Pattern**: 3-column table (source, target, notes)
- **Density**: 15-30 common mappings

### 8. When Converting Code
```markdown
## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Embrace immutability** - F# defaults to immutable
...
```
- **Purpose**: High-level workflow guidelines
- **Pattern**: Numbered list with bold lead-ins
- **Content**: Strategic advice, not tactical details

### 9. Type System Mapping
```markdown
## Type System Mapping

### Primitive Types
| Source | Target | Notes |

### Collection Types
| Source | Target | Notes |

### Composite Types
| Source | Target | Notes |

### Function Types (optional)
| Source | Target | Notes |
```
- **Purpose**: Comprehensive type mapping reference
- **Pattern**: Subsections with tables
- **Subsections observed**:
  - Primitive Types (always present)
  - Collection Types (always present)
  - Composite Types (always present)
  - Function Types (often present)
  - Generics / Type Parameters (sometimes present)

### 10. Idiom Translation
```markdown
## Idiom Translation

### Pattern 1: <Name>
### Pattern 2: <Name>
...
### Pattern N: <Name>
```
OR (alternative naming):
```markdown
### Pillar 1: <Name>
### Pillar 2: <Name>
```
- **Purpose**: Core transformation patterns
- **Pattern**: Numbered patterns/pillars with consistent structure
- **Count**: 8-10 patterns per skill
- **Structure per pattern**:
  - Before (Source) code block
  - After (Target) code block
  - "Why this translation:" explanation

### 11. Error Handling
```markdown
## Error Handling

### Source Error Model
### Target Error Model
### Error Translation Patterns
```
- **Purpose**: Error model mapping and best practices
- **Pattern**: Comparison tables and code examples
- **Content**: Exception types, Result/Option types, error propagation

### 12. Concurrency Patterns (if applicable)
```markdown
## Concurrency Patterns

### Async Model Comparison
### Threading Patterns
### Channel/Message Passing
```
- **Purpose**: Async/concurrent code translation
- **Pattern**: Present for languages with significant concurrency differences
- **Content**: async/await mapping, threading models, synchronization

### 13. Memory & Ownership (for systems targets)
```markdown
## Memory & Ownership

### Ownership Model
### Lifetime Annotations
### Smart Pointers
```
- **Purpose**: Memory management translation (Python→Rust, C→Rust)
- **Pattern**: Only present when target has manual/ownership-based memory
- **Content**: Reference semantics, borrowing, lifetimes

### 14. Common Pitfalls
```markdown
## Common Pitfalls

### 1. <Pitfall Name>
**Problem:** Description
**Solution:** Resolution

### 2. <Pitfall Name>
...
```
- **Purpose**: Warn about common conversion mistakes
- **Pattern**: Numbered sections with Problem/Solution structure
- **Count**: 5-8 pitfalls per skill
- **Value for IR**: Anti-patterns and negative guidance

### 15. Tooling
```markdown
## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| `cargo` | Build system | Replaces pip/poetry |
```
- **Purpose**: Development tooling mapping
- **Pattern**: Table mapping source tools to target equivalents
- **Categories**: Build, test, format, lint, debug, REPL

### 16. Examples
```markdown
## Examples

### Example 1: Simple - <Description>
**Before (Source):**
```<source-lang>
...
```
**After (Target):**
```<target-lang>
...
```

### Example 2: Medium - <Description>
### Example 3: Complex - <Description>
```
- **Purpose**: Complete conversion examples at varying complexity
- **Pattern**: 3 examples (Simple, Medium, Complex)
- **Structure per example**:
  - Before code block (source language)
  - After code block (target language)
  - Optional explanation of key decisions

### 17. See Also
```markdown
## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns
- `convert-<related>` - Related conversions
- `lang-<source>-dev` - Source language patterns
- `lang-<target>-dev` - Target language patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev`
- `patterns-serialization-dev`
```
- **Purpose**: Cross-references to related skills
- **Pattern**: Bulleted lists organized by category
- **Categories**: Parent skill, related conversions, language skills, pattern skills

## Section Frequency

| Section | Required | Notes |
|---------|----------|-------|
| Frontmatter | Yes | All skills |
| Title | Yes | All skills |
| This Skill Extends | Yes | All skills |
| This Skill Adds | Yes | All skills |
| This Skill Does NOT Cover | Yes | All skills |
| Quick Reference | Yes | All skills |
| When Converting Code | Yes | All skills |
| Type System Mapping | Yes | All skills |
| Idiom Translation | Yes | Core content, 8-10 patterns |
| Error Handling | Yes | All skills |
| Concurrency Patterns | Conditional | When languages differ significantly |
| Memory & Ownership | Conditional | For systems language targets |
| Common Pitfalls | Yes | 5-8 pitfalls |
| Tooling | Yes | All skills |
| Examples | Yes | 3 examples (Simple/Medium/Complex) |
| See Also | Yes | All skills |

## Extractable Pattern Types

Based on the structure analysis, the following pattern types can be extracted:

### 1. Type Mappings
- **Source**: Quick Reference, Type System Mapping sections
- **Format**: `(source_type, target_type, notes, confidence)`
- **Volume**: ~50-100 per skill

### 2. Idiom Patterns
- **Source**: Idiom Translation section
- **Format**: `(name, source_code, target_code, explanation, category)`
- **Volume**: 8-10 per skill

### 3. Error Handling Patterns
- **Source**: Error Handling section
- **Format**: `(source_pattern, target_pattern, when_to_use)`
- **Volume**: 3-5 per skill

### 4. Negative Patterns (Anti-patterns)
- **Source**: Common Pitfalls, This Skill Does NOT Cover
- **Format**: `(pitfall, problem, solution)`
- **Volume**: 5-8 pitfalls + scope boundaries

### 5. Guidelines
- **Source**: When Converting Code section
- **Format**: `(guideline, rationale, priority)`
- **Volume**: 5-8 per skill

### 6. Tool Recommendations
- **Source**: Tooling section
- **Format**: `(source_tool, target_tool, purpose)`
- **Volume**: 5-10 per skill

### 7. Scope Boundaries
- **Source**: This Skill Does NOT Cover
- **Format**: `(excluded_topic, alternative_skill)`
- **Volume**: 3-5 per skill

### 8. Cross-References
- **Source**: See Also, This Skill Extends
- **Format**: `(referenced_skill, relationship_type)`
- **Volume**: 5-10 per skill

## Parent Skill Patterns (meta-convert-dev)

All skills reference `meta-convert-dev` as parent. Key patterns inherited:

1. **APTV Workflow**: Analyze → Plan → Transform → Validate
2. **Testing Strategies**: Input/output equivalence testing
3. **General Pitfalls**: Over-engineering, premature optimization
4. **Cross-language Concepts**: Types, functions, modules

## Bidirectional Skill Observations

`convert-elixir-erlang` demonstrates bidirectional structure:

1. **Title uses `↔`**: "Elixir ↔ Erlang Conversion"
2. **Description mentions both directions**: "Bidirectional conversion between..."
3. **Type mappings are reversible**: Same table works in both directions
4. **Idiom patterns show both directions**: Each pattern has Elixir→Erlang and implicitly Erlang→Elixir

For bidirectional skills, pattern extraction should:
- Extract patterns in both directions
- Note which patterns are symmetric vs. asymmetric
- Track any direction-specific guidelines

## Recommendations for Pattern Extraction (Task 0.1)

1. **Structural Parsing**: Markdown headings reliably demarcate sections
2. **Table Extraction**: Type mapping tables have consistent 3-column format
3. **Code Block Extraction**: Fenced code blocks with language annotations
4. **Pattern Detection**: "Pattern N:" or "Pillar N:" prefixes identify idioms
5. **LLM-Assisted**: "Why this translation:" explanations need semantic parsing
6. **Confidence Scoring**: Based on structural clarity and completeness

## File Deliverable

This document serves as the deliverable for Task 0.0 (Skill Structure Analysis) and provides the foundation for building the pattern extraction tooling in Task 0.1.
