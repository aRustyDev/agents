# ADR-003: Value Type Precedence Strategy

## Status
Accepted

## Context
Configuration values can be ambiguous. For example:
- `"true"` - Is this the string "true" or the boolean true in quotes?
- `123` - Is this a number or a string that happens to be numeric?
- `https://example.com` - Is this a URL or just a string?
- `true` - Boolean or unquoted string?

Different configuration formats have different conventions:
- `.env` files often treat everything as strings
- `.properties` files have implicit type coercion
- `.npmrc` files have explicit boolean values

We need a consistent precedence order to resolve ambiguities.

## Decision
Implement a strict precedence order for value type detection:

1. **Double-quoted strings** (highest precedence)
2. **Single-quoted strings**
3. **Boolean values** (true/false)
4. **Integer values**
5. **URI values** (URLs, URNs, etc.)
6. **Raw/unquoted strings** (lowest precedence)

### Implementation Strategy
```javascript
_value: ($) => choice(
  $.string_double,    // "value" - always a string
  $.string_single,    // 'value' - always a string
  $.boolean,          // true or false (unquoted)
  $.integer,          // 123, -456
  $.uri,              // https://..., ftp://..., etc.
  $.raw_value         // anything else
)
```

### Precedence Rules
- **Quoted always wins**: `"true"` is string "true", not boolean
- **Exact matches only**: `true` is boolean, `True` or `TRUE` is raw string
- **No implicit conversion**: `"123"` is string, not number
- **URIs require scheme**: `https://example.com` is URI, `example.com` is raw

## Consequences

### Positive
- **Predictable parsing**: Clear rules for ambiguous values
- **Preserves intent**: Quotes explicitly indicate strings
- **Type safety**: Tools can rely on consistent type detection
- **Cross-format compatibility**: Works across all KEY=VALUE formats

### Negative
- **Breaking changes**: May parse differently than format-specific parsers
- **Strictness**: No fuzzy matching (e.g., `True` ≠ `true`)
- **URI complexity**: Must maintain list of valid URI schemes

### Neutral
- Some formats may need post-processing for format-specific rules
- Error messages must explain why a value has a specific type
- Documentation crucial for user understanding

## Examples

### String Precedence
```bash
# Double quotes - always string
DEBUG="true"          # string: "true"
PORT="3000"          # string: "3000"
URL="https://api.com" # string: "https://api.com"

# Single quotes - always string  
DEBUG='false'        # string: "false"
COUNT='42'           # string: "42"
```

### Boolean Detection
```bash
# Exact match only
DEBUG=true           # boolean: true
DEBUG=false          # boolean: false
DEBUG=True           # raw: "True" (case sensitive)
DEBUG=TRUE           # raw: "TRUE" (case sensitive)
DEBUG=yes            # raw: "yes" (not a boolean)
```

### Numeric Detection
```bash
# Integers only (no decimals in phase 3)
PORT=3000            # integer: 3000
PORT=-1              # integer: -1
PORT=3.14            # raw: "3.14" (not an integer)
PORT=0x123           # raw: "0x123" (no hex support)
```

### URI Detection
```bash
# Must have valid scheme
API=https://api.com       # uri
API=http://localhost:3000 # uri
API=ftp://files.com       # uri
API=api.com              # raw: "api.com" (no scheme)
API=//api.com            # raw: "//api.com" (no scheme)
```

## Grammar Implementation
```javascript
// Precedence defined by choice order
_value: ($) => choice(
  prec(5, $.string_double),
  prec(5, $.string_single),
  prec(4, $.boolean),
  prec(3, $.integer),
  prec(2, $.uri),
  prec(1, $.raw_value)
),

// Strict patterns
boolean: ($) => token(choice('true', 'false')),
integer: ($) => token(/[+-]?\d+/),
uri: ($) => token(/[a-z][a-z0-9+.-]*:\/\/[^\s]*/),
```

## Testing Strategy
Create comprehensive tests for edge cases:
```
==================
boolean vs string precedence
==================
VALUE="true"
---
(variable value: (string_double))

==================
integer vs raw precedence  
==================
VALUE=123abc
---
(variable value: (raw_value))
```

## Migration Notes
Projects using this parser should:
1. Review existing value parsing assumptions
2. Update documentation about type detection
3. Test with real configuration files
4. Consider post-processing for format-specific rules

## References
- [Value Types Implementation Plan](../../plans/tree-sitter/kvconf/02-phase2-strings.md)
- Test corpus for precedence validation
- Performance benchmarks for type detection