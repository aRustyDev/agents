# Tree-sitter Notes Index

This directory contains development notes, observations, and discoveries for tree-sitter projects.

## Projects

### [KVConf (tree-sitter-dotenv)](kvconf/)
Notes from developing the universal KEY=VALUE parser including parser bug discoveries, design decisions, and performance observations.

## Common Tree-sitter Observations

### Parser Development Patterns
- State machine bugs often involve lexer state transitions
- `token.immediate` is crucial for preventing unwanted tokenization
- Precedence ordering matters for ambiguous patterns

### Performance Considerations
- Avoid regex backtracking in grammar rules
- Use `token()` for better performance
- Test with large files early in development

### Debugging Techniques
- Use `--debug` flag for detailed parsing info
- Check grammar.json for generated rules
- Test incrementally with small examples

## Note Organization Tips

- Use date prefixes for chronological tracking
- Create topic files for ongoing investigations
- Keep debug sessions documented for future reference