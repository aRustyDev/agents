# Phase 1: Foundation and Setup (Checkpoint 1.0)

## Table of Contents
- [1.1 Environment Setup](#11-environment-setup)
- [1.2 Grammar Refactoring Foundation](#12-grammar-refactoring-foundation)
- [1.3 Test Infrastructure](#13-test-infrastructure)
- [Checkpoint 1.0 Review Requirements](#checkpoint-10-review-requirements)

## 1.1 Environment Setup

### Steps:
1. **Create feature branch**
   ```bash
   just new-branch feature/typed-values
   ```
   
2. **Verify clean working state**
   ```bash
   just clean
   just install
   ```

3. **Set up test infrastructure**
   - Create `test/` directory structure
   - Set up corpus test framework
   - Create test runner script

4. **Create comprehensive test files**
   
   **Pattern to follow for test file creation:**
   ```bash
   # For each file type, create a test file with this structure:
   # test-{feature}-{filetype}.{ext}
   # Example: test-strings-env.env, test-urls-npmrc.npmrc
   ```
   
   Files to create:
   - `.env` - Standard environment variables
   - `.env.local` / `.env.development` / `.env.production` - Environment-specific configs
   - `.npmrc` - NPM configuration
   - `.yarnrc` - Yarn v1 configuration  
   - `.gemrc` - Ruby Gem configuration
   - `.properties` - Java properties files
   - `.gitconfig` - Git configuration (supports KEY = VALUE)
   - `.ini` - INI configuration files
   
   **Example content for each test file type:**
   
   `.env` file example:
   ```env
   # Application settings
   NODE_ENV=development
   PORT=3000
   DATABASE_URL=postgresql://user:pass@localhost/mydb
   API_KEY="secret-key-with-spaces"
   DEBUG=true
   MAX_CONNECTIONS=100
   ```
   
   `.npmrc` file example:
   ```ini
   # Registry settings
   registry=https://registry.npmjs.org
   @mycompany:registry=https://npm.company.com
   
   # Auth tokens
   //npm.company.com/:_authToken=${NPM_TOKEN}
   
   # Package settings
   auto-install-peers=true
   strict-peer-dependencies=false
   package-import-method=clone-or-copy
   ```
   
   `.gitconfig` file example:
   ```gitconfig
   [user]
       name = John Doe
       email = john@example.com
   [core]
       autocrlf = false
       ignorecase = true
   [url "https://github.com/"]
       insteadOf = git://github.com/
   ```
   
   `.properties` file example:
   ```properties
   # Database configuration
   database.url=jdbc:mysql://localhost:3306/mydb
   database.username=root
   database.password=${DB_PASSWORD}
   
   # Application settings
   app.debug=true
   app.max_connections=100
   app.name=My Application
   ```
   
   `.ini` file example:
   ```ini
   ; Application configuration
   [database]
   host = localhost
   port = 3306
   username = root
   password = ${DB_PASSWORD}
   
   [app]
   debug = true
   name = "My Application"
   ```
   
   `.gemrc` file example:
   ```yaml
   gem: --no-document
   backtrace: true
   bulk_threshold: 1000
   sources: https://rubygems.org/
   concurrent_downloads: 8
   ```
   
   `.yarnrc` file example:
   ```conf
   # Yarn v1 configuration
   registry "https://registry.npmjs.org"
   "@mycompany:registry" "https://npm.company.com"
   disable-self-update-check true
   ```
   
   **Validation script to ensure all test files are valid:**
   
   Create `test/validate-fixtures.js`:
   ```javascript
   #!/usr/bin/env node
   const fs = require('fs');
   const path = require('path');
   const Parser = require('tree-sitter');
   const EnvGrammar = require('../');
   
   const parser = new Parser();
   parser.setLanguage(EnvGrammar);
   
   const fixtures = [
     'test-strings-env.env',
     'test-urls-npmrc.npmrc',
     'test-primitives-properties.properties',
     'test-errors-env.env',
     'test-edge-cases-ini.ini',
     'test-interpolation-env.env'
   ];
   
   let allValid = true;
   
   fixtures.forEach(fixture => {
     const filePath = path.join(__dirname, 'fixtures', fixture);
     if (!fs.existsSync(filePath)) {
       console.error(`❌ Missing: ${fixture}`);
       allValid = false;
       return;
     }
     
     const content = fs.readFileSync(filePath, 'utf8');
     const tree = parser.parse(content);
     
     if (tree.rootNode.hasError) {
       console.error(`❌ Parse error in ${fixture}`);
       console.error(`   Content: ${content.substring(0, 50)}...`);
       allValid = false;
     } else {
       console.log(`✅ Valid: ${fixture}`);
     }
   });
   
   if (!allValid) {
     console.error('\n⚠️  Some test files are invalid or missing');
     process.exit(1);
   } else {
     console.log('\n✅ All test files are valid');
   }
   ```
   
   Add to justfile:
   ```just
   # Validate all test fixtures
   validate-fixtures:
       cd ../tree-sitter-dotenv && node test/validate-fixtures.js
   ```
   
   Note: The justfile is now located at `.claude/justfile`

5. **Document project structure**
   ```
   tree-sitter-dotenv/
   ├── grammar.js          # Main grammar file
   ├── test/
   │   ├── corpus/        # Tree-sitter corpus tests
   │   ├── fixtures/      # Test files
   │   └── helpers/       # Test utilities
   └── docs/              # Documentation
   ```

### Success Criteria:
- [ ] Feature branch created and checked out
- [ ] All dependencies installed
- [ ] Test directory structure created
- [ ] At least one test file for each major format
- [ ] Project structure documented

### If You Get Stuck:
- Run `just validate-grammar` to check grammar syntax
- Use `git status` to ensure clean working directory
- Check that `node_modules/` exists after install

**Troubleshooting Guide for Common Setup Issues:**

**Issue: "command not found: just"**
- Solution: Install just using `brew install just` (macOS) or see https://github.com/casey/just

**Issue: "Cannot find module 'tree-sitter'"**
- Solution: Run `npm install` in the tree-sitter-dotenv directory
- Verify: Check that node_modules/tree-sitter exists

**Issue: "Grammar failed to compile"**
- Check syntax: `node -c grammar.js` should return no output if valid
- Common causes:
  - Missing comma in choice() or seq()
  - Unclosed parentheses or quotes
  - Invalid regex syntax
- Debug: Look for the line number in the error message

**Issue: "npx: command not found"**
- Solution: Install Node.js 14+ which includes npx
- Verify: `node --version` should show v14.0.0 or higher

**Issue: "Permission denied" when running scripts**
- Solution: `chmod +x test/validate-fixtures.js`
- Alternative: Run with `node test/validate-fixtures.js`

**Issue: Git shows many untracked files**
- Ensure .gitignore includes:
  ```
  node_modules/
  build/
  *.log
  .DS_Store
  ```
- Run `git status --ignored` to verify

**Issue: Tests fail immediately after setup**
- This is expected! The plan follows TDD - tests should fail first
- Verify setup is correct: the grammar should compile but tests fail

**Quick Verification Commands:**
```bash
# Check Node/npm installation
node --version  # Should be 14+
npm --version   # Should be 6+

# Check grammar syntax
cd tree-sitter-dotenv && node -c grammar.js

# Check tree-sitter CLI
npx tree-sitter --version

# Test basic parsing
echo "key=value" > test.env && npx tree-sitter parse test.env
```

## 1.2 Grammar Refactoring Foundation

### Pre-requisites:
- Completed step 1.1
- All test files created

### Steps:
1. **Back up current grammar**
   ```bash
   cp grammar.js grammar.js.backup
   ```

2. **Refactor variable rule**
   ```javascript
   // Pattern to follow:
   variable: ($) =>
     seq(
       field("name", $.identifier), 
       optional($._spacing),  // TODO: Implement flexible spacing
       "=",
       optional($._spacing),
       field("value", optional($._value))
     ),
   ```
   
   **Implementation of _spacing rule for flexible whitespace:**
   
   ```javascript
   // Add this rule to support optional spaces around =
   _spacing: ($) => /[ \t]*/,
   
   // Alternative if you want to capture newlines too:
   _spacing_with_newline: ($) => /[ \t\r\n]*/,
   ```
   
   **Full implementation example:**
   ```javascript
   variable: ($) =>
     seq(
       field("name", $.identifier), 
       optional($._spacing),  // Allow "key = value"
       "=",
       optional($._spacing),  // Allow "key= value" or "key = value"
       field("value", optional($._value))
     ),
   ```
   
   **Note:** The _spacing rule starts with underscore to make it hidden (not part of the parse tree).

3. **Create _value choice rule**
   ```javascript
   // Start with placeholder that maintains current behavior
   _value: ($) => alias(token.immediate(/[^\n\r]*/), $.raw_value),
   ```

4. **Run tests after each change**
   ```bash
   just generate
   just test
   ```

5. **Commit working state**
   ```bash
   just commit "refactor: prepare variable rule for typed values"
   ```

### Success Criteria:
- [ ] Grammar still generates without errors
- [ ] All existing tests pass
- [ ] Parse output unchanged from baseline
- [ ] Committed to git

### Testing Instructions:
```bash
# After each grammar change:
echo "key=value" | npx tree-sitter parse -
# Should show: (variable name: (identifier) value: (raw_value))
```

**Automated regression test script:**

Create `test/regression-test.js`:
```javascript
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Store baseline parse results
const baselineDir = path.join(__dirname, 'baseline');
const testCases = [
  'key=value',
  'key="string value"',
  'key=true',
  'key=123',
  'key=https://example.com',
  'key = value',  // spacing
  '@scope:key=value',  // namespace
  'key=${VAR}',  // interpolation
];

function ensureBaselineDir() {
  if (!fs.existsSync(baselineDir)) {
    fs.mkdirSync(baselineDir, { recursive: true });
  }
}

function generateBaseline() {
  console.log('Generating baseline parse results...');
  ensureBaselineDir();
  
  testCases.forEach((testCase, index) => {
    const filename = `test${index}.env`;
    const filePath = path.join(baselineDir, filename);
    fs.writeFileSync(filePath, testCase);
    
    const output = execSync(`npx tree-sitter parse ${filePath}`, {
      cwd: path.join(__dirname, '..'),
      encoding: 'utf8'
    });
    
    fs.writeFileSync(filePath + '.baseline', output);
    console.log(`✅ Baseline saved for: ${testCase}`);
  });
}

function runRegression() {
  console.log('Running regression tests...');
  let failures = 0;
  
  testCases.forEach((testCase, index) => {
    const filename = `test${index}.env`;
    const filePath = path.join(baselineDir, filename);
    const baselinePath = filePath + '.baseline';
    
    if (!fs.existsSync(baselinePath)) {
      console.error(`❌ Missing baseline for: ${testCase}`);
      failures++;
      return;
    }
    
    const currentOutput = execSync(`npx tree-sitter parse ${filePath}`, {
      cwd: path.join(__dirname, '..'),
      encoding: 'utf8'
    });
    
    const baseline = fs.readFileSync(baselinePath, 'utf8');
    
    if (currentOutput.trim() !== baseline.trim()) {
      console.error(`❌ Regression in: ${testCase}`);
      console.error('Expected:', baseline.trim());
      console.error('Got:', currentOutput.trim());
      failures++;
    } else {
      console.log(`✅ No regression: ${testCase}`);
    }
  });
  
  if (failures > 0) {
    console.error(`\n❌ ${failures} regression(s) found`);
    process.exit(1);
  } else {
    console.log('\n✅ All regression tests passed');
  }
}

// Main
const command = process.argv[2];
if (command === 'baseline') {
  generateBaseline();
} else if (command === 'test') {
  runRegression();
} else {
  console.log('Usage:');
  console.log('  node regression-test.js baseline  # Generate baselines');
  console.log('  node regression-test.js test      # Run regression tests');
}
```

Add to justfile:
```just
# Generate regression test baselines
regression-baseline:
    cd tree-sitter-dotenv && node test/regression-test.js baseline

# Run regression tests
regression-test:
    cd tree-sitter-dotenv && node test/regression-test.js test
```

## 1.3 Test Infrastructure

### Steps:
1. **Create corpus test structure**
   
   **Pattern for corpus tests:**
   ```
   ==================
   Test name
   ==================
   input text here
   ---
   expected parse tree here
   ```

2. **Set up test categories**
   ```
   corpus/
   ├── basic.txt          # Basic KEY=VALUE
   ├── strings.txt        # String value types
   ├── primitives.txt     # Bool, int values
   ├── uris.txt          # URI/URL values
   ├── errors.txt        # Error cases
   └── formats.txt       # Format-specific tests
   ```

3. **Create test runner script**
   ```javascript
   // test/run-tests.js
   /**
    * Test runner that validates parse trees match expected output
    */
   const fs = require('fs');
   const path = require('path');
   const Parser = require('tree-sitter');
   const EnvGrammar = require('../');
   
   const parser = new Parser();
   parser.setLanguage(EnvGrammar);
   
   class TestRunner {
     constructor() {
       this.passed = 0;
       this.failed = 0;
       this.errors = [];
     }
     
     parseExpectedTree(expectedStr) {
       // Convert the expected tree format to a comparable structure
       // Remove whitespace and normalize
       return expectedStr
         .replace(/\s+/g, ' ')
         .replace(/\(\s+/g, '(')
         .replace(/\s+\)/g, ')')
         .trim();
     }
     
     parseActualTree(tree) {
       // Convert actual tree to string format
       return tree.rootNode.toString()
         .replace(/\s+/g, ' ')
         .replace(/\(\s+/g, '(')
         .replace(/\s+\)/g, ')')
         .trim();
     }
     
     runTest(name, input, expected) {
       try {
         const tree = parser.parse(input);
         const actualTree = this.parseActualTree(tree);
         const expectedTree = this.parseExpectedTree(expected);
         
         if (actualTree === expectedTree) {
           this.passed++;
           console.log(`✅ ${name}`);
         } else {
           this.failed++;
           this.errors.push({
             name,
             expected: expectedTree,
             actual: actualTree
           });
           console.log(`❌ ${name}`);
           console.log(`   Expected: ${expectedTree}`);
           console.log(`   Actual:   ${actualTree}`);
         }
       } catch (error) {
         this.failed++;
         this.errors.push({
           name,
           error: error.message
         });
         console.log(`❌ ${name} - Error: ${error.message}`);
       }
     }
     
     runTestFile(filePath) {
       const content = fs.readFileSync(filePath, 'utf8');
       const tests = content.split(/={10,}/);
       
       tests.forEach(test => {
         if (!test.trim()) return;
         
         const lines = test.trim().split('\n');
         const name = lines[0].trim();
         const separatorIndex = lines.findIndex(line => line.startsWith('---'));
         
         if (separatorIndex === -1) {
           console.error(`⚠️  Invalid test format in ${name}`);
           return;
         }
         
         const input = lines.slice(1, separatorIndex).join('\n').trim();
         const expected = lines.slice(separatorIndex + 1).join('\n').trim();
         
         this.runTest(name, input, expected);
       });
     }
     
     runAllTests(corpusDir) {
       const files = fs.readdirSync(corpusDir)
         .filter(f => f.endsWith('.txt'));
       
       files.forEach(file => {
         console.log(`\nRunning tests in ${file}:`);
         this.runTestFile(path.join(corpusDir, file));
       });
       
       console.log('\n' + '='.repeat(50));
       console.log(`Total: ${this.passed + this.failed} tests`);
       console.log(`Passed: ${this.passed}`);
       console.log(`Failed: ${this.failed}`);
       
       if (this.failed > 0) {
         console.log('\nFailed tests:');
         this.errors.forEach(err => {
           console.log(`- ${err.name}`);
           if (err.error) {
             console.log(`  Error: ${err.error}`);
           }
         });
         process.exit(1);
       }
     }
   }
   
   // Main
   if (require.main === module) {
     const corpusDir = path.join(__dirname, 'corpus');
     const runner = new TestRunner();
     runner.runAllTests(corpusDir);
   }
   
   module.exports = TestRunner;
   ```

4. **Add test commands to justfile**
   ```just
   # Run specific test category
   test-corpus CATEGORY:
       cd tree-sitter-dotenv && npx tree-sitter test -f {{CATEGORY}}
   ```

### Success Criteria:
- [ ] Corpus directory structure created
- [ ] At least 3 tests per category
- [ ] Test runner functional
- [ ] All tests documented

**Guide for Writing Effective Corpus Tests:**

**Corpus Test Format:**
```
==================
Test name (descriptive, unique)
==================
input text to parse
---
(expected_parse_tree
  (with proper nesting)
  (and field names))
```

**Best Practices:**

1. **One concept per test**
   ```
   ==================
   simple boolean value
   ==================
   key=true
   ---
   (source_file
     (variable
       name: (identifier)
       value: (bool)))
   ```

2. **Test edge cases**
   ```
   ==================
   boolean with trailing space
   ==================
   key=true 
   ---
   (source_file
     (variable
       name: (identifier)
       value: (bool)))
   ```

3. **Test failures explicitly**
   ```
   ==================
   multiple values error
   ==================
   key=true false
   ---
   (source_file
     (variable
       name: (identifier)
       value: (bool))
     (error_multiple_values))
   ```

4. **Use descriptive names**
   - Good: "double quoted string with interpolation"
   - Bad: "test 1" or "string test"

5. **Include field names in expected output**
   ```
   (variable
     name: (identifier)    # Include field names
     value: (string_double))
   ```

6. **Test precedence**
   ```
   ==================
   string precedence over bool
   ==================
   key="true"
   ---
   (source_file
     (variable
       name: (identifier)
       value: (string_double)))  # Not (bool)
   ```

7. **Group related tests**
   - Put all string tests in strings.txt
   - Put all error tests in errors.txt
   - Keep files focused and manageable

8. **Document special cases**
   ```
   ==================
   empty value (valid in many formats)
   ==================
   key=
   ---
   (source_file
     (variable
       name: (identifier)
       value: (empty)))
   ```

**Common Mistakes to Avoid:**

1. **Missing whitespace in expected output**
   - Parser output has specific spacing
   - Use the actual parser output as reference

2. **Wrong node names**
   - Verify node names match grammar rules
   - Hidden rules (starting with _) won't appear

3. **Missing ERROR nodes**
   - Parser may include ERROR nodes for invalid syntax
   - Include these in expected output

4. **Incorrect nesting**
   - Pay attention to parentheses
   - Field names are at the same level as their values

**Debugging Tips:**

1. **Generate actual output first**
   ```bash
   echo "your test input" | npx tree-sitter parse -
   ```

2. **Use --debug flag for details**
   ```bash
   echo "your test input" | npx tree-sitter parse --debug -
   ```

3. **Check grammar rules**
   - Verify rule names in grammar.js
   - Check precedence and conflicts

4. **Start simple**
   - Test basic cases first
   - Add complexity incrementally

**Example Test File Structure:**
```
==================
basic assignment
==================
key=value
---
(source_file
  (variable
    name: (identifier)
    value: (raw_value)))

==================
quoted string
==================
key="value"
---
(source_file
  (variable
    name: (identifier)
    value: (string_double)))

==================
string with interpolation
==================
key="Hello ${USER}"
---
(source_file
  (variable
    name: (identifier)
    value: (string_double
      (interpolation
        (identifier)))))
```

**Checkpoint 1.0 Review Requirements**: 
- Grammar still compiles: `just generate` succeeds
- Existing functionality preserved: baseline tests pass
- Test infrastructure ready: can run corpus tests
- Documentation updated: README reflects changes

**MANDATORY EXTERNAL REVIEW BEFORE PROCEEDING**