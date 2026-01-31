# Tree-sitter-dotenv Typed Values Development Plan - Overview

## Table of Contents
- [Overview](#overview)
- [Goals](#goals)
- [Development Principles](#development-principles)
- [Value Type Precedence](#value-type-precedence)
- [Error Node Strategy](#error-node-strategy)
- [File Format Considerations](#file-format-considerations)
- [Branch Strategy](#branch-strategy)
- [Phases Overview](#phases-overview)
- [Success Criteria](#success-criteria)
- [Risk Mitigation](#risk-mitigation)
- [Timeline Estimate](#timeline-estimate)
- [Critical Reminders](#critical-reminders)

## Overview
This plan outlines the iterative, test-driven development approach to implement typed value parsing in tree-sitter-dotenv while maintaining parser correctness and adding comprehensive syntax highlighting support.

Note: While the grammar is named "tree-sitter-dotenv", it will support a wide range of KEY=VALUE configuration file formats beyond just .env files, making it a universal parser for this common configuration pattern.

**IMPORTANT**: Every checkpoint is MANDATORY and REQUIRES external review before proceeding to the next phase.

## Goals
1. Parse values into typed nodes (bool, integer, url, string, etc.)
2. Maintain the parser fix that prevents values from being parsed as new variables
3. Support all KEY=VALUE file formats (.env, .npmrc, .ini, .properties, etc.)
4. Provide rich syntax highlighting in Zed
5. Ensure no regressions through comprehensive testing

## Development Principles
- **Test-Driven Development**: Write tests before implementing features
- **Behavior-Driven Development**: Define expected behaviors clearly
- **Incremental Progress**: Small, tested changes with frequent commits
- **Regular Checkpoints**: External review at major milestones
- **Comprehensive Documentation**: Document all decisions and implementations

## Value Type Precedence
1. Double-quoted strings (with interpolation support)
2. Single-quoted strings (literal, no interpolation)
3. Boolean values (true/false)
4. Integer values
5. URI values (includes URLs, URNs, and other URI schemes)
6. Unquoted strings / raw values (catch-all)

## Error Node Strategy
- Use specific ERROR node types for different error conditions
- Scope errors as narrowly as possible (e.g., just the trailing comma)
- Allow parser to continue after errors (permissive parsing)
- Error types:
  - `error_trailing_comma`: For trailing commas
  - `error_multiple_values`: For space-separated values after primitives
  - `error_invalid_syntax`: For other syntax errors
  - `error`: Default catch-all for unspecified errors

## File Format Considerations

### Syntax Variations Across Formats
Different KEY=VALUE formats have slight variations that need consideration:

1. **Spacing around `=`**:
   - `.env`, `.npmrc`: No spaces (`KEY=value`)
   - `.gitconfig`, `.ini`: Optional spaces (`KEY = value`)
   - `.properties`: Can have spaces, colons, or equals (`key=value`, `key:value`, `key value`)

2. **Comment Styles**:
   - Most formats: `#` comments
   - `.ini`, `.gitconfig`: Also support `;` comments
   - `.properties`: `#` or `!` comments

3. **Section Headers**:
   - `.gitconfig`, `.ini`: `[section]` headers
   - Others: No section support

4. **Special Syntax**:
   - `.npmrc`: URL-style keys (`//host/:key=value`)
   - `.gitconfig`: Indented values under sections
   - `.tfvars`: HCL syntax with maps and lists

### Parser Strategy
- Core parser handles common KEY=VALUE pattern
- Allow flexible spacing around `=`
- Support both `#` and `;` comments
- Section headers parsed but not required
- Special syntaxes handled as extended identifier patterns

## Branch Strategy
- Branch name: `feature/typed-values`
- All development on single branch
- Commits after each passing test
- Checkpoint tags for major milestones

## Phases Overview

1. **Phase 1: Foundation and Setup** - Environment setup, test infrastructure, grammar refactoring foundation
2. **Phase 2: String Types** - Double-quoted strings, single-quoted strings, interpolation support
3. **Phase 3: Primitive Types** - Boolean values, integer values, error handling
4. **Phase 4: Complex Types** - URI/URL values, unquoted strings, error nodes
5. **Phase 5: Edge Cases and Polish** - Edge case handling, performance optimization, comprehensive testing
6. **Phase 6: Future Enhancements** - Array support (deferred)
7. **Phase 7: Documentation and Finalization** - Grammar documentation, integration testing, release preparation

## Success Criteria
- [ ] All value types parse correctly according to precedence
- [ ] Interpolation works only in double-quoted strings
- [ ] Errors are detected and scoped appropriately
- [ ] All tests pass consistently
- [ ] Highlighting works correctly in Zed
- [ ] No regressions from current functionality
- [ ] Documentation is complete and clear
- [ ] Performance is acceptable for 1000-line files
- [ ] Support for all major KEY=VALUE file formats:
  - [ ] Environment files (.env, .env.*)
  - [ ] NPM/Yarn configs (.npmrc, .yarnrc)
  - [ ] Git configs (.gitconfig)
  - [ ] Java properties (.properties)
  - [ ] INI files (.ini, .cfg)
  - [ ] Ruby gem configs (.gemrc)
  - [ ] Other config formats (.conf, .config, etc.)
- [ ] URI parsing supports multiple schemes:
  - [ ] HTTP(S) URLs
  - [ ] FTP URLs
  - [ ] File URLs
  - [ ] Database URLs (jdbc, mysql, postgresql)
  - [ ] Other common schemes

## Risk Mitigation
- Checkpoint tags allow easy rollback
- Comprehensive tests catch regressions early
- Documentation ensures knowledge transfer
- Regular reviews prevent drift from requirements
- Clear patterns prevent confusion during implementation

## Timeline Estimate
- Phase 1: 2-3 hours
- Phase 2: 3-4 hours
- Phase 3: 2-3 hours
- Phase 4: 4-5 hours (increased for URI complexity)
- Phase 5: 2-3 hours
- Phase 6: Deferred
- Phase 7: 2-3 hours
- **Total**: 15-21 hours of focused development

## Critical Reminders

**CHECKPOINT REVIEWS ARE MANDATORY**
- Do not proceed past any checkpoint without external review
- Each checkpoint has specific success criteria that must be met
- Reviews ensure the extension compiles, installs, and works correctly

**TESTING IS REQUIRED**
- Write tests before implementing features
- Run tests after every change
- Commit only when tests pass

**DOCUMENTATION IS ESSENTIAL**
- Document decisions as you make them
- Update docs as you implement
- Comment complex grammar rules