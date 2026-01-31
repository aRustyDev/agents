# Tree-sitter KVConf Examples Index

This directory contains code examples, sample configurations, and usage demonstrations for the tree-sitter kvconf project.

## Configuration Examples

### Environment Files

- [basic-env-file.env](./basic-env-file.env) - Complete .env file with common patterns
- [value-types.env](./value-types.env) - Demonstrates all supported value types

### NPM Configuration

- [complete-npmrc.npmrc](./complete-npmrc.npmrc) - Comprehensive .npmrc with all features

### Java Properties

- [java-properties.properties](./java-properties.properties) - Enterprise Java application config

### INI Configuration

- [config.ini](./config.ini) - Multi-section INI file with comments

## Parser Feature Examples

### Value Types and Edge Cases

- [value-types.env](./value-types.env) - All supported value types with examples
- [error-cases.env](./error-cases.env) - Error handling and edge cases

### Tree-sitter Queries

- [queries.scm](./queries.scm) - Example queries for finding specific patterns

## Quick Reference

### Supported Value Types

1. **Strings**: Double-quoted (with interpolation), single-quoted (literal)
2. **Booleans**: `true` and `false` (lowercase only)
3. **Numbers**: Integers (positive and negative)
4. **URIs**: URLs with schemes (http://, ftp://, etc.)
5. **Raw values**: Anything else

### Common Patterns

- Variable interpolation: `"Hello ${USER}"`
- Empty values: `KEY=`
- Comments: `# comment` or `; comment`
- Namespaces: `@scope:key=value`
- URL paths: `//host/:key=value`

## Usage Tips

1. **Test your configuration** with the parser:

   ```bash
   npx tree-sitter parse config.env
   ```

2. **Use queries** to find specific patterns in your configuration files

3. **Check error nodes** to identify syntax issues:
   ```bash
   npx tree-sitter parse --debug config.env
   ```

# Tree-sitter Examples Index

This directory contains code examples and sample configurations for tree-sitter projects.

## Projects

### [KVConf (tree-sitter-dotenv)](kvconf/)

Working examples of KEY=VALUE configuration files in various formats, demonstrating parser capabilities and syntax highlighting.

## Example Categories

### Configuration Files

Complete, working configuration files that demonstrate real-world usage:

- Environment files (.env)
- NPM configuration (.npmrc)
- INI files (.ini)
- Properties files (.properties)
- Git configuration (.gitconfig)

### Grammar Examples

Code snippets showing tree-sitter grammar patterns and techniques.

### Integration Examples

How to use tree-sitter parsers in different contexts:

- Command-line usage
- Node.js integration
- Editor integration
- Syntax highlighting

## Example Quality Guidelines

1. **Complete and runnable** - Examples should work as-is
2. **Well-commented** - Explain what each part does
3. **Real-world relevant** - Based on actual use cases
4. **Demonstrate features** - Show off parser capabilities
5. **Include edge cases** - Help users understand limits
