# Convert Skills Consolidation & IR Design Plan

Multi-phase plan for consolidating convert-* skills and designing an Intermediate Representation (IR) schema to support cross-language codebase conversion.

## Goals

1. **Primary**: Design an IR that captures enough semantic information to convert between any supported language pair with high fidelity
2. **Secondary**: Support incremental analysis (partial codebases, evolving code)
3. **Tertiary**: Enable tooling ecosystem (extraction, synthesis, diffing, validation)

## Success Criteria

- [ ] IR can represent 80%+ of patterns in existing convert-* skills
- [ ] Round-trip conversion preserves semantics (same behavior, not same syntax)
- [ ] Cross-family conversions identify and document information loss
- [ ] Incremental updates don't require full re-analysis

## Current Status

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 0: Pattern Extraction | **Complete** | 100% |
| Phase 1: Language Families | **Complete** | 100% |
| Phase 2: Language Survey | Not Started | 0% |
| Phase 3: Semantic Gaps | Not Started | 0% |
| Phase 4: IR Schema Design | Not Started | 0% |
| Phase 5: Validation & Tooling | Not Started | 0% |
| Phase 6: Consolidation | Not Started | 0% |

**Pre-work completed:**
- [x] Phase 1 of skill consolidation: Merged 29 bidirectional pairs (78 → 49 skills)

## Phase Overview

| Phase | Goal | Depends On | Effort |
|-------|------|------------|--------|
| [Phase 0](phase/0-pattern-extraction.md) | Extract patterns from existing 49 convert-* skills | — | ~~2-3 days~~ ✓ |
| [Phase 1](phase/1-language-families.md) | Comprehensive taxonomy of language families | — | ~~3-5 days~~ ✓ |
| [Phase 2](phase/2-language-survey.md) | Catalog languages with family classification | Phase 0, 1 | 10-14 days |
| [Phase 3](phase/3-semantic-gaps.md) | Identify and classify conversion challenges | Phase 0, 1, 2 | 2-3 days |
| [Phase 4](phase/4-ir-schema-design.md) | Design the multi-layer IR architecture | Phase 3 | 5-7 days |
| [Phase 5](phase/5-validation-tooling.md) | Verify IR design and build tools | Phase 4 | 7-10 days |
| [Phase 6](phase/6-consolidation.md) | Merge insights into unified IR and skill architecture | Phase 5 | 3-5 days |

Total estimated effort: 5-7 weeks

## Directory Structure

```
.claude/plans/merge-convert-skills/
├── index.md                      # This file - plan overview
├── phase/                        # Individual phase plans
│   ├── 0-pattern-extraction.md
│   ├── 1-language-families.md
│   ├── 2-language-survey.md
│   ├── 3-semantic-gaps.md
│   ├── 4-ir-schema-design.md
│   ├── 5-validation-tooling.md
│   └── 6-consolidation.md
├── analysis/                     # Analysis outputs
│   ├── index.md                  # Analysis index
│   ├── bidirectional-merge.md    # Phase 1 merge analysis (complete)
│   ├── post-merge-state.md       # Current 49-skill landscape
│   └── ...                       # Future analysis docs
└── data/                         # SQL dumps and data files
    ├── schema.sql                # Database schema
    ├── families.sql              # Language family data
    ├── languages.sql             # Language profiles
    └── patterns.sql              # Extracted IR patterns
```

## Quick Links

### Phase Plans
- [Phase 0: Pattern Extraction](phase/0-pattern-extraction.md)
- [Phase 1: Language Families](phase/1-language-families.md)
- [Phase 2: Language Survey](phase/2-language-survey.md)
- [Phase 3: Semantic Gaps](phase/3-semantic-gaps.md)
- [Phase 4: IR Schema Design](phase/4-ir-schema-design.md)
- [Phase 5: Validation & Tooling](phase/5-validation-tooling.md)
- [Phase 6: Consolidation](phase/6-consolidation.md)

### Analysis Documents
- [Analysis Index](analysis/index.md)
- [Bidirectional Merge Analysis](analysis/bidirectional-merge.md)
- [Post-Merge State](analysis/post-merge-state.md)

### Data
- [Database Schema](data/schema.sql)

## Target Skill Architecture

After consolidation, skills will be restructured as:

```
context/skills/
├── codebase-analysis/
│   ├── SKILL.md
│   └── reference/
│       ├── ir/
│       │   ├── schema.md
│       │   ├── extraction-guide.md
│       │   └── tools.md
│       ├── families/
│       │   ├── ml-fp.md
│       │   ├── beam.md
│       │   └── ...
│       └── languages/
│           ├── python.md
│           ├── rust.md
│           └── ...
│
├── codebase-implement-from-ir/
│   ├── SKILL.md
│   └── reference/
│       ├── synthesis-guide.md
│       ├── patterns/
│       │   ├── error-handling.md
│       │   ├── concurrency.md
│       │   └── ...
│       └── targets/
│           ├── rust/
│           ├── roc/
│           └── ...
│
└── idiomatic-{lang}/
    └── SKILL.md  # Language-specific idioms
```

## Next Actions

1. [x] ~~Create SQLite database with schema~~ (data/patterns.db)
2. [x] ~~Phase 0: Extract patterns from existing convert-* skills~~ (7,195 patterns)
3. [x] ~~Phase 1: Research language families~~ (13 families documented)
4. [ ] **Start Phase 2: Language Survey** (22 full + 7 minimal profiles)
