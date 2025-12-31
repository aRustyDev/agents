# Feedback Remediation Plan

## Overview

This plan addresses 26 open feedback issues from conversion skill creation sessions. Issues are organized by priority and grouped by implementation effort.

## Issue Categories

| Category | Count | Description |
|----------|-------|-------------|
| **Lang Skill Gaps** | 10 | Missing pillars in lang-*-dev skills |
| **Meta-convert-dev** | 6 | Improvements to the meta-skill |
| **Command Workflow** | 6 | Improvements to `/create-lang-conversion-skill` |
| **New Automation** | 2 | New tooling/scripts |
| **Consolidation** | 2 | Issues that consolidate multiple feedback items |

---

## Phase 1: High-Impact Consolidations (Week 1)

### 1.1 Expand lang-roc-dev (5/8 → 8/8)
**Issue:** #403 (consolidates #376, #391, #395, #396, #400)
**Priority:** High
**Effort:** Medium (3 new sections)

**Add sections:**
- [ ] Zero/Default Values - Tag unions for optional, default patterns
- [ ] Serialization - Encode/Decode abilities, JSON handling
- [ ] Build System - `roc` CLI, platform URLs, project structure

**Closes:** #376, #391, #395, #396, #400

---

### 1.2 Expand lang-fsharp-dev (3/8 → 8/8)
**Issue:** #404 (consolidates #366)
**Priority:** High
**Effort:** High (5 new sections)

**Add sections:**
- [ ] Module System - Namespaces, modules, .fsi files
- [ ] Error Handling - Result, Option, railway-oriented
- [ ] Concurrency - Async workflows, MailboxProcessor
- [ ] Metaprogramming - Type providers, quotations
- [ ] Zero/Default Values - Option.None, defaults

**Closes:** #366

---

### 1.3 Expand lang-elixir-dev (6/9 → 9/9)
**Issue:** #352
**Priority:** High
**Effort:** Medium (3 sections to expand)

**Add/expand sections:**
- [ ] Metaprogramming - quote/unquote, defmacro, AST
- [ ] Serialization - Jason, Protocol implementations
- [ ] REPL/Workflow - IEx, hot reload, observer
- [ ] Distributed Elixir - Node clustering, :rpc, pg2

**Closes:** #352

---

### 1.4 Expand lang-scala-dev (6/9 → 9/9)
**Issues:** #351, #364, #407
**Priority:** Medium
**Effort:** Medium (3-4 sections)

**Add sections:**
- [ ] Module/Import - Package objects, visibility
- [ ] Serialization - circe, upickle, play-json
- [ ] Metaprogramming - Scala 2/3 macros, inline
- [ ] REPL Workflow - scala-cli, Ammonite

**Closes:** #351, #364, #407

---

### 1.5 Expand lang-erlang-dev Concurrency
**Issue:** #394
**Priority:** Medium
**Effort:** Low (1 section)

**Add:**
- [ ] Dedicated ## Concurrency section
- [ ] Process spawning patterns
- [ ] Selective receive, mailbox management
- [ ] Distributed concurrency (rpc patterns)

**Closes:** #394

---

## Phase 2: Meta-skill Improvements (Week 2)

### 2.1 Add Concurrency Pattern Deep-Dive
**Issue:** #413
**Priority:** High
**Effort:** High

**Add to meta-convert-dev:**
- [ ] Concurrency Model Matrix (Actors↔STM↔IO↔Channels)
- [ ] Pattern translation examples (3+ detailed)
- [ ] Supervision tree translation patterns
- [ ] Cross-references to convert-X-Y skills

**Closes:** #413

---

### 2.2 Enhance meta-convert-dev with Erlang Examples
**Issue:** #406
**Priority:** Medium
**Effort:** Medium

**Add:**
- [ ] Erlang examples alongside Elixir/Haskell
- [ ] Standard library mapping table (7 FP languages)
- [ ] Cross-language pattern index

**Closes:** #406

---

### 2.3 Add FP→FP Conversion Checklist
**Issue:** #408
**Priority:** Low
**Effort:** Medium

**Add:**
- [ ] FP→FP specific checklist (type system, purity, effects)
- [ ] Numeric type mapping table across FP languages
- [ ] Effect system comparison

**Closes:** #408

---

### 2.4 Consolidate meta-convert-dev Feedback
**Issues:** #332, #348, #363, #264, #268
**Priority:** Medium
**Effort:** Low (already partially addressed in PR #349)

**Verify addressed:**
- [x] 9th Pillar (REPL/Workflow) - PR #349
- [x] Functional→Functional section - PR #349
- [ ] Platform ecosystem section - needs expansion
- [ ] State management translation
- [ ] Numeric type edge cases

**Closes:** #332, #348, #363, #264, #268 (partial)

---

## Phase 3: Command Workflow Improvements (Week 3)

### 3.1 Add 8-Pillars Validation Script
**Issue:** #411
**Priority:** High
**Effort:** Medium

**Implement:**
- [ ] `just validate-pillars <skill>` command
- [ ] Detection heuristics for each pillar
- [ ] Integration with `/create-lang-conversion-skill`
- [ ] CI validation for lang-*-dev skills

**Closes:** #411

---

### 3.2 Add Reverse Skill Check
**Issue:** #405
**Priority:** High
**Effort:** Low

**Add to command:**
- [ ] Step 1.5: Check for reverse skill existence
- [ ] Cross-reference guidance for pattern consistency
- [ ] Self-review validation for bidirectional consistency

**Closes:** #405, #367

---

### 3.3 Consolidate Command Feedback
**Issues:** #211, #218, #261, #334
**Priority:** Medium
**Effort:** Low (most already addressed in PR #349)

**Verify addressed:**
- [x] Quick Start Mode - PR #349
- [x] 9th Pillar guidance - PR #349
- [x] Pillar Gap Mitigation Examples - PR #349
- [ ] Automate 8 Pillars Validation → #411
- [ ] Reverse Skill Check → #405
- [ ] Example Complexity Rubric - add to command
- [ ] Template Variables - evaluate feasibility

**Closes:** #211, #218, #261, #334 (partial)

---

## Phase 4: Additional Improvements (Week 4)

### 4.1 Foundation Issue #205
**Issue:** #205
**Priority:** Medium
**Effort:** Medium

**Track progress:**
- [ ] Performance Considerations section
- [ ] Ownership Model Translation depth
- [ ] Async Pattern translation depth
- [ ] Dependency Management guidance
- [ ] Validation checklist for command

**Closes:** #205

---

## Implementation Strategy

### Parallel Workstreams

```
Week 1: Lang Skills (can run 3-4 agents in parallel)
├── Agent 1: lang-roc-dev (#403)
├── Agent 2: lang-fsharp-dev (#404)
├── Agent 3: lang-elixir-dev (#352)
└── Agent 4: lang-scala-dev (#351, #364, #407)

Week 2: Meta-skill (sequential, requires coordination)
├── Concurrency deep-dive (#413)
├── Erlang examples (#406)
└── FP→FP checklist (#408)

Week 3: Command/Automation (can run 2 agents in parallel)
├── Agent 1: Validation script (#411)
└── Agent 2: Reverse skill check (#405)

Week 4: Cleanup
├── Close consolidated issues
├── Verify all improvements
└── Update documentation
```

### Git Workflow

Each improvement should:
1. Create feature branch: `feat/<issue-area>-<issue-number>`
2. Make changes with atomic commits
3. Open PR linking to issue(s)
4. Use "Closes #X" to auto-close issues

### Quality Checks

Before closing issues:
- [ ] All checklist items in issue addressed
- [ ] New content follows existing skill format
- [ ] Cross-references validated
- [ ] No new pillar gaps introduced

---

## Issue Closure Summary

| Phase | Issues Closed | New PRs |
|-------|---------------|---------|
| Phase 1 | #376, #391, #395, #396, #400, #366, #352, #351, #364, #407, #394 | 5 |
| Phase 2 | #413, #406, #408, #332, #348, #363, #264, #268 | 3-4 |
| Phase 3 | #411, #405, #367, #211, #218, #261, #334 | 2-3 |
| Phase 4 | #205 | 1 |
| **Total** | **26 issues** | **~12 PRs** |

---

## Execution Commands

```bash
# Phase 1 - Lang skills (parallel)
/create-lang-conversion-skill roc <any>  # Will expand lang-roc-dev
# Or direct editing of lang-*-dev skills

# Phase 2 - Meta-skill
# Edit meta-convert-dev/SKILL.md directly

# Phase 3 - Command/Automation
# Edit .claude/commands/create-lang-conversion-skill.md
# Create justfile recipe for validate-pillars
```

---

## Notes

- PR #349 already addressed: 9th Pillar, Functional→Functional, Quick Start Mode
- Some issues will be closed by multiple PRs
- Consolidated issues (#403, #404) should close their sub-issues automatically
- Consider creating umbrella PRs for each phase

---

## Executable Prompts

Each prompt below can be run in a separate Claude Code session. They create worktrees, implement fixes, update issues, and create PRs.

### Prompt 1: lang-elixir-dev (#352)

```
## Task: Address lang-elixir-dev feedback issue #352

### Context
Issue #352 identifies 4 missing sections in `components/skills/lang-elixir-dev/SKILL.md`:
1. Dedicated Metaprogramming section (macros, quote/unquote, defmacro, __using__)
2. Serialization section (Jason/Poison, Protocol-based serialization)
3. REPL/Workflow section (IEx, hot code reloading, Observer, iex -S mix)
4. Zero/Default value handling section (nil handling, default arguments, struct defaults)

### Instructions
1. Create a worktree for this work:
   git -C /Users/arustydev/repos/configs/ai worktree add /private/tmp/ai-worktrees/fix-lang-elixir-dev feat/fix-lang-elixir-dev-352

2. Use the `lang-elixir-dev` skill itself to understand current patterns

3. Research and add the 4 missing sections to SKILL.md following the 8 Pillars framework from `meta-convert-dev`

4. Validate the updated skill using `/validate-lang-conversion-skill` patterns (check token budget < 500 lines for main concepts)

5. Commit changes with conventional commit format

6. Create a PR that closes #352

7. Add a comment to issue #352 summarizing what was implemented

### Expected Outcome
- SKILL.md updated with 4 new dedicated sections
- Pillar coverage improved from 5/9 to 9/9
- PR created linking to #352
```

---

### Prompt 2: lang-scala-dev (#351, #364)

```
## Task: Address lang-scala-dev feedback issues #351 and #364

### Context
Issues #351 and #364 identify missing sections in `components/skills/lang-scala-dev/SKILL.md`:
- #351: Missing dedicated Module/Import section
- #364: Missing dedicated Serialization section (JSON, XML, binary formats)

Current pillar coverage: 5/8

### Instructions
1. Create a worktree for this work:
   git -C /Users/arustydev/repos/configs/ai worktree add /private/tmp/ai-worktrees/fix-lang-scala-dev feat/fix-lang-scala-dev-351-364

2. Use `lang-scala-dev` skill to understand current structure

3. Add dedicated sections:
   - ## Module System (imports, packages, visibility, companion objects)
   - ## Serialization (circe, play-json, upickle, XML, binary)

4. Follow patterns from `lang-fsharp-dev` which has 8/8 pillar coverage as a reference

5. Commit changes with conventional commit format

6. Create a PR that closes #351 and #364

7. Add comments to both issues summarizing implementations

### Expected Outcome
- SKILL.md updated with 2 new dedicated sections
- Pillar coverage improved from 5/8 to 7/8 or 8/8
- PR created linking to both issues
```

---

### Prompt 3: lang-roc-dev (#400, #395, #396, #376)

```
## Task: Address lang-roc-dev feedback issues #400, #395, #396, #376

### Context
Multiple issues identify partial coverage in `components/skills/lang-roc-dev/SKILL.md`:
- #376: Zero/Default values need dedicated section
- #376: Serialization (Encode/Decode abilities) needs expansion
- #376: Build system (roc build, roc run, roc test) needs dedicated section
- #395, #396, #400: Additional pillar coverage gaps

Current pillar coverage: 5/8 (Zero/Default, Serialization, Build are partial)

### Instructions
1. Create a worktree for this work:
   git -C /Users/arustydev/repos/configs/ai worktree add /private/tmp/ai-worktrees/fix-lang-roc-dev feat/fix-lang-roc-dev-pillars

2. Read existing SKILL.md and identify exactly what's missing vs what exists

3. Expand or create dedicated sections for:
   - ## Zero and Default Values (zero values for types, optional fields via tag unions)
   - ## Serialization (Encode/Decode abilities, JSON examples, custom implementations)
   - ## Build System (roc build, roc run, roc test, platform dependencies)

4. Use WebSearch to find current Roc documentation for accurate patterns

5. Commit changes with conventional commit format

6. Create a PR that closes #376 (the main tracking issue) and references #395, #396, #400

7. Add comments to all 4 issues summarizing what was addressed

### Expected Outcome
- SKILL.md updated with 3 expanded/new sections
- Pillar coverage improved from 5/8 to 8/8
- PR created linking to all related issues
```

---

### Prompt 4: meta-convert-dev (#332, #348, #363, #268, #264, #344)

```
## Task: Address meta-convert-dev feedback issues

### Context
Multiple issues identify structural gaps in `components/skills/meta-convert-dev/SKILL.md`:
- #268: Platform Ecosystem section needed (JVM, BEAM, .NET, Native)
- #264: Paradigm Translation section needed (OOP↔FP, imperative↔declarative)
- #332: Numeric edge cases documentation
- #344: Stdlib mapping patterns
- #348, #363: Additional structural improvements

### Instructions
1. Create a worktree for this work:
   git -C /Users/arustydev/repos/configs/ai worktree add /private/tmp/ai-worktrees/fix-meta-convert-dev feat/fix-meta-convert-dev-structure

2. Read the current SKILL.md structure and meta-convert-guide for context

3. Add or expand sections for:
   - ## Platform Ecosystem (platform families, interop considerations)
   - ## Paradigm Translation (OOP to FP patterns, imperative to declarative)
   - Numeric edge cases in existing type mapping sections
   - Stdlib mapping patterns (common operations across languages)

4. Ensure changes follow progressive disclosure pattern (main SKILL.md < 500 lines, details in reference/)

5. Commit changes with conventional commit format

6. Create a PR that closes the primary issues and references others

7. Add comments to issues summarizing implementations

### Expected Outcome
- SKILL.md and reference/ updated with structural improvements
- Clear platform ecosystem and paradigm translation guidance
- PR created linking to relevant issues
```

---

### Prompt 5: create-lang-conversion-skill command (#211, #218, #261)

```
## Task: Address create-lang-conversion-skill command feedback

### Context
Issues identify minor remaining gaps in `components/commands/create-lang-conversion-skill.md`:
- #211: Template completeness improvements
- #218: Example quality checklist enhancements
- #261: Edge case handling in generation

Most items are already addressed, but some refinements remain.

### Instructions
1. Create a worktree for this work:
   git -C /Users/arustydev/repos/configs/ai worktree add /private/tmp/ai-worktrees/fix-create-lang-conversion-skill feat/fix-create-lang-conversion-skill-cmd

2. Read issues #211, #218, #261 to understand specific remaining gaps

3. Read current command file and identify what's already implemented vs what's missing

4. Make targeted improvements:
   - Enhance template sections if incomplete
   - Improve example quality checklist
   - Add edge case handling guidance

5. Validate command structure follows slash command best practices

6. Commit changes with conventional commit format

7. Create a PR that closes applicable issues

8. Add comments to issues summarizing what was addressed vs what may need separate work

### Expected Outcome
- Command file refined with remaining improvements
- Clear documentation of any items deferred to separate issues
- PR created linking to addressed issues
```

---

## Prompt Usage Notes

1. Run each prompt in a **separate Claude Code session**
2. Prompts are independent and can run in parallel
3. Each creates its own worktree under `/private/tmp/ai-worktrees/`
4. PRs will be created against `main` branch
5. Issues will be updated with implementation summaries

## Worktree Cleanup

After PRs are merged:

```bash
# List worktrees
git -C /Users/arustydev/repos/configs/ai worktree list

# Remove worktrees
git -C /Users/arustydev/repos/configs/ai worktree remove /private/tmp/ai-worktrees/fix-lang-elixir-dev
git -C /Users/arustydev/repos/configs/ai worktree remove /private/tmp/ai-worktrees/fix-lang-scala-dev
git -C /Users/arustydev/repos/configs/ai worktree remove /private/tmp/ai-worktrees/fix-lang-roc-dev
git -C /Users/arustydev/repos/configs/ai worktree remove /private/tmp/ai-worktrees/fix-meta-convert-dev
git -C /Users/arustydev/repos/configs/ai worktree remove /private/tmp/ai-worktrees/fix-create-lang-conversion-skill
```
