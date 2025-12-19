# ADR-001: Universal KEY=VALUE Parser Approach

## Status
Accepted

## Context
The tree-sitter-dotenv project initially targeted only `.env` files. However, many configuration file formats use the same basic KEY=VALUE pattern:
- `.env` files (environment variables)
- `.npmrc` files (npm configuration)
- `.ini` files (INI configuration)
- `.properties` files (Java properties)
- `.gitconfig` files (Git configuration)
- `.yarnrc` files (Yarn configuration)
- `.gemrc` files (Ruby Gem configuration)

Each format has slight variations in syntax (spacing, comments, sections) but shares the core KEY=VALUE structure.

## Decision
Create a single, universal parser that can handle all KEY=VALUE configuration formats rather than separate parsers for each format.

The parser will:
- Support flexible spacing around `=`
- Allow multiple comment styles (`#`, `;`, `//`)
- Parse but not require section headers
- Handle format-specific syntax variations
- Provide a common AST structure for all formats

## Consequences

### Positive
- **Single codebase**: One parser to maintain instead of many
- **Consistent behavior**: All KEY=VALUE files parsed the same way
- **Shared improvements**: Bug fixes and features benefit all formats
- **Simplified tooling**: One extension can support multiple file types
- **Better performance**: Single WASM module for all formats

### Negative
- **Complexity**: Grammar must handle all format variations
- **Compromises**: May not support every format-specific feature
- **Testing burden**: Must test against all supported formats
- **Larger grammar**: More rules and patterns to maintain

### Neutral
- File type detection relies on extensions rather than content
- Some format-specific features may be parsed generically
- Error handling must be permissive across formats

## Implementation Notes
The grammar uses flexible patterns:
```javascript
// Flexible spacing
_spacing: ($) => /[ \t]*/

// Multiple comment styles
comment: ($) => choice(
  /#[^\n\r]*/,
  /;[^\n\r]*/,
  /\/\/[^\n\r]*/
)

// Optional sections
section: ($) => seq('[', $.section_name, ']')
```

## References
- Original issue discussing multiple format support
- Grammar patterns for each supported format
- Test files demonstrating compatibility