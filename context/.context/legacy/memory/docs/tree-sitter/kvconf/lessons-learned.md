# Lessons Learned - Tree-sitter KVConf Project

## Overview

This document captures key insights, technical discoveries, and best practices learned during the development of the tree-sitter-dotenv parser (kvconf project).

## Technical Lessons

### Parser State Machine Bug Discovery
**Context**: Attempting to parse simple KEY=VALUE patterns
**Discovery**: The parser was incorrectly tokenizing `key=value` as two separate variables
**Solution**: Use `token.immediate` to prevent lexer state transitions
**Example**:
```javascript
// Problem: This allows lexer to enter wrong state
variable: ($) => seq(
  field("name", $.identifier),
  "=",
  field("value", optional($.value))
)

// Solution: Force tight coupling
variable: ($) => seq(
  field("name", $.identifier),
  token.immediate("="),
  field("value", optional(alias(token.immediate(/[^\n\r]*/), $.value)))
)
```
**References**: [ADR-002](adr/ADR-002-token-immediate-parser-fix.md), [Parser Bug Analysis](analysis/ANALYSIS.md)

### Value Type Precedence Critical
**Context**: Parsing ambiguous values like "true" vs true
**Discovery**: Order of choice alternatives determines parsing behavior
**Solution**: Strict precedence: strings > booleans > integers > URIs > raw
**Example**:
```javascript
_value: ($) => choice(
  $.string_double,    // "true" is string, not boolean
  $.string_single,    // 'true' is string, not boolean
  $.boolean,          // true is boolean
  $.integer,          // 123 is integer
  $.uri,              // https://... is URI
  $.raw_value         // anything else
)
```
**References**: [ADR-003](adr/ADR-003-value-type-precedence.md)

### Lexer State Understanding Essential
**Context**: Debugging parser behavior
**Discovery**: Tree-sitter's lexer has states that affect tokenization
**Solution**: Understand when lexer can accept new tokens vs continue current token
**Example**: After parsing "=", the lexer was in a state where it could accept identifiers, causing values to be misinterpreted
**References**: Deep debugging sessions documented in analysis

## Tool-Specific Lessons

### Zed Extension Caching
**Discovery**: Zed aggressively caches extension files and grammar
**Impact**: Changes don't reflect even after reinstalling extension
**Workaround**:
```bash
# Clear all Zed caches
rm -rf ~/Library/Caches/Zed
# Restart Zed completely
# Reinstall extension
```
**Version**: Zed 0.160.7 (as of project time)

### Tree-sitter CLI Debugging
**Discovery**: `--debug` flag provides invaluable parser state information
**Usage**:
```bash
echo "key=value" | npx tree-sitter parse --debug -
```
**Benefit**: Shows exactly how parser is tokenizing input
**Note**: May warn about missing parser directories - this is normal without global config

### WASM Building Quirks
**Discovery**: WASM build can succeed but produce incorrect output if grammar has issues
**Solution**: Always test WASM output matches native parser output
**Command**: `npx tree-sitter build --wasm` (replaces deprecated `build-wasm`)
**Platform Warning**: ARM Macs show platform mismatch warning - this is harmless

## Anti-Patterns to Avoid

### Overly Complex Regex in Grammar
**Why it's problematic**: Causes exponential parsing time on certain inputs
**Better approach**: Use simpler patterns with explicit precedence
**Example**:
```javascript
// Bad: Complex regex with backtracking
identifier: ($) => /[a-zA-Z_][a-zA-Z0-9_-]*(@[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+)?/

// Good: Explicit choice
identifier: ($) => choice(
  /[a-zA-Z_][a-zA-Z0-9_-]*/,
  seq('@', /[a-zA-Z0-9_-]+/, ':', /[a-zA-Z0-9_-]+/)
)
```

### Assuming File Format Consistency
**Why it's problematic**: Different KEY=VALUE formats have subtle differences
**Better approach**: Design for flexibility from the start
**Example**: `.npmrc` uses `//host/:key=value`, `.properties` allows `key:value`

### Ignoring Error Recovery
**Why it's problematic**: One syntax error breaks entire file parsing
**Better approach**: Design grammar to continue after errors
**Example**: Use optional error nodes, narrow error scope

## Performance Insights

### String Parsing Optimization
**Measurement**: String parsing initially took 50μs per line
**Optimization**: Use `token()` wrapper for better performance
**Result**: Reduced to <10μs per line
**Impact**: 5x performance improvement

### Large File Handling
**Target**: <100ms for 1000-line files
**Achievement**: 78ms average with optimized grammar
**Key factors**:
- Avoid backtracking in regex
- Use precedence instead of ordered choice
- Minimize lookahead

## Best Practices Discovered

### Test-Driven Grammar Development
1. Write corpus test first
2. See it fail with current grammar
3. Implement minimal grammar change
4. Verify test passes
5. Check for regressions

### Incremental Parser Development
- Start with most basic case (KEY=VALUE)
- Add one feature at a time
- Test thoroughly before adding next feature
- Keep previous tests passing

### Documentation as You Go
- Document discoveries immediately in notes
- Create ADRs for significant decisions
- Update help guides with solutions
- Keep examples current

## File Format Specific Insights

### .npmrc Peculiarities
- URL-style keys: `//registry.npmjs.org/:_authToken`
- Scoped packages: `@mycompany:registry`
- No spaces around equals

### .env Conventions
- Everything is a string by default
- Shell-style interpolation expected
- Quotes are significant

### .properties Flexibility
- Allows `=`, `:`, or space as separator
- Supports line continuation with `\`
- Both `#` and `!` as comments

## Integration Insights

### Editor Integration Challenges
- Caching is aggressive in modern editors
- Hot reload often doesn't work for grammars
- Syntax highlighting queries need careful testing

### Multi-Format Support Strategy
- One grammar, multiple file extensions
- Consistent AST across formats
- Format-specific post-processing when needed

## Future Considerations

Based on our experience, future tree-sitter projects should:

1. **Start with state machine design** - Understand lexer states early
2. **Plan for multiple formats** - Even if starting with one
3. **Implement error recovery early** - Not as an afterthought
4. **Set performance targets upfront** - And test regularly
5. **Document patterns thoroughly** - Future you will thank you

## Phase 2 Specific Lessons

### Hidden Rules and Field Assignment
**Context**: Implementing interpolation with default values
**Discovery**: Hidden rules (prefixed with _) don't properly support field assignment
**Solution**: Convert to visible rules when fields are needed
**Example**:
```javascript
// Problem: Field assignment doesn't work
_interpolation_value: ($) => /[^}]+/,
interpolation_default: ($) =>
  seq('${', field('name', $.identifier), ':-', field('default', $._interpolation_value), '}')

// Solution: Make rule visible
interpolation_value: ($) => /[^}]+/,
interpolation_default: ($) =>
  seq('${', field('name', $.identifier), ':-', field('default', $.interpolation_value), '}')
```

### Inline Comments Limitation
**Context**: Supporting comments after values (e.g., `KEY=value # comment`)
**Discovery**: Tree-sitter doesn't support lookahead patterns, making inline comments difficult
**Current Status**: Known limitation - inline comments are parsed as part of raw_value
**Workaround**: Users should place comments on separate lines
**Future Fix**: Requires significant grammar restructuring or external scanner
**Example**:
```bash
# Preferred (works correctly)
# This is a comment about KEY
KEY=value

# Limited support (comment parsed as part of value)
KEY=value # this comment is part of the value
```

### Single-Quoted Strings Must Be Literal
**Context**: Phase 2 string implementation
**Discovery**: Single-quoted strings should not process escape sequences
**Solution**: Use simple pattern without escape sequence support
**Example**:
```javascript
// Correct: Single quotes are literal
string_single: ($) => seq("'", repeat(/[^']+/), "'")
// Wrong: Would process escapes
string_single: ($) => seq("'", repeat(choice($.escape_sequence, /[^'\\]+/)), "'")
```

### Escape Sequence Highlighting Scope
**Context**: Fixing escape sequence highlighting in single-quoted strings
**Discovery**: Global escape sequence highlighting affects all strings
**Solution**: Scope escape sequence highlighting to specific string types
**Example**:
```scheme
; Wrong: Highlights escapes in all contexts
(escape_sequence) @constant.character.escape

; Correct: Only in double-quoted strings
(string_double (escape_sequence) @constant.character.escape)
```

## Zed Extension Development Lessons

### Extension TOML Parsing Issues
**Context**: Modifying extension.toml for development
**Discovery**: Zed's TOML parser is very strict about field order and structure
**Common Errors**:
```
missing field `repository`
TOML parse error at line 9, column 1
```
**Solution**: Ensure all required fields are present and properly formatted
**Best Practice**: Always validate extension.toml after manual edits

### Commit Hash Requirements
**Context**: Updating extension to use new parser commits
**Discovery**: Zed requires full commit hashes when fetching from GitHub
**Example**:
```toml
# Wrong: Short hash fails
commit = "3f39139"

# Correct: Full hash works
commit = "3f39139f04d6da64ac920c3bc3e110c5ff60d7f8"
```
**Command**: `git log -1 --format="%H"` to get full hash

### Highlights.scm Synchronization
**Context**: Parser changes require highlighting updates
**Discovery**: Both parser repo and extension must have matching highlights.scm
**Required Steps**:
1. Update queries/highlights.scm in parser repo
2. Update languages/env/highlights.scm in extension
3. Push parser changes first
4. Update extension commit reference
5. Rebuild/reinstall extension

### Extension Debugging Workflow
**Best Practice for Each Phase**:
1. Implement parser changes
2. Update highlights.scm in parser repo
3. Commit and push to feature branch
4. Copy highlights.scm to extension
5. Update extension.toml with new commit
6. Test in Zed with verification file
7. Document any highlighting issues

## Phase 3: Primitive Types Lessons

### Token Precedence is Critical
**Context**: Implementing boolean and integer types
**Problem**: Raw values were matching before typed values
**Solution**: Use `token(prec(n, ...))` to set lexer-level precedence
**Example**:
```javascript
// Higher precedence = matched first
bool: ($) => token(prec(2, choice('true', 'false'))),
integer: ($) => token(prec(1, /[+-]?\d+/)),
raw_value: ($) => prec(-1, /[^"'\n\r][^\n\r]*/),
```

### Token Wrapper Conflicts
**Context**: Parser failing to match `key=value` correctly
**Discovery**: `token(prec(-1, ...))` on raw_value caused lexer conflicts
**Solution**: Remove token wrapper, keep only precedence
**Example**:
```javascript
// Wrong: Creates lexer conflict
raw_value: ($) => token(prec(-1, /[^"'\n\r][^\n\r]*/)),

// Correct: Precedence without token wrapper
raw_value: ($) => prec(-1, /[^"'\n\r][^\n\r]*/),
```

### Lexer Tokenization Behavior
**Context**: Values like `123abc` parsed as integer + identifier
**Discovery**: Tree-sitter's lexer creates discrete tokens before parsing
**Impact**: Cannot parse mixed alphanumeric as single token without external scanner
**Workaround**: Document as known limitation, recommend quoting

### Comments After Typed Values Work
**Context**: Testing inline comments with booleans and integers
**Discovery**: Comments parse correctly after typed values (bool, integer, string)
**Insight**: Only raw_value consumes comments due to its greedy regex
**Example**:
```bash
DEBUG=true # ✓ Parses as bool + comment
PORT=3000 # ✓ Parses as integer + comment
NAME=value # ✗ Comment part of raw_value
```

## Summary

The most critical lesson: **Understanding tree-sitter's lexer state machine is essential**. The `token.immediate` pattern solved our core parsing bug and would have saved weeks if known earlier. When building parsers, invest time in understanding the tool's internals, not just its API.

Phase 3 reinforced this: The distinction between parser-level precedence (`prec()`) and lexer-level precedence (`token(prec())`) is crucial for controlling which tokens are matched when multiple patterns could apply at the same position.