# Phase 1 Lessons Learned

## Date: 2025-08-31

### Context
Implementing Phase 1 of the typed values parser - foundation and setup.

### Key Discoveries

#### 1. Zed Extension Integration Requirements
**Problem**: The Zed extension failed to load with "Invalid node type raw_value" errors.

**Root Causes**:
1. The `highlights.scm` file referenced node types that existed in the grammar but weren't used in actual parsing
2. The grammars directory had an entire copy of tree-sitter-dotenv instead of just the WASM file
3. Node types in highlights.scm must match exactly what the parser produces

**Solution**:
- Keep highlights.scm minimal - only reference node types that are actually produced
- Clean grammars directory to contain only the WASM file
- Update highlights.scm whenever grammar changes affect node types

#### 2. Grammar Organization
**Discovery**: The existing grammar has many orphaned rules (bool, integer, string_interpolated, etc.) that aren't connected to the main parsing flow.

**Impact**: These unused rules confuse the Zed extension and make the grammar harder to understand.

**Recommendation**: When implementing Phase 2+, either:
- Remove unused rules entirely, or
- Properly integrate them into the _value choice rule

#### 3. Testing Infrastructure
**Success**: The modular test structure works well:
- validate-fixtures.js for quick validation
- regression-test.js for ensuring no breaking changes
- Separate test files for different value types

**Note**: Some test files fail parsing due to format-specific features (INI sections, properties line continuations) - this is expected and will be addressed in later phases.

#### 4. Build Process
**Key Steps for Zed Integration**:
1. `npx tree-sitter generate` - Generate parser
2. `npx tree-sitter build --wasm` - Build WASM (ignore platform warnings)
3. Update extension.toml with new commit hash
4. Copy tree-sitter-env.wasm to grammars/env.wasm
5. Ensure highlights.scm only references valid node types

### Action Items for Future Phases

1. **Phase 2 (Strings)**: 
   - When adding string_double and string_single, update highlights.scm
   - Test Zed extension after each grammar change
   - Keep track of which node types are actually produced

2. **Phase 3+ (Primitives/Complex Types)**:
   - Consider removing orphaned rules or properly integrating them
   - Update highlights.scm incrementally as new node types are added
   - Run regression tests after each change

3. **General**:
   - Add a "sync-extension" step to each phase checklist
   - Document the exact node types produced in each phase
   - Consider adding automated tests for highlights.scm validity

### Commands to Remember
```bash
# After grammar changes:
cd tree-sitter-dotenv
npx tree-sitter generate
npx tree-sitter build --wasm  # Note: --wasm replaces deprecated build-wasm
cp tree-sitter-env.wasm ../zed-env/grammars/env.wasm

# Update extension.toml with:
git rev-parse HEAD

# Test parsing (from project root):
echo "test=content" | npx tree-sitter parse -
# Note: tree-sitter parse may warn about missing parser directories
# This is not a bug - it's looking for a global config we don't need
```

### Tool Deprecations and Warnings

#### 1. tree-sitter build-wasm Deprecation
**Warning**: `build-wasm` is deprecated and will be removed in v0.24.0
**Solution**: Use `npx tree-sitter build --wasm` instead
**Status**: Not a bug - just use the new syntax

#### 2. Platform Warning for WASM Build
**Warning**: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)
**Explanation**: This warning appears on ARM Macs (M1/M2) when building WASM
**Status**: Not a bug - the WASM builds correctly despite the warning
**Impact**: None - the generated WASM works on all platforms

#### 3. Parser Directory Configuration
**Warning**: You have not configured any parser directories!
**Explanation**: tree-sitter parse looks for a global config file (~/.config/tree-sitter/config.json)
**Status**: Not a bug - we don't need global parser directories for our use case
**Workaround**: Parse directly from the grammar directory or ignore the warning

### Phase 1 Final Status

#### What We Built (Local Branch)
- Added `_spacing` rule for flexible whitespace
- Refactored to support `KEY = VALUE` format
- Prepared foundation for typed values

#### What's Actually Running (Remote Commit)
- Basic `KEY=VALUE` parsing (no spaces)
- No inline comment support
- No error handling
- All values are generic strings

#### Critical Learning
**Local changes don't affect Zed** unless:
1. Pushed to remote repository
2. Commit hash updated in extension.toml
3. Zed can fetch the commit from GitHub

This explains all the "missing" features - they exist locally but not remotely.

### Phase 1 Highlighting Behavior (Expected)

#### What Works
- Full-line comments (lines starting with #) - grey
- Basic KEY=VALUE parsing - red keys, green values, cyan =
- All characters after first = are treated as the value

#### What Doesn't Work Yet (By Design)
- Inline comments (# after values) - parsed as part of value
- Multiple equals (===) - everything after first = is the value
- Value type differentiation - all values are raw strings

These limitations are intentional for Phase 1 and will be addressed in later phases.