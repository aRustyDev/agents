# Phase 2: String Types (Checkpoint 2.0)

## Table of Contents
- [2.1 Double-quoted Strings](#21-double-quoted-strings)
- [2.2 Single-quoted Strings](#22-single-quoted-strings)
- [2.3 Highlights for Strings](#23-highlights-for-strings)

**REMINDER: Do not start Phase 2 until Checkpoint 1.0 is approved**

## Critical Integration Steps (Lessons from Phase 1)

### Before Starting Implementation:
1. **Clean the Zed extension directory**
   ```bash
   # Ensure grammars directory only contains WASM file
   cd ../zed-env/grammars
   ls -la  # Should only show env.wasm, no env/ subdirectory
   ```

2. **Verify current highlights.scm compatibility**
   ```bash
   # Check what node types are currently referenced
   cat ../zed-env/languages/env/highlights.scm
   ```

### During Implementation:
1. **After each grammar change**:
   - Run `npx tree-sitter generate`
   - Test with `echo 'key="test"' | npx tree-sitter parse -`
   - Note which node types are produced
   
2. **Before updating highlights.scm**:
   - List all new node types that will be produced
   - Remove references to any unused node types
   - Keep highlights.scm minimal and aligned

### After Implementation:
1. **Sync Extension Checklist**:
   ```bash
   # 1. Generate and build
   cd ../tree-sitter-dotenv
   npx tree-sitter generate
   npx tree-sitter build --wasm
   
   # 2. Get commit hash
   git add -A && git commit -m "feat: implement string types"
   git rev-parse HEAD
   
   # 3. Update extension
   cd ../zed-env
   # Update extension.toml with new commit hash
   cp ../tree-sitter-dotenv/tree-sitter-env.wasm grammars/env.wasm
   
   # 4. Test in Zed
   zed test-strings.env
   ```

2. **Verify Integration**:
   - No "Invalid node type" errors in Zed logs
   - Syntax highlighting appears for strings
   - Extension loads without errors

## 2.1 Double-quoted Strings

### Pre-requisites:
- Checkpoint 1.0 approved
- Test files for strings created

### Implementation Pattern:
1. **Write failing tests first**
   ```
   ==================
   double quoted string
   ==================
   key="simple string"
   ---
   (source_file
     (variable
       name: (identifier)
       value: (string_double)))
   ```

2. **Implement grammar rule**
   ```javascript
   string_double: ($) => seq(
     '"',
     repeat(choice(
       $._string_content,
       $.interpolation,
       $.escape_sequence
     )),
     '"'
   ),
   
   // Implementation of _string_content to match non-special characters
   _string_content: ($) => /[^"$\\]+/,  // Anything except ", $, or \
   
   // Implementation of interpolation for ${VAR} syntax
   interpolation: ($) => seq(
     '${',
     field('variable', $.identifier),
     optional(seq(
       choice(':-', '-'),
       field('default', $._interpolation_default)
     )),
     '}'
   ),
   
   _interpolation_default: ($) => /[^}]+/,  // Default value in ${VAR:-default}
   
   // Implementation of escape_sequence for \" \n etc
   escape_sequence: ($) => choice(
     '\\n',   // newline
     '\\r',   // carriage return
     '\\t',   // tab
     '\\\\',  // backslash
     '\\"',   // double quote
     "\\'",   // single quote
     '\\$',   // dollar sign (to escape interpolation)
     seq('\\', /[0-7]{1,3}/),  // octal escape
     seq('\\x', /[0-9a-fA-F]{2}/),  // hex escape
     seq('\\u', /[0-9a-fA-F]{4}/),  // unicode escape
   )
   ```

3. **Update _value choice**
   ```javascript
   _value: ($) => choice(
     $.string_double,  // Add this
     alias(token.immediate(/[^\n\r]*/), $.raw_value)
   ),
   ```

4. **Test each change**
   ```bash
   just test-corpus strings
   ```

### Test Cases to Implement:
- `key="simple string"` → string_double
- `key="with ${VAR} interpolation"` → string_double with interpolation node
- `key="with ${VAR:-default} syntax"` → string_double with complex interpolation
- `key="escaped \" quotes"` → string_double with escape_sequence
- `key="multi word string"` → string_double
- `key=""` → empty string_double

### Success Criteria:
- [ ] All double-quoted string tests pass
- [ ] Interpolation only recognized inside double quotes
- [ ] Escape sequences handled correctly
- [ ] No regression in other tests

**Performance benchmark for string parsing:**

Create `test/benchmark-strings.js`:
```javascript
#!/usr/bin/env node
const Parser = require('tree-sitter');
const EnvGrammar = require('../');

const parser = new Parser();
parser.setLanguage(EnvGrammar);

// Test cases of increasing complexity
const benchmarks = [
  {
    name: 'Simple string',
    input: 'key="simple value"',
    iterations: 10000
  },
  {
    name: 'String with interpolation',
    input: 'key="Hello ${USER}, path is ${HOME}/documents"',
    iterations: 10000
  },
  {
    name: 'String with escapes',
    input: 'key="Line 1\\nLine 2\\tTabbed\\\\Backslash\\"Quote"',
    iterations: 10000
  },
  {
    name: 'Complex interpolation',
    input: 'key="User: ${USER:-nobody}, Home: ${HOME:-/tmp}, Path: ${PATH}"',
    iterations: 10000
  },
  {
    name: 'Long string (1KB)',
    input: 'key="' + 'x'.repeat(1000) + '"',
    iterations: 1000
  },
  {
    name: 'Many interpolations',
    input: 'key="' + Array(50).fill('${VAR}').join(' ') + '"',
    iterations: 1000
  }
];

console.log('String Parsing Performance Benchmark\n');
console.log('Warmup...');
// Warmup
for (let i = 0; i < 1000; i++) {
  parser.parse('warmup="test"');
}

// Run benchmarks
benchmarks.forEach(bench => {
  const start = process.hrtime.bigint();
  
  for (let i = 0; i < bench.iterations; i++) {
    parser.parse(bench.input);
  }
  
  const end = process.hrtime.bigint();
  const totalMs = Number(end - start) / 1000000;
  const avgUs = (totalMs * 1000) / bench.iterations;
  
  console.log(`\n${bench.name}:`);
  console.log(`  Input length: ${bench.input.length} chars`);
  console.log(`  Iterations: ${bench.iterations}`);
  console.log(`  Total time: ${totalMs.toFixed(2)}ms`);
  console.log(`  Average: ${avgUs.toFixed(2)}μs per parse`);
  console.log(`  Rate: ${(1000000 / avgUs).toFixed(0)} parses/second`);
});

// Memory usage
if (global.gc) {
  global.gc();
  const usage = process.memoryUsage();
  console.log('\nMemory usage:');
  console.log(`  Heap used: ${(usage.heapUsed / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  RSS: ${(usage.rss / 1024 / 1024).toFixed(2)} MB`);
} else {
  console.log('\nRun with --expose-gc for memory stats');
}
```

Add to justfile:
```just
# Run string parsing performance benchmark
benchmark-strings:
    cd tree-sitter-dotenv && node --expose-gc test/benchmark-strings.js
```

**Performance targets:**
- Simple strings: < 10μs per parse
- Strings with interpolation: < 20μs per parse
- Complex strings: < 50μs per parse
- No memory leaks over repeated parsing

## 2.2 Single-quoted Strings

### Implementation Pattern:
1. **Write tests for single quotes**
   ```
   ==================
   single quoted string
   ==================
   key='literal ${VAR} text'
   ---
   (source_file
     (variable
       name: (identifier)
       value: (string_single)))
   ```

2. **Implement grammar rule**
   ```javascript
   string_single: ($) => seq(
     "'",
     repeat(choice(
       /[^'\\]+/,  // Any char except ' or \
       $.escape_sequence
     )),
     "'"
   ),
   ```

3. **Update _value choice with precedence**
   ```javascript
   _value: ($) => choice(
     $.string_double,
     $.string_single,  // Add this
     alias(token.immediate(/[^\n\r]*/), $.raw_value)
   ),
   ```

### Success Criteria:
- [ ] Single quotes parse as string_single
- [ ] No interpolation inside single quotes
- [ ] Escape sequences work
- [ ] Precedence order maintained

## 2.3 Highlights for Strings

### Steps:
1. **Clean up existing highlights.scm first**
   ```bash
   # Remove any references to unused node types
   # Current minimal version should only have:
   # - comment
   # - raw_value
   # - identifier
   # - "="
   ```

2. **Update highlights.scm with new string types**
   ```scheme
   ; String values
   (string_double) @string
   (string_single) @string
   
   ; Interpolation
   (interpolation) @string.escape
   
   ; Different colors for quote types
   ; Double quotes and their content
   (string_double 
     "\"" @punctuation.delimiter)
   (string_double) @string.quoted.double
   
   ; Single quotes and their content  
   (string_single
     "'" @punctuation.delimiter)
   (string_single) @string.quoted.single
   
   ; Escape sequences get special highlighting
   (escape_sequence) @constant.character.escape
   
   ; Raw strings (unquoted) are different
   (raw_value) @string.unquoted
   
   ; Alternative approach using captures for quote characters
   ; This allows themes to style opening/closing quotes differently
   (string_double
     "\"" @string.quoted.double.begin
     . 
     (_)*
     .
     "\"" @string.quoted.double.end)
     
   (string_single  
     "'" @string.quoted.single.begin
     .
     (_)*
     .
     "'" @string.quoted.single.end)
   ```

2. **Build and test in Zed**
   ```bash
   just build  # includes generate, build-wasm, and test
   just sync-extension
   just install-extension
   ```

3. **Visual verification checklist**
   - [ ] Double quotes highlighted
   - [ ] Single quotes highlighted
   - [ ] Interpolated variables visible
   - [ ] Different colors for each string type

**Screenshot Examples of Expected Highlighting:**

Since we cannot include actual screenshots in this plan, here are text-based representations of how the highlighting should appear in Zed. Each color is indicated in brackets:

**Example 1: Basic Strings**
```
[gray]# String examples[/gray]
[blue]key[/blue][white]=[/white][green]"double quoted string"[/green]
[blue]another[/blue][white]=[/white][yellow]'single quoted string'[/yellow]
[blue]unquoted[/blue][white]=[/white][white]raw string value[/white]
```

**Example 2: String with Interpolation**
```
[blue]greeting[/blue][white]=[/white][green]"Hello [/green][purple]${USER}[/purple][green], welcome to [/green][purple]${HOME}[/purple][green]"[/green]
[blue]with_default[/blue][white]=[/white][green]"User: [/green][purple]${USER:-nobody}[/purple][green]"[/green]
```

**Example 3: Escape Sequences**
```
[blue]escaped[/blue][white]=[/white][green]"Line 1[/green][orange]\n[/orange][green]Line 2[/green][orange]\t[/orange][green]Tab[/green][orange]\\[/orange][green]Backslash[/green][orange]\"[/orange][green]Quote"[/green]
```

**Example 4: Mixed Quote Types**
```
[blue]double[/blue][white]=[/white][green]"This has [/green][purple]${interpolation}[/purple][green]"[/green]
[blue]single[/blue][white]=[/white][yellow]'This has literal ${text}'[/yellow]
[blue]raw[/blue][white]=[/white][white]unquoted ${text} here[/white]
```

**Color Key for Themes:**
- [gray] - Comments (`@comment`)
- [blue] - Variable names/keys (`@variable.parameter`)
- [white] - Operators and raw values (`@operator`, `@string.unquoted`)
- [green] - Double-quoted strings (`@string.quoted.double`)
- [yellow] - Single-quoted strings (`@string.quoted.single`)
- [purple] - Interpolated variables (`@string.escape`)
- [orange] - Escape sequences (`@constant.character.escape`)

**Visual Testing Guide:**

1. Create a test file `highlight-test.env`:
```env
# Test all string types
DOUBLE_PLAIN="simple double quoted"
SINGLE_PLAIN='simple single quoted'
RAW_PLAIN=unquoted raw value

# Test interpolation (only in double quotes)
DOUBLE_INTERP="Hello ${USER}, path: ${HOME}/docs"
SINGLE_INTERP='Literal ${USER} text'
RAW_INTERP=raw ${USER} text

# Test escape sequences
ESCAPED="Line1\nLine2\tTab\\Back\"Quote"
SINGLE_ESCAPE='Only \' escape works here'

# Test complex cases
COMPLEX="${USER:-default}\n\t${HOME}"
EMPTY=""
SPACES="  spaces preserved  "
```

2. Open in Zed and verify:
   - Double quotes appear in one color (typically green)
   - Single quotes appear in another color (typically yellow)
   - Interpolations within double quotes are highlighted specially
   - Escape sequences stand out from regular text
   - Raw values have minimal or no special coloring

3. Switch between different Zed themes to ensure visibility in all cases

**Checkpoint 2.0 Review Requirements**:
- String parsing works correctly: all string tests pass
- Interpolation only in double quotes: verified by tests
- Highlighting shows different string types: visual confirmation in Zed
- No regressions: all previous tests still pass

**MANDATORY EXTERNAL REVIEW BEFORE PROCEEDING**