# Tree-sitter KVConf Plans Index

This directory contains the development plans for implementing typed value parsing in tree-sitter-dotenv (kvconf), a universal KEY=VALUE configuration file parser.

## Plan Overview

The plan is divided into 7 phases with mandatory checkpoints between each phase:

### Core Development Phases

1. **[Phase 0: Overview](./00-overview.md)** - Project goals, principles, and overall strategy
2. **[Phase 1: Foundation and Setup](./01-phase1-foundation.md)** - Environment setup, test infrastructure, grammar refactoring
3. **[Phase 2: String Types](./02-phase2-strings.md)** - Double-quoted strings, single-quoted strings, interpolation support  
4. **[Phase 3: Primitive Types](./03-phase3-primitives.md)** - Boolean values, integer values, error handling
5. **[Phase 4: Complex Types](./04-phase4-complex.md)** - URI/URL values, unquoted strings, error nodes
6. **[Phase 5: Edge Cases and Polish](./05-phase5-edge-cases.md)** - Edge case handling, performance optimization
7. **[Phase 6: Future Enhancements](./06-phase6-future.md)** - Deferred features (array support)
8. **[Phase 7: Documentation and Finalization](./07-phase7-documentation.md)** - Grammar docs, integration testing, release

### Supporting Documents

- **[Testing Strategy](./08-testing-strategy.md)** - Corpus tests, debugging patterns, commit strategy
- **[Documentation Structure](./09-documentation-structure.md)** - How documentation should be organized
- **[Justfile Modularization Plan](./10-justfile-modularization-plan.md)** - Plan to break up monolithic justfile

## Key Features Being Implemented

- **Universal KEY=VALUE parser** supporting multiple file formats (.env, .npmrc, .ini, .properties, etc.)
- **Typed value parsing** with proper precedence (strings > booleans > integers > URIs > raw)
- **String interpolation** support (only in double-quoted strings)
- **Comprehensive error handling** with narrow error scoping
- **Performance optimized** for large configuration files

## Development Status

- [x] Phase 1 TODOs completed (test infrastructure, validation scripts, troubleshooting guides)
- [x] Phase 2 TODOs completed (string parsing implementation, performance benchmarks, highlighting)
- [ ] Phases 3-7 pending implementation

## Quick Links

- [Original unified plan](./TYPED_VALUES_DEVELOPMENT_PLAN.md) (if preserved)
- [Project TODO list](./TODO.md)
- [Project justfile](../../../justfile) - Build automation (being modularized)
- [Grammar file](../../../../tree-sitter-dotenv/grammar.js) - Core parser implementation

## Checkpoint Reviews

**IMPORTANT**: Every phase has a mandatory checkpoint review before proceeding to the next phase. Do not skip reviews!

**CRITICAL ZED EXTENSION REQUIREMENT**: Every checkpoint MUST verify:
1. extension.toml commit hash is EXACTLY 40 characters (not 7, 12, or 16)
2. Hash matches latest pushed commit: `git log -1 --format="%H"`
3. Manual fetch test passes: `git fetch origin <hash> --depth 1`
4. Extension installs without "failed to fetch revision" errors

**Any hash mismatch or fetch failure = CHECKPOINT FAILED**

- Checkpoint 1.0: Foundation complete
- Checkpoint 2.0: String types working
- Checkpoint 3.0: Primitives implemented
- Checkpoint 4.0: Complex types done
- Checkpoint 5.0: Edge cases handled
- Checkpoint 6.0: Documentation complete