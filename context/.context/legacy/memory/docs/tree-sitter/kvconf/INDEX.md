# Tree-sitter KVConf Documentation Index

This directory contains historical documentation, analysis reports, architecture decisions, and other formal documentation for the tree-sitter kvconf project.

## Historical Documentation

### Analysis Reports
- [Parser Bug Analysis](analysis/ANALYSIS.md) - Deep technical analysis of the parser state machine bug
- [NPM RC Highlighting Plan](analysis/NPMRC_HIGHLIGHTING_PLAN.md) - Initial plan for fixing .npmrc syntax highlighting
- [NPM RC Implementation Plan](analysis/NPMRC_IMPLEMENTATION_PLAN.md) - Updated plan with parser bug discovery
- [Completion Report](analysis/COMPLETION_REPORT.md) - Summary of parser bug fix implementation
- [Final Solution](analysis/FINAL_SOLUTION.md) - Comprehensive solution documentation
- [Debug Highlights](analysis/DEBUG_HIGHLIGHTS.md) - Zed highlighting issue analysis
- ~~Process Guide~~ - Moved to [Help Guides](../../help/tree-sitter/kvconf/)
- ~~Debug Tree~~ - Moved to [Debugging Syntax Trees](../../help/tree-sitter/kvconf/debugging-syntax-trees.md)
- ~~Test Highlighting~~ - Moved to [Testing Zed Highlighting](../../help/tree-sitter/kvconf/testing-zed-highlighting.md)

### Development Plans
- Individual phase plans in [plans directory](../../plans/tree-sitter/kvconf/)

### Architecture Decisions
- [ADR-000: Migration from Monolithic Plan](adr/ADR-000-migration-from-monolithic-plan.md)
  - Decision to split the development plan into modular structure
  - Migration of test files and build automation

- [ADR-001: Universal KEY=VALUE Parser Approach](adr/ADR-001-universal-key-value-parser.md)
  - Decision to create one parser for all configuration formats
  - Rationale: Better maintainability and consistent behavior

- [ADR-002: Token.immediate for Parser Fix](adr/ADR-002-token-immediate-parser-fix.md)
  - Use of token.immediate to solve parser state machine bug
  - Prevents lexer from misinterpreting values as new variables

- [ADR-003: Value Type Precedence Strategy](adr/ADR-003-value-type-precedence.md)
  - Ordered precedence: strings > booleans > integers > URIs > raw
  - Ensures correct parsing of ambiguous values

### Design Documents
- Parser state machine design
- Value type detection strategy
- Error recovery approach
- Performance optimization techniques

### Lessons Learned
- [Complete Lessons Learned Document](lessons-learned.md) - Comprehensive insights from the project
- Key insights:
  - Importance of understanding lexer state transitions
  - Value of comprehensive test coverage  
  - Benefits of incremental development approach
  - Critical role of `token.immediate` for parser correctness

## Help and Troubleshooting

For development guides and troubleshooting resources, see the [Help Directory](../../help/tree-sitter/kvconf/):
- [Tree-sitter Grammar Development Guide](../../help/tree-sitter/kvconf/tree-sitter-grammar-development.md)
- [Zed Extension Development Guide](../../help/tree-sitter/kvconf/zed-extension-development.md)