---
description: Create a convert-X-Y skill for translating code between languages
argument-hint: <source-lang> <target-lang>
---

# Create Language Conversion Skill

Create a new one-way language conversion skill (`convert-<source>-<target>`) that extends `meta-convert-dev` with language-pair-specific patterns.

## Arguments

- `$1` - Source language (lowercase, e.g., `typescript`, `python`, `golang`)
- `$2` - Target language (lowercase, e.g., `rust`, `python`, `golang`)

## Prerequisites

This command requires the `meta-convert-dev` skill to be available. Read it first to understand the foundational patterns.

## Workflow

### Step 1: Validate Arguments

1. Confirm both source and target languages are provided
2. Validate language names are lowercase and recognized
3. Construct skill name: `convert-$1-$2`

If arguments are missing, ask the user:
```
Please provide source and target languages:
/create-lang-conversion-skill <source-lang> <target-lang>

Example: /create-lang-conversion-skill typescript rust
```

### Step 2: Read Foundation & Reference Skills

Read these skills to understand patterns and gather examples:

1. **Meta-skill** (required): `components/skills/meta-convert-dev/SKILL.md`
   - APTV workflow (Analyze → Plan → Transform → Validate)
   - Type mapping strategies
   - Idiom translation approaches
   - Testing strategies

2. **Existing conversion skills** (for reference):
   - Search for `convert-*` skills in `components/skills/`
   - Use these as examples for structure and depth
   - Borrow patterns that apply to your language pair

3. **Language skills** (if available):
   - `lang-$1-dev` - Source language patterns
   - `lang-$2-dev` - Target language patterns

### Step 2.5: Validate 8 Pillars Coverage

Before creating a conversion skill, validate that both source and target language skills have adequate coverage of the **8 Pillars** essential for code conversion:

| Pillar | Description | Why Essential for Conversion |
|--------|-------------|------------------------------|
| Module System | Imports, exports, visibility, packages | Import/export translation |
| Error Handling | Error types, Result/Option, exceptions | Error model translation |
| Concurrency Model | Async/await, threads, channels | Async pattern translation |
| Metaprogramming | Decorators, macros, annotations | Attribute/decorator translation |
| Zero/Default Values | Null, undefined, Option, defaults | Null-safety translation |
| Serialization Idioms | JSON, struct tags, validation | Data structure translation |
| Build/Deps | Package managers, build tools | Project migration |
| Testing Idioms | Test frameworks, mocking | Test suite conversion |

#### Validation Process

1. **Read both language skills:**
   ```
   components/skills/lang-$1-dev/SKILL.md
   components/skills/lang-$2-dev/SKILL.md
   ```

2. **Check for each pillar** - Look for dedicated sections or substantial coverage:
   - ✓ = Has a dedicated section or comprehensive coverage
   - ~ = Mentioned but incomplete
   - ✗ = Missing entirely

3. **Calculate coverage scores:**
   - Green: 6-8 pillars covered
   - Yellow: 4-5 pillars covered
   - Red: 0-3 pillars covered

4. **If either skill scores Yellow or Red:**

   **Option A: Proceed with warnings** (for time-sensitive tasks)
   - Document missing pillars in the conversion skill's "Limitations" section
   - Note that external research was required for those areas
   - Create follow-up issues to improve lang-*-dev skills

   **Option B: Improve lang-*-dev first** (recommended)
   - Create issues to add missing pillars to lang-*-dev skills
   - Add the missing content to lang-*-dev skills
   - Then proceed with conversion skill creation

   **Option C: Use cross-cutting pattern skills** (for common gaps)
   - `patterns-concurrency-dev` - Supplements Concurrency gaps
   - `patterns-serialization-dev` - Supplements Serialization gaps
   - `patterns-metaprogramming-dev` - Supplements Metaprogramming gaps
   - Reference these skills in the conversion skill's "See Also" section

   Ask the user which approach they prefer.

5. **Report validation results:**
   ```
   ## 8 Pillars Validation

   | Skill | Module | Error | Concurrency | Metaprog | Zero | Serial | Build | Test | Score |
   |-------|--------|-------|-------------|----------|------|--------|-------|------|-------|
   | lang-$1-dev | ✓/~/✗ | ... | ... | ... | ... | ... | ... | ... | X/8 |
   | lang-$2-dev | ✓/~/✗ | ... | ... | ... | ... | ... | ... | ... | X/8 |

   **Status:** Green/Yellow/Red
   **Recommendation:** [Proceed / Improve skills first / Proceed with documented gaps]
   ```

### Step 3: Research Language Pair

Before creating the skill, research the specific language pair:

1. **Type system differences**: How do types map between languages?
2. **Error handling**: Exceptions vs Result types vs error returns
3. **Concurrency models**: async/await, goroutines, threads, etc.
4. **Memory models**: GC vs ownership vs manual
5. **Idiomatic patterns**: What's "the way" in each language?
6. **Ecosystem**: Common library equivalents between languages

Use WebSearch if needed to find authoritative conversion guides.

### Step 4: Create Skill Directory

```bash
mkdir -p components/skills/convert-$1-$2
```

### Step 5: Generate SKILL.md

Create the skill file using the template below.

**Important**: For code examples, reference existing `convert-X-Y` skills rather than creating examples from scratch. This ensures consistency and allows users to see real, tested patterns.

```markdown
---
name: convert-<source>-<target>
description: Convert <Source> code to idiomatic <Target>. Use when migrating <Source> projects to <Target>, translating <Source> patterns to idiomatic <Target>, or refactoring <Source> codebases. Extends meta-convert-dev with <Source>-to-<Target> specific patterns.
---

# Convert <Source> to <Target>

Convert <Source> code to idiomatic <Target>. This skill extends `meta-convert-dev` with <Source>-to-<Target> specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: <Source> types → <Target> types
- **Idiom translations**: <Source> patterns → idiomatic <Target>
- **Error handling**: <Source> error model → <Target> error model
- **Async patterns**: <Source> concurrency → <Target> concurrency
- **[If applicable] Memory/Ownership**: <Source> memory model → <Target>

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- <Source> language fundamentals - see `lang-<source>-dev`
- <Target> language fundamentals - see `lang-<target>-dev`
- Reverse conversion (<Target> → <Source>) - see `convert-<target>-<source>`

---

## Quick Reference

| <Source> | <Target> | Notes |
|----------|----------|-------|
| ... | ... | ... |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Preserve semantics** over syntax similarity
4. **Adopt target idioms** - don't write "<Source> code in <Target> syntax"
5. **Handle edge cases** - null/nil/None, error paths, resource cleanup
6. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| <Source> | <Target> | Notes |
|----------|----------|-------|
| ... | ... | ... |

### Collection Types

| <Source> | <Target> | Notes |
|----------|----------|-------|
| ... | ... | ... |

### Composite Types

| <Source> | <Target> | Notes |
|----------|----------|-------|
| ... | ... | ... |

---

## Idiom Translation

### Pattern: <Common Pattern Name>

**<Source>:**
```<source-lang>
// Source code example
```

**<Target>:**
```<target-lang>
// Target code example - idiomatic, not transliterated
```

**Why this translation:**
- Explanation of why this is idiomatic in target language

[Repeat for major patterns...]

---

## Error Handling

### <Source> Error Model → <Target> Error Model

[Detailed section on error translation...]

---

## Concurrency Patterns

### <Source> Async → <Target> Async

[Detailed section on concurrency translation...]

---

## [If Applicable] Memory & Ownership

### <Source> Memory Model → <Target> Memory Model

[Detailed section for GC ↔ ownership conversions...]

---

## Common Pitfalls

1. **<Pitfall 1>**: Description and how to avoid
2. **<Pitfall 2>**: Description and how to avoid
...

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| ... | ... | ... |

---

## Examples

Examples should progress in complexity:

### Example 1: Simple - <Single concept>

**Before (<Source>):**
```<source-lang>
// Simple, focused example demonstrating one concept
```

**After (<Target>):**
```<target-lang>
// Idiomatic translation of the single concept
```

### Example 2: Medium - <Multiple concepts>

**Before (<Source>):**
```<source-lang>
// Example combining 2-3 concepts (e.g., types + error handling)
```

**After (<Target>):**
```<target-lang>
// Shows how concepts interact in target language
```

### Example 3: Complex - <Real-world pattern>

**Before (<Source>):**
```<source-lang>
// Complete, realistic source code (~50-100 lines)
// Demonstrates a real-world use case
```

**After (<Target>):**
```<target-lang>
// Complete, idiomatic target code
// Shows full translation including edge cases
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-X-Y` - Related conversion skills (list specific ones if applicable)
- `lang-<source>-dev` - <Source> development patterns
- `lang-<target>-dev` - <Target> development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, channels, threads across languages
- `patterns-serialization-dev` - JSON, validation, struct tags across languages
- `patterns-metaprogramming-dev` - Decorators, macros, annotations across languages
```

### Step 6: Populate Content

Fill in the template with specific content for this language pair:

#### Content Requirements

| Section | Minimum | Quality Bar |
|---------|---------|-------------|
| Quick Reference | 10 entries | Most common type mappings |
| Primitive Types | All primitives | Include edge cases (infinity, NaN) |
| Collection Types | 5+ types | Array, Map, Set, Tuple equivalents |
| Composite Types | 3+ types | Struct, Class, Interface mappings |
| Idiom Translations | 5-10 patterns | Common patterns with "why" explanations |
| Error Handling | Complete section | Full error model translation |
| Concurrency | Complete section | Async/threading translation |
| Memory/Ownership | If applicable | Include if languages differ (GC vs ownership) |
| Examples | 3+ (simple, medium, complex) | Progressive complexity |
| Pitfalls | 5+ pitfalls | Language-pair specific mistakes |

#### Example Complexity Guide

| Level | Lines | Concepts | Purpose |
|-------|-------|----------|---------|
| Simple | 5-15 | 1 | Demonstrate single type/idiom translation |
| Medium | 20-40 | 2-3 | Show concept interactions |
| Complex | 50-100 | 4+ | Real-world use case, production-ready |

### Step 7: Validate Skill

Run through this checklist before completing:

#### Structure Validation
- [ ] SKILL.md has valid YAML frontmatter
- [ ] `name` matches directory name (`convert-$1-$2`)
- [ ] `description` includes trigger phrases (convert, migrate, translate)
- [ ] All sections from template are present
- [ ] No placeholder text remains (`...`, `<Description>`, etc.)

#### Content Validation
- [ ] Type mapping tables are comprehensive
- [ ] Idiom translations include "why" explanations
- [ ] Error handling section covers full error model
- [ ] Concurrency section addresses async patterns
- [ ] Memory/Ownership included if languages differ

#### Example Validation
- [ ] Examples progress in complexity (simple → complex)
- [ ] Source code examples are syntactically correct
- [ ] Target code examples are idiomatic (not transliterated)
- [ ] Examples cover different aspects (types, errors, async)
- [ ] Complex example is realistic and complete

#### Cross-Reference Validation
- [ ] References `meta-convert-dev` as foundation
- [ ] Links to `lang-$1-dev` if it exists
- [ ] Links to `lang-$2-dev` if it exists
- [ ] Mentions reverse skill `convert-$2-$1` in "Does NOT Cover"
- [ ] Lists related `convert-X-Y` skills in "See Also"

### Step 8: Suggest Cross-References

After creating the skill, suggest related skills that should reference it:

```markdown
## Cross-Reference Updates Suggested

Consider adding references to this skill in:

1. **`meta-convert-dev`** - Add to "Existing Conversion Skills" section
2. **`lang-$1-dev`** - Add to "Related Skills" section
3. **`lang-$2-dev`** - Add to "Related Skills" section
4. **`convert-$2-$1`** - Reference as reverse skill (if it exists)
```

### Step 9: Report Results

```
## Skill Created

| Field | Value |
|-------|-------|
| Skill Name | `convert-<source>-<target>` |
| Location | `components/skills/convert-<source>-<target>/SKILL.md` |
| Extends | `meta-convert-dev` |

**Validation Results:**
- [ ] Structure valid
- [ ] Content complete
- [ ] Examples validated
- [ ] Cross-references added

**Key Features:**
- [List main type mappings covered]
- [List main idiom translations covered]
- [Error handling approach]
- [Concurrency model translation]

**Next Steps:**
1. Review type mapping completeness
2. Test with real conversion scenarios
3. Update cross-referenced skills
```

### Step 10: Self-Review & Feedback

After completing the skill creation, provide feedback on the tools and skills used during the process. This helps improve the ecosystem.

#### 10.1 Identify Skills & Commands Used

List all skills and commands used during this task:

```markdown
## Skills & Commands Used

| Resource | Type | How Used |
|----------|------|----------|
| `meta-convert-dev` | skill | Foundation for structure and patterns |
| `lang-$1-dev` | skill | Source language patterns (if used) |
| `lang-$2-dev` | skill | Target language patterns (if used) |
| `convert-X-Y` | skill | Reference for examples (if used) |
| `/create-lang-conversion-skill` | command | This workflow |
```

#### 10.2 Gather Feedback

For each resource used, evaluate:

**What worked well:**
- Clear instructions that helped complete the task
- Patterns that translated well to this language pair
- Sections that saved time or prevented mistakes

**What could be improved:**
- Missing information that required external research
- Unclear instructions that caused confusion
- Patterns that didn't apply to this language pair
- Suggestions for new sections or examples

**Context to include:**
- Which language pair was being created
- Specific challenges encountered
- Workarounds used for missing guidance

#### 10.3 Create Feedback Issues

For each resource with actionable feedback:

1. **Search for existing parent issues:**
   ```bash
   gh issue list --repo aRustyDev/ai --search "<skill-or-command-name>" --state open
   ```

2. **If parent issue exists** (about the skill/command in question):
   - Create a child issue linked to the parent
   - Use `Relates to #<parent>` in the body

3. **If no relevant parent exists:**
   - Create a new issue

**Issue Template:**

```markdown
## Feedback: <skill-or-command-name>

### Context
- **Task**: Creating `convert-$1-$2` skill
- **Used for**: [e.g., "Understanding APTV workflow", "Type mapping patterns"]

### What Worked Well
- [Specific positive feedback with examples]

### Suggested Improvements
- [ ] [Actionable improvement 1]
- [ ] [Actionable improvement 2]

### Additional Notes
[Any other observations or suggestions]

---
Feedback from: `/create-lang-conversion-skill $1 $2`
```

**Example issue creation:**

```bash
# If parent issue #205 exists for meta-convert-dev
gh issue create --repo aRustyDev/ai \
  --title "feedback(meta-convert-dev): from convert-$1-$2 creation" \
  --body "$(cat <<'EOF'
## Feedback: meta-convert-dev

### Context
- **Task**: Creating `convert-typescript-rust` skill
- **Used for**: Foundation patterns, type mapping strategies

### What Worked Well
- APTV workflow provided clear structure
- Type mapping tables were excellent templates

### Suggested Improvements
- [ ] Add more examples for async cancellation patterns
- [ ] Include guidance on translating decorators/attributes

Relates to #205

---
Feedback from: `/create-lang-conversion-skill typescript rust`
EOF
)"
```

#### 10.4 Report Feedback Summary

```markdown
## Feedback Submitted

| Resource | Issue | Summary |
|----------|-------|---------|
| `meta-convert-dev` | #XXX | [Brief summary] |
| `/create-lang-conversion-skill` | #YYY | [Brief summary] |
```

## Examples

```
/create-lang-conversion-skill typescript rust
/create-lang-conversion-skill python golang
/create-lang-conversion-skill typescript python
```

## Notes

- Each conversion skill is ONE-WAY (e.g., `convert-ts-rust` is different from `convert-rust-ts`)
- Always read `meta-convert-dev` first for foundational patterns
- Reference existing `convert-X-Y` skills for structure and examples
- Focus on idiomatic translations, not syntax transliteration
- Include comprehensive type mapping tables
- Provide examples at multiple complexity levels (simple, medium, complex)
- Complete the validation checklist before marking skill as done
- **Always complete Step 10** - Feedback improves the ecosystem for future skill creation
