# Tree-sitter Plans Index

This directory contains development plans for tree-sitter related projects.

## Projects

### [KVConf (tree-sitter-dotenv)](kvconf/)
Universal KEY=VALUE configuration file parser supporting .env, .npmrc, .ini, and other formats.

**Status**: Active development - Phase 3-7 pending implementation

**Key Features**:
- Typed value parsing with precedence
- Multi-format support
- String interpolation
- Comprehensive error handling

## Common Tree-sitter Planning Patterns

When creating plans for tree-sitter projects:

1. **Phase-based development** - Break grammar development into logical phases
2. **Test-driven approach** - Write corpus tests before implementing features  
3. **Checkpoint reviews** - Mandatory external review between phases
4. **Performance targets** - Set clear performance goals (e.g., <100ms for 1000 lines)

## Tree-sitter Resources

- [Official Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Grammar Development Guide](https://tree-sitter.github.io/tree-sitter/creating-parsers)
- [Help Guides](../../help/tree-sitter/) - Our tree-sitter development guides