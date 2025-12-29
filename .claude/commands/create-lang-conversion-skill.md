---
description: Create a convert-X-Y skill for translating code between languages
argument-hint: <source-lang> <target-lang>
---

# Create Language Conversion Skill

Create a new one-way language conversion skill (`convert-<source>-<target>`) that extends `meta-convert-dev` with language-pair-specific patterns.

## Arguments

- `$1` - Source language (lowercase, e.g., `typescript`, `python`, `golang`)
- `$2` - Target language (lowercase, e.g., `rust`, `python`, `golang`)

## Quick Reference

| Step | Action | Purpose |
|------|--------|---------|
| 0 | Check existing | Avoid duplicate skills |
| 1 | Validate args | Ensure valid language names |
| 2 | Read foundations | Understand meta-skill patterns |
| 2.5 | Validate 8 Pillars | Ensure lang skills have coverage |
| 3 | Research pair | Gather language-specific mappings |
| 4 | Create directory | Set up skill location |
| 5 | Generate SKILL.md | Create from template |
| 6 | Populate content | Fill in language-specific details |
| 7 | Validate skill | Run quality checklist |
| 8 | Cross-references | Suggest related skill updates |
| 9 | Report | Summary of what was created |
| 10 | Feedback | Self-review and improvement suggestions |

**Modes:**
- **Create** (default) - New skill from scratch
- **Update** - Improve existing skill (use `--update` or detect existing)

## Prerequisites

This command requires the `meta-convert-dev` skill to be available. Read it first to understand the foundational patterns.

---

## Workflow

### Step 0: Check for Existing Skill

Before creating a new skill, check if one already exists:

```bash
# Check if skill directory exists
ls components/skills/convert-$1-$2/

# Search for existing PRs
gh pr list --search "convert-$1-$2" --state all
```

**If the skill already exists:**

1. **Confirm with user**: "A `convert-$1-$2` skill already exists. Options:"
   - **Update mode**: Improve the existing skill (add missing sections, enhance examples)
   - **Skip**: Move on to next task
   - **Force create**: Replace existing (requires explicit confirmation)

2. **For update mode**, skip to [Step 6: Populate Content](#step-6-populate-content) and focus on:
   - Filling gaps identified in validation
   - Adding missing type mappings
   - Improving examples
   - Updating cross-references

3. **Report findings** even if skipping:
   ```markdown
   ## Existing Skill Found

   | Field | Value |
   |-------|-------|
   | Skill | `convert-$1-$2` |
   | Status | Already exists |
   | Location | `components/skills/convert-$1-$2/SKILL.md` |
   | PR | #XXX (if known) |

   **Recommendation:** [Update / Skip / Review]
   ```

---

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

2. **Existing conversion skills** (required - read at least 1):
   - Search for `convert-*` skills in `components/skills/`
   - **Read one complete skill** (e.g., `convert-typescript-rust/SKILL.md` lines 1-300) to understand:
     - Expected depth for type mapping tables
     - "Why this translation" explanation style
     - Example complexity progression
   - Borrow patterns that apply to your language pair

3. **Language skills** (if available):
   - `lang-$1-dev` - Source language patterns
   - `lang-$2-dev` - Target language patterns

**Before proceeding**: Confirm you have read at least one complete conversion skill as a reference.

### Step 2.5: Validate 8 Pillars Coverage (Automated)

Before creating a conversion skill, validate that both source and target language skills have adequate coverage of the **8 Pillars** essential for code conversion.

#### Pillar Reference

| Pillar | Search Terms | Why Essential |
|--------|-------------|---------------|
| Module | `## Module`, `import`, `export`, `visibility` | Import/export translation |
| Error | `## Error`, `Result`, `Exception`, `try/catch` | Error model translation |
| Concurrency | `## Concurrency`, `async`, `await`, `thread` | Async pattern translation |
| Metaprogramming | `## Metaprogramming`, `decorator`, `macro`, `annotation` | Attribute translation |
| Zero/Default | `## Zero`, `## Default`, `null`, `Option`, `None` | Null-safety translation |
| Serialization | `## Serialization`, `JSON`, `serde`, `marshal` | Data structure translation |
| Build | `## Build`, `## Dependencies`, `Cargo`, `package.json` | Project migration |
| Testing | `## Testing`, `#[test]`, `describe`, `unittest` | Test suite conversion |

#### Automated Validation

Run this validation automatically when reading the lang-*-dev skills:

```bash
# Check for section headers (example for bash, but do this by reading the file)
for pillar in "Module" "Error" "Concurrency" "Metaprogramming" "Zero\|Default" "Serialization" "Build" "Testing"; do
  grep -c "## .*$pillar" components/skills/lang-$1-dev/SKILL.md
done
```

**While reading each skill file, check for these patterns:**

| Pillar | ✓ Criteria | ~ Criteria | ✗ Criteria |
|--------|-----------|------------|------------|
| Module | Has `## Module` section with 50+ lines | Mentioned in another section | No coverage |
| Error | Has `## Error` section with examples | Has Result/Exception mentions | No coverage |
| Concurrency | Has `## Concurrency` section | Has async/thread mentions | No coverage |
| Metaprogramming | Has `## Metaprogramming` section | Has decorator/macro mentions | No coverage |
| Zero/Default | Has dedicated section or table | Mentioned in types section | No coverage |
| Serialization | Has `## Serialization` section | Has JSON/serde mentions | No coverage |
| Build | Has `## Build` section | Has package manager mentions | No coverage |
| Testing | Has `## Testing` section | Has test framework mentions | No coverage |

#### Quick Score Calculation

Count section headers matching pillars:
- **8/8**: Excellent - proceed confidently
- **6-7/8**: Good - note gaps, proceed with pattern skill references
- **4-5/8**: Fair - strongly recommend improving lang skills first
- **0-3/8**: Poor - must improve lang skills before proceeding

#### Handling Gaps

| Score | Action |
|-------|--------|
| 6-8/8 | Proceed. Reference pattern skills for missing pillars |
| 4-5/8 | Ask user: Proceed with gaps documented OR improve skills first |
| 0-3/8 | Stop. Create issues to improve lang-*-dev skills first |

**Pattern skill supplements:**
- `patterns-concurrency-dev` → Concurrency gaps
- `patterns-serialization-dev` → Serialization gaps
- `patterns-metaprogramming-dev` → Metaprogramming gaps

#### Report Format

```markdown
## 8 Pillars Validation

| Skill | Mod | Err | Conc | Meta | Zero | Ser | Build | Test | Score |
|-------|-----|-----|------|------|------|-----|-------|------|-------|
| lang-$1-dev | ✓ | ✓ | ✓ | ~ | ✓ | ✓ | ✓ | ✓ | 7.5/8 |
| lang-$2-dev | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8/8 |

**Combined Score:** 15.5/16 (Excellent)
**Gaps:** lang-$1-dev metaprogramming is partial
**Mitigation:** Reference `patterns-metaprogramming-dev`
**Decision:** Proceed ✓
```

### Step 3: Research Language Pair

Before creating the skill, research the specific language pair using these structured checklists:

#### 3.1 Type System Differences
- [ ] Read primitive types sections in both lang skills
- [ ] Create draft mapping table for primitives
- [ ] Identify types without direct equivalents
- [ ] Note numeric precision differences (32-bit vs 64-bit, overflow behavior)

#### 3.2 Error Handling
- [ ] Identify error model in source (Exceptions? Result types? Error returns?)
- [ ] Identify error model in target
- [ ] Map error propagation patterns (try/catch → ?, throw → return Err)
- [ ] Note any "no runtime errors" guarantees (like Elm)

#### 3.3 Concurrency Models
- [ ] Identify async model in source (async/await, callbacks, actors?)
- [ ] Identify async model in target
- [ ] Map concurrency primitives (Promise → Future, Channel → mpsc)
- [ ] Note architectural differences (managed runtime vs explicit)

#### 3.4 Memory Models
- [ ] Source memory model: GC / ownership / manual / managed
- [ ] Target memory model
- [ ] If different, plan ownership translation strategy
- [ ] Note lifetime considerations if applicable

#### 3.5 Idiomatic Patterns
- [ ] What's considered "the way" in source language?
- [ ] What's considered "the way" in target language?
- [ ] Identify patterns that should NOT be directly translated
- [ ] Note paradigm shifts (OOP → FP, imperative → declarative)

#### 3.6 Ecosystem Equivalents
- [ ] Common HTTP libraries
- [ ] JSON/serialization libraries
- [ ] Testing frameworks
- [ ] Build tools

#### When to Use WebSearch

Use WebSearch when:
- Lang skills lack coverage for a pillar
- Looking for real-world migration guides
- Finding common pitfalls others have encountered

**Example queries:**
- `"<Source> to <Target> migration patterns 2024"` - General migration guides
- `"<Source> <pattern> equivalent in <Target>"` - Specific pattern translations
- `"Common mistakes converting <Source> to <Target>"` - Pitfalls research
- `"<Source> vs <Target> error handling"` - Error model comparison

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
| Idiom Translations | See priority list below | Common patterns with "why" explanations |
| Error Handling | Complete section | Full error model translation |
| Concurrency | Complete section | Async/threading translation |
| Memory/Ownership | If applicable | Include if languages differ (GC vs ownership) |
| Examples | 3+ (simple, medium, complex) | Progressive complexity |
| Pitfalls | 5+ pitfalls | Language-pair specific mistakes |

#### Idiom Translation Priority

**Required patterns (must include):**
1. Null/optional handling (null → Option, Maybe → nil, etc.)
2. Collection operations (map, filter, reduce equivalents)
3. Error propagation (try/catch → Result, throws → Either)
4. Async/await patterns (if either language has async)

**Language-specific patterns (include 2-6 based on relevance):**
- Type alias/newtype definitions
- Pattern matching
- Generics/type parameters
- Interface/trait implementations
- Resource cleanup (using/defer/Drop)
- Builder patterns
- Iteration patterns

#### Quality Guidance: Good vs Great

| Aspect | Good | Great |
|--------|------|-------|
| Type mapping | `String → &str` | `String → &str for borrowed, String for owned; use Cow<str> when ownership varies` |
| Why explanation | "Use Result in Rust" | "Use Result because Rust has no exceptions; the ? operator propagates errors like try/catch but at compile time" |
| Example code | Syntactically correct | Syntactically correct + follows target language conventions (naming, formatting, idioms) |
| Pitfall | "Don't forget to handle errors" | "TypeScript's `undefined` vs Rust's `Option`: TS allows property access on undefined (runtime error), Rust requires explicit unwrap (compile error)" |

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
