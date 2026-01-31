# Phase 5: Edge Cases and Polish (Checkpoint 5.0)

## User's Zed Theme Color Map
- **Orange**: booleans, integers
- **Green**: strings
- **White**: raw_values
- **Grey**: comments
- **Cyan**: operators
- **Red**: errors/keys (variable names)

## Table of Contents
- [5.1 Edge Case Handling](#51-edge-case-handling)
- [5.2 Performance Optimization](#52-performance-optimization)
- [5.3 Comprehensive Testing](#53-comprehensive-testing)

**REMINDER: Do not start Phase 5 until Checkpoint 4.0 is approved**

## Critical Zed Integration Steps

### Phase 5 Specific Requirements:
1. **Performance Testing with Zed**:
   - Test parser performance with large .env files in Zed
   - Monitor syntax highlighting lag
   - Check memory usage with complex files

2. **Edge Case Verification**:
   - Create phase5-edge-cases.env with all edge cases
   - Test in Zed for visual artifacts
   - Ensure error recovery doesn't break highlighting

3. **Final Integration Checklist**:
   ```bash
   # Before final push
   npx tree-sitter test  # All tests pass
   npx tree-sitter build --wasm  # WASM builds
   
   # Commit and get hash
   git add -A
   git commit -m "feat(phase5): Complete edge case handling"
   git push origin feature/typed-values
   git log -1 --format="%H"
   ```

4. **Zed Extension Polish (WITH HASH VERIFICATION)**:
   ```bash
   # MANDATORY: Update extension after EVERY grammar change
   cd tree-sitter-dotenv
   git add -A && git commit -m "Phase 5: <description>"
   git push origin feature/typed-values
   
   # Get FULL hash (40 chars) - DO NOT TRUNCATE
   FULL_HASH=$(git log -1 --format="%H")
   echo "Full hash: $FULL_HASH (length: ${#FULL_HASH})"
   
   # Verify on GitHub
   git ls-remote origin | grep "$FULL_HASH" || exit 1
   
   # Update extension
   cd ../zed-env
   sed -i '' "s/commit = \".*\"/commit = \"$FULL_HASH\"/" extension.toml
   grep "commit = " extension.toml  # VERIFY 40 chars
   
   # Copy latest highlights
   cp ../tree-sitter-dotenv/queries/highlights.scm languages/env/highlights.scm
   
   # Test and install
   zed --install-dev-extension .
   ```

## MCP Tool Integration

### MANDATORY: Use tree-sitter MCP tools throughout Phase 5

**CRITICAL REQUIREMENT**: You MUST use the MCP tools as the PRIMARY method for analysis and development. Only fall back to CLI tools when MCP tools are unavailable or as a secondary verification.

### Required MCP Tool Usage:
1. **Edge Case Discovery**:
   ```bash
   # Find existing edge case handling patterns
   mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="ERROR|error|edge" file_pattern="**/*.{js,txt}"
   
   # Search for similar edge case tests
   mcp__tree_sitter__find_similar_code project="tree-sitter-dotenv" snippet="ERROR" language="javascript"
   ```

2. **Performance Profiling**:
   ```bash
   # Analyze complexity of edge case patterns
   mcp__tree_sitter__analyze_complexity project="tree-sitter-dotenv" file_path="grammar.js"
   
   # Find performance-critical regex patterns
   mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="/\\\\[\\\\s\\\\S]*\\\\+/" file_pattern="grammar.js"
   ```

3. **Real-World Pattern Analysis**:
   ```bash
   # Search collected real-world files for edge patterns
   mcp__tree_sitter__list_files project="tree-sitter-dotenv" pattern="test/real-world-configs/*.env" | while read file; do
     mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="\\\\$\\\\{|#|=" file_pattern="$file" context_lines=1
   done
   ```

4. **Test Coverage Gap Analysis**:
   ```bash
   # Find untested node types
   mcp__tree_sitter__run_query project="tree-sitter-dotenv" query="(_) @node" language="javascript" file_path="grammar.js" | \
     compare with test coverage
   ```

## 5.1 Edge Case Handling

**MCP TOOLS REQUIRED**: Use `mcp__tree_sitter__get_ast` and `mcp__tree_sitter__run_query` to analyze how the parser handles edge cases BEFORE implementing fixes.

### Cases to handle:
1. **Empty values**
   ```
   key=
   key= # comment after empty
   ```
   
2. **Whitespace handling**
   ```
   key = value  # spaces around =
   key=  value  # spaces before value
   ```

3. **Special characters**
   ```
   key=value\with\backslashes
   key=value@with@symbols
   key=value#not-a-comment
   ```

4. **Long values**
   ```
   key=very long value that might span multiple visual lines but is still one logical line in the file...
   ```

5. **Error Node Types (deferred from Phase 4)**
   ```javascript
   // Specific error types for better error reporting
   error_trailing_comma: ($) => ',',
   error_multiple_values: ($) => /[^\n\r#]+/,
   error_missing_equals: ($) => token('='),
   error: ($) => /[^\n\r]+/,  // Catch-all
   ```
   
   Test cases:
   ```env
   # Multiple values on one line
   KEY=value1 value2 value3    # Should show error_multiple_values
   
   # Trailing content after typed values
   BOOL=true false             # bool + error_multiple_values
   INT=123 456                 # integer + error_multiple_values
   URL=https://example.com extra text  # url + error_multiple_values
   
   # Missing equals
   KEY VALUE                   # Should show error_missing_equals
   
   # Mixed errors
   KEY=123abc                  # integer + error (known issue)
   ```

### Implementation checklist:
**MANDATORY**: For EACH item below, use MCP tools FIRST:
- Use `mcp__tree_sitter__get_ast` to examine parse trees
- Use `mcp__tree_sitter__run_query` to find error nodes
- Use `mcp__tree_sitter__find_text` to search for patterns
- [ ] Empty values parse as empty raw_value
- [ ] Flexible spacing works
- [ ] Special characters handled
- [ ] Performance acceptable for long lines
- [ ] Error node types implemented for better error reporting
- [ ] Error nodes properly highlighted in Zed (red color)

### Stress Test Generator
Create `test/generators/edge-case-generator.js`:
```javascript
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

class EdgeCaseGenerator {
  constructor(outputDir = 'test/edge-cases') {
    this.outputDir = outputDir;
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
  }
  
  // Generate test cases for empty values
  generateEmptyValues() {
    const cases = [
      'EMPTY=',
      'EMPTY_WITH_COMMENT= # this is empty',
      'EMPTY_WITH_SPACE= ',
      'EMPTY_WITH_TAB=\t',
      'EMPTY_NEWLINE=\n',
      'MULTIPLE_EMPTY=\n\nANOTHER_EMPTY=',
    ];
    
    const content = cases.join('\n');
    fs.writeFileSync(path.join(this.outputDir, 'empty-values.env'), content);
    return cases.length;
  }
  
  // Generate test cases for whitespace variations
  generateWhitespaceVariations() {
    const cases = [
      'NO_SPACE=value',
      'SPACE_BEFORE_EQUALS =value',
      'SPACE_AFTER_EQUALS= value',
      'SPACES_BOTH_SIDES = value',
      'MULTIPLE_SPACES  =  value',
      'TAB_BEFORE_EQUALS\t=value',
      'TAB_AFTER_EQUALS=\tvalue',
      'MIXED_WHITESPACE \t = \t value',
      'TRAILING_SPACE=value ',
      'TRAILING_TAB=value\t',
    ];
    
    const content = cases.join('\n');
    fs.writeFileSync(path.join(this.outputDir, 'whitespace.env'), content);
    return cases.length;
  }
  
  // Generate test cases with special characters
  generateSpecialCharacters() {
    const cases = [
      'BACKSLASHES=C:\\Users\\path\\to\\file',
      'FORWARD_SLASHES=/usr/local/bin/app',
      'MIXED_SLASHES=C:/Users\\Documents/file',
      'AT_SYMBOLS=user@example.com@v1.0',
      'HASH_IN_VALUE=value#not-a-comment',
      'DOLLAR_SIGNS=price$99.99$USD',
      'AMPERSANDS=param1=a&param2=b&param3=c',
      'PIPES=command|grep|awk|sed',
      'BRACKETS=array[0][key]={value}',
      'UNICODE=emoji_🎉_celebration_🚀',
      'CONTROL_CHARS=line1\\nline2\\ttab\\rreturn',
      'QUOTES_MIX=it\'s "mixed" `quotes` here',
      'PARENTHESES=(value (nested) more)',
      'MATH_SYMBOLS=1+2*3/4-5=result',
      'REGEX_LIKE=^start.*middle.*end$',
    ];
    
    const content = cases.join('\n');
    fs.writeFileSync(path.join(this.outputDir, 'special-chars.env'), content);
    return cases.length;
  }
  
  // Generate very long values
  generateLongValues() {
    const cases = [];
    
    // Long continuous string
    cases.push(`LONG_CONTINUOUS=${'x'.repeat(1000)}`);
    
    // Long URL with many parameters
    const params = Array(50).fill(0).map((_, i) => `param${i}=value${i}`).join('&');
    cases.push(`LONG_URL=https://example.com/api/v1/endpoint?${params}`);
    
    // Long path
    const deepPath = Array(50).fill('folder').join('/');
    cases.push(`LONG_PATH=/root/${deepPath}/file.txt`);
    
    // Long JSON-like value
    const jsonLike = JSON.stringify(Array(100).fill({key: 'value', nested: {data: 'test'}}));
    cases.push(`LONG_JSON=${jsonLike}`);
    
    // Long base64
    const base64 = Buffer.from('x'.repeat(1000)).toString('base64');
    cases.push(`LONG_BASE64=${base64}`);
    
    const content = cases.join('\n');
    fs.writeFileSync(path.join(this.outputDir, 'long-values.env'), content);
    return cases.length;
  }
  
  // Generate edge cases that might break parsers
  generateParserBreakers() {
    const cases = [
      // Keys that look like comments
      '#KEY=value',
      ';KEY=value',
      '//KEY=value',
      
      // Keys with equals signs
      'KEY=WITH=EQUALS=value',
      'KEY==value',
      '===value',
      
      // Values that look like variables
      'KEY=$VALUE',
      'KEY=${VALUE}',
      'KEY=$(command)',
      'KEY=`command`',
      
      // Incomplete syntax
      'KEY=${INCOMPLETE',
      'KEY="incomplete',
      'KEY=\'incomplete',
      
      // Reserved words as keys
      'true=false',
      'false=true',
      'null=undefined',
      'undefined=null',
      
      // Numeric keys
      '123=value',
      '0xFF=hex',
      '3.14=pi',
      '1e10=scientific',
    ];
    
    const content = cases.join('\n');
    fs.writeFileSync(path.join(this.outputDir, 'parser-breakers.env'), content);
    return cases.length;
  }
  
  // Generate all test files
  generateAll() {
    console.log('Generating edge case test files...\n');
    
    const counts = {
      empty: this.generateEmptyValues(),
      whitespace: this.generateWhitespaceVariations(),
      special: this.generateSpecialCharacters(),
      long: this.generateLongValues(),
      breakers: this.generateParserBreakers(),
    };
    
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    
    console.log('Generated files:');
    console.log(`  ✅ empty-values.env (${counts.empty} cases)`);
    console.log(`  ✅ whitespace.env (${counts.whitespace} cases)`);
    console.log(`  ✅ special-chars.env (${counts.special} cases)`);
    console.log(`  ✅ long-values.env (${counts.long} cases)`);
    console.log(`  ✅ parser-breakers.env (${counts.breakers} cases)`);
    console.log(`\nTotal: ${total} edge cases in ${Object.keys(counts).length} files`);
    console.log(`\nFiles saved to: ${this.outputDir}/`);
  }
}

// Run if called directly
if (require.main === module) {
  const generator = new EdgeCaseGenerator();
  generator.generateAll();
}

module.exports = EdgeCaseGenerator;
```

Add to justfile:
```just
# Generate edge case test files
generate-edge-cases:
    cd tree-sitter-dotenv && node test/generators/edge-case-generator.js

# Test edge cases
test-edge-cases: generate-edge-cases
    cd tree-sitter-dotenv && for f in test/edge-cases/*.env; do \
        echo "Testing $$f..."; \
        npx tree-sitter parse "$$f" > /dev/null && echo "✅ $$f" || echo "❌ $$f"; \
    done
```

## 5.2 Performance Optimization

**MCP TOOLS REQUIRED**: 
- Use `mcp__tree_sitter__analyze_complexity` BEFORE writing benchmark scripts
- Use `mcp__tree_sitter__get_symbols` to identify performance-critical patterns
- Use `mcp__tree_sitter__find_text` to locate complex regex patterns

### Optimization steps:
1. **Profile current parser**
   Create `test/benchmarks/performance-benchmark.js`:
   ```javascript
   #!/usr/bin/env node
   const fs = require('fs');
   const path = require('path');
   const Parser = require('tree-sitter');
   const EnvGrammar = require('../../');
   
   class PerformanceBenchmark {
     constructor() {
       this.parser = new Parser();
       this.parser.setLanguage(EnvGrammar);
       this.results = [];
     }
     
     // Generate test file with specified number of lines
     generateTestFile(lines, complexity = 'mixed') {
       const testDir = path.join(__dirname, 'test-files');
       if (!fs.existsSync(testDir)) {
         fs.mkdirSync(testDir, { recursive: true });
       }
       
       const filename = `test-${lines}-lines-${complexity}.env`;
       const filepath = path.join(testDir, filename);
       
       const generators = {
         simple: (i) => `SIMPLE_VAR_${i}=value${i}`,
         strings: (i) => {
           const types = [
             `STRING_DOUBLE_${i}="double quoted value ${i}"`,
             `STRING_SINGLE_${i}='single quoted value ${i}'`,
             `STRING_INTERPOLATION_${i}="value with ${i} interpolation"`,
           ];
           return types[i % types.length];
         },
         complex: (i) => {
           const types = [
             `URL_${i}=https://example.com/path/to/resource?param=${i}`,
             `DB_URL_${i}=postgresql://user:pass@localhost:5432/db${i}`,
             `BOOL_${i}=${i % 2 === 0 ? 'true' : 'false'}`,
             `INT_${i}=${i * 100}`,
             `PATH_${i}=/very/long/path/to/some/file/system/location/${i}/file.txt`,
           ];
           return types[i % types.length];
         },
         mixed: (i) => {
           const allTypes = [
             `SIMPLE_${i}=value${i}`,
             `STRING_${i}="quoted value ${i}"`,
             `URL_${i}=https://api.example.com/v${i}`,
             `BOOL_${i}=${i % 2 === 0 ? 'true' : 'false'}`,
             `INT_${i}=${i}`,
             `EMPTY_${i}=`,
             `COMMENT_${i}=value # with comment`,
             `SPACED_${i} = value with spaces`,
           ];
           return allTypes[i % allTypes.length];
         },
         worst: (i) => {
           // Worst case: very long lines with complex patterns
           const longValue = 'x'.repeat(200) + `_${i}_` + 'y'.repeat(200);
           return `LONG_VAR_${i}=${longValue}`;
         }
       };
       
       const lines_array = [];
       const generator = generators[complexity] || generators.mixed;
       
       for (let i = 0; i < lines; i++) {
         lines_array.push(generator(i));
         // Add some comments and empty lines for realism
         if (i % 10 === 0) {
           lines_array.push('# Comment line');
         }
         if (i % 20 === 0) {
           lines_array.push('');
         }
       }
       
       const content = lines_array.join('\n');
       fs.writeFileSync(filepath, content);
       
       return { filepath, content, actualLines: lines_array.length };
     }
     
     // Benchmark parsing performance
     benchmarkParse(filepath, content, runs = 10) {
       const times = [];
       const memorySamples = [];
       
       // Warm up
       for (let i = 0; i < 3; i++) {
         this.parser.parse(content);
       }
       
       // Actual benchmark
       for (let i = 0; i < runs; i++) {
         if (global.gc) global.gc(); // Force GC if available
         
         const memBefore = process.memoryUsage();
         const start = process.hrtime.bigint();
         
         const tree = this.parser.parse(content);
         
         const end = process.hrtime.bigint();
         const memAfter = process.memoryUsage();
         
         times.push(Number(end - start) / 1_000_000); // Convert to ms
         memorySamples.push({
           heapUsed: (memAfter.heapUsed - memBefore.heapUsed) / 1024 / 1024, // MB
           external: (memAfter.external - memBefore.external) / 1024 / 1024,
         });
         
         // Verify parse was successful
         if (tree.rootNode.hasError) {
           console.warn('⚠️  Parse tree has errors');
         }
       }
       
       // Calculate statistics
       times.sort((a, b) => a - b);
       const avg = times.reduce((a, b) => a + b, 0) / times.length;
       const median = times[Math.floor(times.length / 2)];
       const min = times[0];
       const max = times[times.length - 1];
       const p95 = times[Math.floor(times.length * 0.95)];
       
       const avgMemory = memorySamples.reduce((a, b) => a + b.heapUsed, 0) / memorySamples.length;
       
       return {
         times: { avg, median, min, max, p95 },
         memory: { avgHeapMB: avgMemory },
         runs
       };
     }
     
     // Run full benchmark suite
     async runBenchmarks() {
       console.log('Tree-sitter Parser Performance Benchmark');
       console.log('=====================================\n');
       
       const testCases = [
         { lines: 10, complexity: 'simple' },
         { lines: 100, complexity: 'simple' },
         { lines: 100, complexity: 'mixed' },
         { lines: 1000, complexity: 'simple' },
         { lines: 1000, complexity: 'mixed' },
         { lines: 1000, complexity: 'complex' },
         { lines: 10000, complexity: 'simple' },
         { lines: 10000, complexity: 'mixed' },
         { lines: 1000, complexity: 'worst' },
       ];
       
       for (const testCase of testCases) {
         console.log(`Testing ${testCase.lines} lines (${testCase.complexity})...`);
         
         const { filepath, content, actualLines } = this.generateTestFile(
           testCase.lines,
           testCase.complexity
         );
         
         const results = this.benchmarkParse(filepath, content);
         
         console.log(`  File: ${path.basename(filepath)}`);
         console.log(`  Actual lines: ${actualLines}`);
         console.log(`  File size: ${(content.length / 1024).toFixed(2)} KB`);
         console.log(`  Parse times (ms):`);
         console.log(`    Average: ${results.times.avg.toFixed(2)}`);
         console.log(`    Median: ${results.times.median.toFixed(2)}`);
         console.log(`    Min: ${results.times.min.toFixed(2)}`);
         console.log(`    Max: ${results.times.max.toFixed(2)}`);
         console.log(`    95th percentile: ${results.times.p95.toFixed(2)}`);
         console.log(`  Memory usage:`);
         console.log(`    Avg heap: ${results.memory.avgHeapMB.toFixed(2)} MB`);
         
         // Check against performance targets
         const target = testCase.lines <= 1000 ? 100 : testCase.lines * 0.1;
         const status = results.times.avg <= target ? '✅' : '❌';
         console.log(`  ${status} Target: < ${target}ms\n`);
         
         this.results.push({
           ...testCase,
           actualLines,
           fileSizeKB: content.length / 1024,
           ...results
         });
       }
       
       // Summary
       console.log('\nPerformance Summary');
       console.log('==================');
       const critical = this.results.filter(r => r.lines === 1000 && r.complexity === 'mixed')[0];
       if (critical) {
         console.log(`\n🎯 Key Metric: 1000-line mixed file`);
         console.log(`   Parse time: ${critical.times.avg.toFixed(2)}ms`);
         console.log(`   Target: < 100ms`);
         console.log(`   Status: ${critical.times.avg <= 100 ? '✅ PASS' : '❌ FAIL'}`);
       }
       
       // Save detailed results
       const reportPath = path.join(__dirname, 'performance-report.json');
       fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
       console.log(`\nDetailed report saved to: ${reportPath}`);
     }
   }
   
   // Run benchmarks
   if (require.main === module) {
     const benchmark = new PerformanceBenchmark();
     benchmark.runBenchmarks().catch(console.error);
   }
   
   module.exports = PerformanceBenchmark;
   ```
   
   Add to justfile:
   ```just
   # Run performance benchmarks
   benchmark-performance:
       cd tree-sitter-dotenv && node --expose-gc test/benchmarks/performance-benchmark.js
   
   # Quick performance check
   perf-check:
       @echo "Quick performance check (1000 lines)..."
       @cd tree-sitter-dotenv && \
       echo "Generating test file..." && \
       for i in {1..1000}; do echo "VAR_$$i=value$$i"; done > perf-test.env && \
       echo "Parsing..." && \
       time npx tree-sitter parse perf-test.env > /dev/null && \
       rm perf-test.env
   ```

2. **Optimize regex patterns**
   - Avoid backtracking
   - Use possessive quantifiers where possible
   - Simplify complex patterns

3. **Measure improvements**
   - Parse time for large files
   - Memory usage
   - Incremental parse performance

### Success Criteria:
- [ ] 1000-line file parses in < 100ms
- [ ] Memory usage reasonable
- [ ] No catastrophic backtracking

## 5.3 Comprehensive Testing

**MCP TOOLS REQUIRED**:
- Use `mcp__tree_sitter__list_files` to enumerate test files
- Use `mcp__tree_sitter__get_file` to read test content
- Use `mcp__tree_sitter__run_query` to validate parsing results
- Use `mcp__tree_sitter__find_usage` to ensure complete test coverage

### Real-world file testing:
1. **Collect real configs from popular projects**
   Create `test/collectors/github-config-collector.js`:
   ```javascript
   #!/usr/bin/env node
   const fs = require('fs');
   const path = require('path');
   const https = require('https');
   const { execSync } = require('child_process');
   
   class GitHubConfigCollector {
     constructor(outputDir = 'test/real-world-configs') {
       this.outputDir = outputDir;
       this.githubToken = process.env.GITHUB_TOKEN; // Optional, for rate limiting
       
       if (!fs.existsSync(outputDir)) {
         fs.mkdirSync(outputDir, { recursive: true });
       }
     }
     
     // Popular repositories with various config files
     getTargetRepos() {
       return [
         // JavaScript/Node.js projects
         { owner: 'facebook', repo: 'react', files: ['.npmrc', '.env.example'] },
         { owner: 'nodejs', repo: 'node', files: ['.npmrc'] },
         { owner: 'vercel', repo: 'next.js', files: ['.npmrc', '.env.example'] },
         { owner: 'expressjs', repo: 'express', files: ['.npmrc'] },
         { owner: 'webpack', repo: 'webpack', files: ['.npmrc'] },
         { owner: 'vuejs', repo: 'vue', files: ['.npmrc'] },
         { owner: 'angular', repo: 'angular', files: ['.npmrc'] },
         { owner: 'gatsbyjs', repo: 'gatsby', files: ['.npmrc', '.env.example'] },
         
         // Full-stack applications
         { owner: 'gothinkster', repo: 'realworld', files: ['.env.example'] },
         { owner: 'withastro', repo: 'astro', files: ['.npmrc', '.env.example'] },
         
         // Ruby projects (for .gemrc)
         { owner: 'rails', repo: 'rails', files: ['.gemrc'] },
         { owner: 'ruby', repo: 'ruby', files: ['.gemrc'] },
         
         // Java projects (for .properties)
         { owner: 'spring-projects', repo: 'spring-boot', files: ['application.properties'] },
         { owner: 'apache', repo: 'kafka', files: ['server.properties'] },
         
         // Python projects
         { owner: 'django', repo: 'django', files: ['.env.example'] },
         { owner: 'pallets', repo: 'flask', files: ['.env.example'] },
         
         // DevOps/Infrastructure
         { owner: 'docker', repo: 'compose', files: ['.env.example'] },
         { owner: 'kubernetes', repo: 'kubernetes', files: ['.env.example'] },
         { owner: 'hashicorp', repo: 'terraform', files: ['.env.example'] },
       ];
     }
     
     // Download file from GitHub
     async downloadFile(owner, repo, filepath, branch = 'main') {
       const url = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${filepath}`;
       const outputName = `${owner}-${repo}-${filepath.replace(/\//g, '-')}`;
       const outputPath = path.join(this.outputDir, outputName);
       
       return new Promise((resolve, reject) => {
         const file = fs.createWriteStream(outputPath);
         
         https.get(url, (response) => {
           if (response.statusCode === 404) {
             // Try master branch if main doesn't exist
             if (branch === 'main') {
               file.close();
               fs.unlinkSync(outputPath);
               return this.downloadFile(owner, repo, filepath, 'master')
                 .then(resolve)
                 .catch(reject);
             }
             file.close();
             fs.unlinkSync(outputPath);
             resolve({ status: 'not_found', owner, repo, filepath });
             return;
           }
           
           if (response.statusCode !== 200) {
             file.close();
             fs.unlinkSync(outputPath);
             resolve({ status: 'error', code: response.statusCode, owner, repo, filepath });
             return;
           }
           
           response.pipe(file);
           
           file.on('finish', () => {
             file.close();
             const stats = fs.statSync(outputPath);
             resolve({
               status: 'success',
               owner,
               repo,
               filepath,
               outputPath,
               size: stats.size
             });
           });
         }).on('error', (err) => {
           fs.unlinkSync(outputPath);
           reject(err);
         });
       });
     }
     
     // Search for config files using GitHub API (requires token)
     async searchConfigFiles(fileType, limit = 10) {
       if (!this.githubToken) {
         console.warn('⚠️  No GITHUB_TOKEN set, using direct downloads only');
         return [];
       }
       
       const searchQuery = `filename:${fileType} size:>10`;
       const url = `https://api.github.com/search/code?q=${encodeURIComponent(searchQuery)}&per_page=${limit}`;
       
       const options = {
         headers: {
           'User-Agent': 'tree-sitter-config-collector',
           'Authorization': `token ${this.githubToken}`,
           'Accept': 'application/vnd.github.v3+json'
         }
       };
       
       // Implementation would use GitHub API
       // Simplified for this example
       return [];
     }
     
     // Collect sample config files
     async collectConfigs() {
       console.log('Collecting real-world config files from GitHub...\n');
       
       const repos = this.getTargetRepos();
       const results = {
         success: [],
         notFound: [],
         errors: []
       };
       
       for (const { owner, repo, files } of repos) {
         for (const file of files) {
           console.log(`Downloading ${owner}/${repo}/${file}...`);
           try {
             const result = await this.downloadFile(owner, repo, file);
             
             if (result.status === 'success') {
               console.log(`  ✅ Saved to ${path.basename(result.outputPath)} (${result.size} bytes)`);
               results.success.push(result);
             } else if (result.status === 'not_found') {
               console.log(`  ⚠️  File not found`);
               results.notFound.push(result);
             } else {
               console.log(`  ❌ Error: ${result.code}`);
               results.errors.push(result);
             }
           } catch (error) {
             console.log(`  ❌ Error: ${error.message}`);
             results.errors.push({ owner, repo, filepath: file, error: error.message });
           }
         }
       }
       
       // Also collect some .gitconfig and .ini files
       const additionalFiles = [
         {
           url: 'https://raw.githubusercontent.com/git/git/master/Documentation/config.txt',
           name: 'git-config-example.gitconfig'
         },
         {
           url: 'https://raw.githubusercontent.com/python/cpython/main/Lib/test/cfgparser.1',
           name: 'python-test.ini'
         }
       ];
       
       console.log('\nDownloading additional config examples...');
       for (const { url, name } of additionalFiles) {
         console.log(`Downloading ${name}...`);
         // Download implementation here
       }
       
       // Summary
       console.log('\n=== Collection Summary ===');
       console.log(`✅ Successfully downloaded: ${results.success.length} files`);
       console.log(`⚠️  Not found: ${results.notFound.length} files`);
       console.log(`❌ Errors: ${results.errors.length} files`);
       console.log(`\nFiles saved to: ${this.outputDir}/`);
       
       // Save manifest
       const manifest = {
         timestamp: new Date().toISOString(),
         stats: {
           success: results.success.length,
           notFound: results.notFound.length,
           errors: results.errors.length
         },
         files: results.success.map(r => ({
           source: `${r.owner}/${r.repo}/${r.filepath}`,
           local: path.basename(r.outputPath),
           size: r.size
         }))
       };
       
       fs.writeFileSync(
         path.join(this.outputDir, 'manifest.json'),
         JSON.stringify(manifest, null, 2)
       );
       
       return results;
     }
     
     // Clean up old downloads
     cleanup() {
       const files = fs.readdirSync(this.outputDir);
       for (const file of files) {
         if (file !== 'manifest.json') {
           fs.unlinkSync(path.join(this.outputDir, file));
         }
       }
       console.log(`Cleaned up ${files.length - 1} files`);
     }
   }
   
   // CLI usage
   if (require.main === module) {
     const collector = new GitHubConfigCollector();
     
     const command = process.argv[2];
     if (command === 'clean') {
       collector.cleanup();
     } else {
       collector.collectConfigs().catch(console.error);
     }
   }
   
   module.exports = GitHubConfigCollector;
   ```
   
   Add to justfile:
   ```just
   # Download real config files from GitHub
   collect-real-configs:
       cd tree-sitter-dotenv && node test/collectors/github-config-collector.js
   
   # Clean downloaded config files
   clean-real-configs:
       cd tree-sitter-dotenv && node test/collectors/github-config-collector.js clean
   ```

2. **Test against each**
   - Parse successfully
   - No errors for valid syntax
   - Appropriate errors for invalid syntax

3. **Create regression test suite**
   Create `test/validators/real-world-validator.js`:
   ```javascript
   #!/usr/bin/env node
   const fs = require('fs');
   const path = require('path');
   const Parser = require('tree-sitter');
   const EnvGrammar = require('../../');
   
   class RealWorldValidator {
     constructor(configDir = 'test/real-world-configs') {
       this.configDir = configDir;
       this.parser = new Parser();
       this.parser.setLanguage(EnvGrammar);
       this.results = {
         passed: [],
         failed: [],
         errors: []
       };
     }
     
     // Load manifest of downloaded files
     loadManifest() {
       const manifestPath = path.join(this.configDir, 'manifest.json');
       if (!fs.existsSync(manifestPath)) {
         throw new Error('No manifest found. Run collect-real-configs first.');
       }
       return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
     }
     
     // Validate a single file
     validateFile(filepath) {
       const content = fs.readFileSync(filepath, 'utf8');
       const filename = path.basename(filepath);
       
       try {
         const tree = this.parser.parse(content);
         const hasError = tree.rootNode.hasError;
         
         // Collect detailed error information
         const errors = [];
         this.collectErrors(tree.rootNode, errors);
         
         // Analyze parse result
         const stats = {
           filename,
           lines: content.split('\n').length,
           size: content.length,
           hasError,
           errorCount: errors.length,
           errors: errors.slice(0, 5), // First 5 errors
           nodeTypes: this.collectNodeTypes(tree.rootNode),
           parseTime: 0 // Will be measured separately
         };
         
         // Measure parse time
         const start = process.hrtime.bigint();
         for (let i = 0; i < 10; i++) {
           this.parser.parse(content);
         }
         const end = process.hrtime.bigint();
         stats.parseTime = Number(end - start) / 10_000_000; // Average ms
         
         // Determine pass/fail based on criteria
         const passed = this.evaluateFile(stats, content);
         
         if (passed) {
           this.results.passed.push(stats);
         } else {
           this.results.failed.push(stats);
         }
         
         return stats;
       } catch (error) {
         const errorInfo = {
           filename,
           error: error.message,
           stack: error.stack
         };
         this.results.errors.push(errorInfo);
         return errorInfo;
       }
     }
     
     // Collect all error nodes
     collectErrors(node, errors) {
       if (node.type === 'ERROR' || node.type.startsWith('error')) {
         errors.push({
           type: node.type,
           start: node.startPosition,
           end: node.endPosition,
           text: node.text.substring(0, 50)
         });
       }
       
       for (let i = 0; i < node.childCount; i++) {
         this.collectErrors(node.child(i), errors);
       }
     }
     
     // Collect node type statistics
     collectNodeTypes(node, types = {}) {
       types[node.type] = (types[node.type] || 0) + 1;
       
       for (let i = 0; i < node.childCount; i++) {
         this.collectNodeTypes(node.child(i), types);
       }
       
       return types;
     }
     
     // Evaluate if file passed validation
     evaluateFile(stats, content) {
       // Special handling for known patterns
       const filename = stats.filename.toLowerCase();
       
       // .npmrc files may have special syntax
       if (filename.endsWith('.npmrc')) {
         // Allow some npmrc-specific patterns
         const npmrcPatterns = [
           /^\/\/.*\/:_authToken=/m,  // Registry auth tokens
           /^@.*:registry=/m,          // Scoped registries
           /^[a-z-]+=\d+$/m,          // Numeric configs
         ];
         
         // If it has npmrc patterns and minimal errors, pass
         const hasNpmrcPattern = npmrcPatterns.some(p => p.test(content));
         if (hasNpmrcPattern && stats.errorCount < 3) {
           return true;
         }
       }
       
       // General criteria
       if (stats.hasError) {
         // Allow files with minor errors (comments as keys, etc)
         const errorRate = stats.errorCount / stats.lines;
         return errorRate < 0.1; // Less than 10% error rate
       }
       
       return true;
     }
     
     // Run validation on all files
     async validateAll() {
       console.log('Real-World Configuration File Validation');
       console.log('======================================\n');
       
       const manifest = this.loadManifest();
       console.log(`Found ${manifest.files.length} files to validate\n`);
       
       // Group files by type
       const filesByType = {};
       for (const file of manifest.files) {
         const ext = path.extname(file.local) || '.env';
         if (!filesByType[ext]) filesByType[ext] = [];
         filesByType[ext].push(file);
       }
       
       // Validate each type
       for (const [ext, files] of Object.entries(filesByType)) {
         console.log(`\nValidating ${ext} files (${files.length} files):`);
         console.log('-'.repeat(50));
         
         for (const file of files) {
           const filepath = path.join(this.configDir, file.local);
           process.stdout.write(`  ${file.local.padEnd(40)}`);
           
           const result = this.validateFile(filepath);
           
           if (result.error) {
             console.log('❌ ERROR');
           } else if (this.results.passed.includes(result)) {
             console.log(`✅ PASS (${result.parseTime.toFixed(2)}ms)`);
           } else {
             console.log(`⚠️  FAIL (${result.errorCount} errors)`);
             if (result.errors.length > 0) {
               console.log(`     First error: ${result.errors[0].type} at ${result.errors[0].start.row}:${result.errors[0].start.column}`);
             }
           }
         }
       }
       
       // Generate report
       this.generateReport();
     }
     
     // Generate detailed report
     generateReport() {
       const total = this.results.passed.length + this.results.failed.length + this.results.errors.length;
       const passRate = (this.results.passed.length / total * 100).toFixed(1);
       
       console.log('\n' + '='.repeat(60));
       console.log('VALIDATION SUMMARY');
       console.log('='.repeat(60));
       console.log(`Total files tested: ${total}`);
       console.log(`✅ Passed: ${this.results.passed.length} (${passRate}%)`);
       console.log(`⚠️  Failed: ${this.results.failed.length}`);
       console.log(`❌ Errors: ${this.results.errors.length}`);
       
       // Performance stats
       if (this.results.passed.length > 0) {
         const avgParseTime = this.results.passed
           .reduce((sum, r) => sum + r.parseTime, 0) / this.results.passed.length;
         console.log(`\nAverage parse time: ${avgParseTime.toFixed(2)}ms`);
       }
       
       // Common node types
       const allNodeTypes = {};
       [...this.results.passed, ...this.results.failed].forEach(r => {
         if (r.nodeTypes) {
           Object.entries(r.nodeTypes).forEach(([type, count]) => {
             allNodeTypes[type] = (allNodeTypes[type] || 0) + count;
           });
         }
       });
       
       console.log('\nMost common node types:');
       Object.entries(allNodeTypes)
         .sort(([,a], [,b]) => b - a)
         .slice(0, 10)
         .forEach(([type, count]) => {
           console.log(`  ${type}: ${count}`);
         });
       
       // Failed file analysis
       if (this.results.failed.length > 0) {
         console.log('\nFailed files analysis:');
         const byErrorCount = this.results.failed
           .sort((a, b) => b.errorCount - a.errorCount)
           .slice(0, 5);
         
         byErrorCount.forEach(f => {
           console.log(`  ${f.filename}: ${f.errorCount} errors`);
         });
       }
       
       // Save detailed report
       const report = {
         timestamp: new Date().toISOString(),
         summary: {
           total,
           passed: this.results.passed.length,
           failed: this.results.failed.length,
           errors: this.results.errors.length,
           passRate
         },
         results: this.results
       };
       
       const reportPath = path.join(this.configDir, 'validation-report.json');
       fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
       console.log(`\nDetailed report saved to: ${reportPath}`);
       
       // Exit code based on pass rate
       const exitCode = passRate >= 95 ? 0 : 1;
       console.log(`\nOverall result: ${exitCode === 0 ? '✅ PASS' : '❌ FAIL'} (target: 95% pass rate)`);
       process.exit(exitCode);
     }
   }
   
   // CLI usage
   if (require.main === module) {
     const validator = new RealWorldValidator();
     validator.validateAll().catch(console.error);
   }
   
   module.exports = RealWorldValidator;
   ```
   
   Add to justfile:
   ```just
   # Validate parser against real-world configs
   validate-real-world: collect-real-configs
       cd tree-sitter-dotenv && node test/validators/real-world-validator.js
   
   # Full real-world test suite
   test-real-world: collect-real-configs validate-real-world
   ```

### Success Criteria:
- [ ] 95%+ real files parse correctly
- [ ] Known edge cases handled
- [ ] Performance acceptable

**Checkpoint 5.0 Review Requirements**:
**CRITICAL**: Before marking ANY task complete, you MUST demonstrate use of relevant MCP tools. Tasks completed without MCP tool usage (where applicable) are considered INCOMPLETE.
- [ ] All edge cases handled gracefully: tests pass
- [ ] Performance acceptable: < 100ms for 1000 lines
- [ ] Real-world files parse correctly: validation passed
- [ ] Feature complete: all value types working
- [ ] **ZED EXTENSION VERIFICATION (MANDATORY)**:
  - [ ] extension.toml commit hash is EXACTLY 40 characters
  - [ ] Hash matches latest pushed commit: `git log -1 --format="%H"`
  - [ ] Manual fetch test passed: `git fetch origin <hash> --depth 1`
  - [ ] Extension installed without errors
  - [ ] Edge case test file shows correct error recovery
  - [ ] Performance acceptable in Zed with large files
- [ ] **FAILURE = CHECKPOINT NOT PASSED**

**MANDATORY EXTERNAL REVIEW BEFORE PROCEEDING**