# Implementation Plan: Address Remaining Feedback Gaps

## Overview

This plan addresses the remaining gaps identified in feedback issues for `meta-convert-dev` and `create-lang-conversion-skill`.

## Gaps to Address

### meta-convert-dev Gaps

| Gap | Related Issues | Priority |
|-----|----------------|----------|
| Metaprogramming Translation Section | #215 (partial) | High |
| Serialization Patterns Section | #208, #209 | High |
| TypeScript-Specific Patterns | #215 | Medium |
| Advanced Feature Templates (HKTs, type classes) | #344 | Medium |

### create-lang-conversion-skill Gaps

| Gap | Related Issues | Priority |
|-----|----------------|----------|
| Reverse Skill Check Step | #345, #350 | High |
| Difficulty Rating Guidance | #217 | Medium |

## Implementation

### Phase 1: meta-convert-dev Additions

#### 1.1 Metaprogramming Translation Section (after line ~1001)

Add comprehensive section covering:
- Decorator → Attribute/Annotation mapping
- Macro system differences (hygienic vs unhygienic)
- Reflection/introspection capabilities
- Code generation patterns
- Mixin translation strategies
- DI container patterns

#### 1.2 Serialization Patterns Section (after Metaprogramming)

Add section covering:
- JSON serialization library mapping
- Custom serializer patterns
- Validation patterns (Zod → Pydantic → validator)
- Schema generation
- Migration strategies between formats

#### 1.3 TypeScript-Specific Patterns (new subsection)

Add language-specific patterns section covering:
- Type guards → pattern matching
- Discriminated unions
- Decorators → attributes
- Advanced generics (conditional types, mapped types)

### Phase 2: create-lang-conversion-skill Additions

#### 2.1 Reverse Skill Check (Step 0.5 or enhance Step 0)

Add explicit step to check if `convert-$2-$1` exists:
- If exists: Reference it for bidirectional insights
- If not: Note the gap and suggest future work

#### 2.2 Difficulty Rating (new section)

Add guidance for rating language pair complexity:
- Easy: Same paradigm, similar type systems
- Medium: Different paradigms OR type systems
- Hard: Different paradigms AND type systems AND memory models

## Files Modified

- `components/skills/meta-convert-dev/SKILL.md`
- `.claude/commands/create-lang-conversion-skill.md`

## Issues to Close via PR

- #215 (partial - TypeScript patterns)
- #208, #209 (serialization)
- #344 (advanced features)
- #345, #350 (reverse skill check)
- #217 (difficulty rating)
