# Tree-sitter KVConf Help Index

This directory contains help guides and troubleshooting resources for the tree-sitter kvconf project.

## Development Guides

### [Tree-sitter Grammar Development](./tree-sitter-grammar-development.md)
A comprehensive guide for developing tree-sitter grammars, including:
- Understanding grammar limitations
- Development environment setup
- Common grammar patterns
- Testing and validation
- Performance optimization
- Debugging techniques

### [Zed Extension Development](./zed-extension-development.md)
A complete guide for integrating tree-sitter grammars with Zed extensions:
- Extension structure and configuration
- Grammar integration methods
- Syntax highlighting with highlights.scm
- Development workflow
- Installation and testing
- Publishing extensions

### [Debugging Syntax Trees](./debugging-syntax-trees.md)
Quick guide for debugging parser output in Zed:
- How to view syntax trees in Zed
- Using the "copy syntax tree" command
- Troubleshooting parsing issues

### [Testing Zed Highlighting](./testing-zed-highlighting.md)
Step-by-step guide for testing syntax highlighting:
- Installation instructions
- Test file locations
- Expected highlighting results
- Verification procedures

## Quick Reference

### Common Commands

**Tree-sitter Development:**
```bash
# Generate parser
npx tree-sitter generate

# Test parsing
npx tree-sitter parse test.env

# Run tests
npx tree-sitter test

# Build WASM
npx tree-sitter build --wasm
```

**Zed Extension Development:**
```bash
# Install dev extension
zed --install-dev-extension .

# Show syntax tree
# In Zed: Editor > Show Syntax Tree

# Clear Zed cache
rm -rf ~/Library/Caches/Zed
```

### Common Issues

1. **Parser state machine bugs** → Use `token.immediate`
2. **Highlighting not updating** → Clear Zed cache and reinstall
3. **Grammar not loading** → Check WASM file and extension manifest
4. **Performance issues** → Optimize grammar patterns

## Related Documentation

- [Development Plans](../../../plans/tree-sitter/kvconf/) - Phased implementation plans
- [Analysis Reports](../../../docs/tree-sitter/kvconf/analysis/) - Historical bug analyses
- [Test Documentation](../../../tests/tree-sitter/kvconf/) - Test patterns and fixtures
- [Build Automation](../../../build/tree-sitter/kvconf/) - Justfile and build scripts

## External Resources

- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Zed Extension Docs](https://zed.dev/docs/extensions)
- [Project Repository](https://github.com/username/tree-sitter-dotenv)