# Tree-sitter KVConf Notes Index

This directory contains development notes, observations, and learnings from the tree-sitter kvconf project.

## Notes

### Parser Development
- [Parser Bug Analysis](../../../../ANALYSIS.md) - Deep dive into the parser state machine bug that was preventing correct KEY=VALUE parsing
- [Grammar Patterns](./grammar-patterns.md) - Common patterns for tree-sitter grammar development (TBD)

### Key Learnings
1. **Parser State Machine Bug**: The original tree-sitter-dotenv had a fundamental bug where values were being parsed as new variables due to incorrect lexer state transitions
2. **Token.immediate Solution**: Using `token.immediate` forces tight coupling between tokens, preventing the lexer from misinterpreting values
3. **Value Type Precedence**: Careful ordering is crucial - strings must be checked before primitives to handle cases like `key="true"`

### Design Decisions
- **Universal Parser**: Rather than creating separate extensions for each file type, we're building one parser that handles all KEY=VALUE formats
- **Permissive Error Handling**: Parser continues after errors, with narrow error scoping for better user experience
- **Interpolation Scope**: Variable interpolation only in double-quoted strings, following common shell conventions

### Performance Observations
- Target: < 100ms for 1000-line files
- Critical optimizations needed for regex patterns to avoid backtracking
- Memory usage must be monitored for large configuration files

### File Format Quirks
- `.npmrc`: Uses URL-style keys like `//registry.npmjs.org/:_authToken`
- `.gitconfig`: Supports section headers `[section]` and indented values
- `.properties`: Allows multiple separators (=, :, or space)
- `.ini`: Supports both # and ; for comments

## References
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Original tree-sitter-dotenv repo](https://github.com/zarifpour/tree-sitter-dotenv)
- [RFC 3986 - URI Generic Syntax](https://tools.ietf.org/html/rfc3986)