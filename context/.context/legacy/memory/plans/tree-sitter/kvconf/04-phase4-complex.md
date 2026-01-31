# Phase 4: Complex Types (Checkpoint 4.0)

## User's Zed Theme Color Map
- **Orange**: booleans, integers
- **Green**: strings
- **White**: raw_values
- **Grey**: comments
- **Cyan**: operators
- **Red**: errors/keys (variable names)

## Table of Contents
- [4.1 URI Values (includes URLs)](#41-uri-values-includes-urls)
- [4.2 Unquoted Strings](#42-unquoted-strings)
- [4.3 Error Nodes](#43-error-nodes)

**REMINDER: Do not start Phase 4 until Checkpoint 3.0 is approved**

## MCP Tool Integration

### Use tree-sitter MCP for:
1. **URI Pattern Analysis**:
   ```bash
   # Search for existing URI/URL patterns in codebase
   mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="uri|url|https?://" file_pattern="**/*.{js,env}"
   
   # Find similar URI parsing implementations
   mcp__tree_sitter__find_similar_code project="tree-sitter-dotenv" snippet="seq('http', optional('s'), '://')" language="javascript"
   ```

2. **Grammar Complexity Monitoring**:
   ```bash
   # Monitor complexity as URI rules are added
   mcp__tree_sitter__analyze_complexity project="tree-sitter-dotenv" file_path="grammar.js"
   
   # Compare before/after AST structure
   mcp__tree_sitter__get_ast project="tree-sitter-dotenv" path="grammar.js" max_depth=2
   ```

3. **Test Coverage Analysis**:
   ```bash
   # Find test files with URI examples
   mcp__tree_sitter__list_files project="tree-sitter-dotenv" pattern="test/**/*.env" | while read file; do
     mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="https?://" file_pattern="$file"
   done
   ```

4. **Error Pattern Detection**:
   ```bash
   # Search for error handling patterns
   mcp__tree_sitter__run_query project="tree-sitter-dotenv" query="(ERROR) @error" language="javascript"
   ```

## Critical Zed Integration Steps

### Mandatory Workflow for Each Grammar Change:
1. **Implement and Test Locally**:
   ```bash
   # Make grammar changes
   npx tree-sitter generate
   npx tree-sitter test
   ```

2. **Update Highlighting Rules**:
   - Add to queries/highlights.scm:
     ```scheme
     (uri) @string.special.url
     (uri_scheme) @keyword
     (uri_host) @string.special.hostname
     (uri_port) @number
     (error) @error
     (error_multiple_values) @error
     ```

3. **Commit and Push Changes**:
   ```bash
   git add -A
   git commit -m "feat(phase4): Add URI parsing support"
   git push origin feature/typed-values
   git log -1 --format="%H"  # Copy this full hash
   ```

4. **Update Zed Extension (CRITICAL - VERIFY HASH)**:
   ```bash
   # Step 1: Get FULL commit hash (MUST be 40 characters)
   cd tree-sitter-dotenv
   FULL_HASH=$(git log -1 --format="%H")
   echo "Full hash: $FULL_HASH"
   echo "Hash length: ${#FULL_HASH}"  # MUST show 40
   
   # Step 2: Verify hash is on GitHub
   git ls-remote origin | grep "$FULL_HASH" || echo "ERROR: Hash not on GitHub!"
   
   # Step 3: Update extension.toml with EXACT hash
   cd ../zed-env
   # Copy the FULL hash, do NOT truncate
   sed -i '' "s/commit = \".*\"/commit = \"$FULL_HASH\"/" extension.toml
   
   # Step 4: Verify the update
   grep "commit = " extension.toml
   # MUST show exactly 40 characters between quotes
   
   # Step 5: Copy highlights.scm
   cp ../tree-sitter-dotenv/queries/highlights.scm languages/env/highlights.scm
   
   # Step 6: Test fetch before installation
   cd grammars && rm -rf test-fetch
   git init test-fetch && cd test-fetch
   git remote add origin https://github.com/aRustyDev/tree-sitter-dotenv
   git fetch origin "$FULL_HASH" --depth 1 || echo "FETCH FAILED - CHECK HASH!"
   cd .. && rm -rf test-fetch
   
   # Step 7: Install extension
   cd .. && zed --install-dev-extension .
   ```

5. **Visual Verification**:
   - Create phase4-verification.env with URI test cases
   - Open in Zed to verify highlighting
   - Screenshot any issues for debugging

### Common Phase 4 Issues:
- **Complex grammar slows parsing**: Use token() for terminal patterns
- **URI highlighting too aggressive**: Ensure proper precedence
- **Extension fails to load**: Check for syntax errors in highlights.scm

## 4.1 URI Values (includes URLs)

### URI Grammar Implementation:
Based on RFC 3986 URI syntax:

1. **URI components**
   ```javascript
   uri: ($) => seq(
     field('scheme', $.uri_scheme),
     ':',
     optional($.uri_hier_part),
     optional(seq('?', field('query', $.uri_query))),
     optional(seq('#', field('fragment', $.uri_fragment)))
   ),
   
   uri_scheme: ($) => /[a-zA-Z][a-zA-Z0-9+.-]*/,
   
   // Full URI hierarchy implementation
   uri_hier_part: ($) => choice(
     // //authority/path
     seq(
       '//',
       field('authority', $.uri_authority),
       field('path', optional($.uri_path_abempty))
     ),
     // /path (absolute path)
     field('path', $.uri_path_absolute),
     // path (rootless path)
     field('path', $.uri_path_rootless),
     // empty
     field('path', $.uri_path_empty)
   ),
   
   uri_authority: ($) => seq(
     optional(seq(field('userinfo', $.uri_userinfo), '@')),
     field('host', $.uri_host),
     optional(seq(':', field('port', $.uri_port)))
   ),
   
   uri_userinfo: ($) => /[a-zA-Z0-9._~!$&'()*+,;=:-]*/,
   
   uri_host: ($) => choice(
     $.ip_literal,
     $.ipv4_address,
     $.reg_name
   ),
   
   ip_literal: ($) => seq('[', choice($.ipv6_address, $.ipvfuture), ']'),
   
   ipv6_address: ($) => /[0-9a-fA-F:]+/,  // Simplified
   
   ipvfuture: ($) => seq('v', /[0-9a-fA-F]+/, '.', /[a-zA-Z0-9._~!$&'()*+,;=:-]+/),
   
   ipv4_address: ($) => /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,
   
   reg_name: ($) => /[a-zA-Z0-9._~!$&'()*+,;=-]*/,
   
   uri_port: ($) => /\d+/,
   
   uri_path_abempty: ($) => repeat(seq('/', $.uri_segment)),
   
   uri_path_absolute: ($) => seq('/', optional(seq($.uri_segment_nz, repeat(seq('/', $.uri_segment))))),
   
   uri_path_rootless: ($) => seq($.uri_segment_nz, repeat(seq('/', $.uri_segment))),
   
   uri_path_empty: ($) => '',
   
   uri_segment: ($) => /[a-zA-Z0-9._~!$&'()*+,;=:@-]*/,
   
   uri_segment_nz: ($) => /[a-zA-Z0-9._~!$&'()*+,;=:@-]+/,
   
   uri_query: ($) => /[a-zA-Z0-9._~!$&'()*+,;=:@/?-]*/,
   
   uri_fragment: ($) => /[a-zA-Z0-9._~!$&'()*+,;=:@/?-]*/,
   
   // Common schemes to support:
   // - http, https (web)
   // - ftp, ftps (file transfer)
   // - mailto (email)
   // - file (local files)
   // - data (data URLs)
   // - jdbc, mysql, postgresql (databases)
   // - git, ssh (version control)
   ```

2. **Simplified URL for common case**
   ```javascript
   url: ($) => token(seq(
     /https?:\/\//,
     /[a-zA-Z0-9.-]+/,
     optional(seq(':', /\d+/)),
     optional(/\/[^\s#]*/),
     optional(seq('#', /[^\s]*/))
   )),
   ```

### Test Cases:
- `key=https://example.com` → url
- `key=https://api.example.com/v1/users?page=1&limit=10#section` → url
- `key=ftp://files.example.com/path/to/file` → uri
- `key=mailto:user@example.com` → uri
- `key=jdbc:mysql://localhost:3306/database` → uri
- `key=file:///home/user/document.pdf` → uri
- `key=data:text/plain;base64,SGVsbG8gV29ybGQ=` → uri

### Success Criteria:
- [ ] Common URLs parse with url node
- [ ] Full URIs parse with scheme detection
- [ ] Query parameters captured
- [ ] Fragments captured
- [ ] Database URLs work

### URI Validation Helper
Create `test/helpers/uri-validator.js`:
```javascript
#!/usr/bin/env node
const Parser = require('tree-sitter');
const EnvGrammar = require('../../');

class UriValidator {
  constructor() {
    this.parser = new Parser();
    this.parser.setLanguage(EnvGrammar);
  }
  
  validateUri(uriString) {
    const input = `test=${uriString}`;
    const tree = this.parser.parse(input);
    const value = tree.rootNode.child(0)?.namedChild(1);
    
    if (!value) {
      return { valid: false, error: 'No value parsed' };
    }
    
    const isUri = value.type === 'uri' || value.type === 'url';
    const result = {
      valid: isUri,
      type: value.type,
      scheme: null,
      authority: null,
      path: null,
      query: null,
      fragment: null
    };
    
    if (isUri && value.type === 'uri') {
      // Extract URI components
      for (const child of value.namedChildren) {
        const fieldName = child.fieldName;
        if (fieldName) {
          result[fieldName] = child.text;
        }
      }
    }
    
    return result;
  }
  
  testCommonUris() {
    const testCases = [
      'https://example.com',
      'http://api.example.com:8080/v1/users?page=1',
      'ftp://files.example.com/path/to/file.txt',
      'mailto:user@example.com',
      'file:///home/user/document.pdf',
      'jdbc:mysql://localhost:3306/database',
      'postgresql://user:pass@host/db',
      'git+ssh://git@github.com/user/repo.git',
      'data:text/plain;base64,SGVsbG8=',
      'tel:+1-234-567-8900',
      'urn:isbn:0451450523',
      'redis://localhost:6379/0',
      'mongodb://localhost:27017/mydb',
      'ws://localhost:8080/websocket',
      'wss://secure.example.com/ws'
    ];
    
    console.log('Testing common URI patterns:\n');
    for (const uri of testCases) {
      const result = this.validateUri(uri);
      const status = result.valid ? '✅' : '❌';
      console.log(`${status} ${uri}`);
      console.log(`   Type: ${result.type}`);
      if (result.scheme) {
        console.log(`   Scheme: ${result.scheme}`);
      }
      console.log('');
    }
  }
}

// Usage
if (require.main === module) {
  const validator = new UriValidator();
  
  if (process.argv[2] === 'test') {
    validator.testCommonUris();
  } else if (process.argv[2]) {
    const result = validator.validateUri(process.argv[2]);
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node uri-validator.js test              # Test common URIs');
    console.log('  node uri-validator.js "uri-to-test"     # Validate specific URI');
  }
}

module.exports = UriValidator;
```

Add to justfile:
```just
# Validate URI parsing
validate-uri URI:
    cd tree-sitter-dotenv && node test/helpers/uri-validator.js "{{URI}}"

# Test common URI patterns
test-uris:
    cd tree-sitter-dotenv && node test/helpers/uri-validator.js test
```

### Additional URI Schemes Research

Based on common configuration file usage patterns, here are the URI schemes that should be supported:

#### 1. **Web Protocols** (Most Common)
- `http://` - Standard web protocol
- `https://` - Secure web protocol
- `ws://` - WebSocket protocol
- `wss://` - Secure WebSocket protocol

#### 2. **Database Connection URIs**
- `postgresql://` or `postgres://` - PostgreSQL databases
- `mysql://` - MySQL databases
- `mongodb://` - MongoDB databases
- `redis://` - Redis connections
- `jdbc:mysql://` - JDBC MySQL connections
- `jdbc:postgresql://` - JDBC PostgreSQL connections
- `jdbc:oracle:thin:` - JDBC Oracle connections
- `sqlite://` or `sqlite3://` - SQLite databases

#### 3. **Version Control**
- `git://` - Git protocol
- `git+ssh://` - Git over SSH
- `git+https://` - Git over HTTPS
- `ssh://` - SSH protocol
- `svn://` - Subversion

#### 4. **File Transfer**
- `ftp://` - File Transfer Protocol
- `ftps://` - FTP over SSL/TLS
- `sftp://` - SSH File Transfer Protocol
- `file://` - Local file system

#### 5. **Messaging and Communication**
- `amqp://` - Advanced Message Queuing Protocol
- `amqps://` - AMQP over TLS
- `mqtt://` - Message Queuing Telemetry Transport
- `kafka://` - Apache Kafka (non-standard but common)
- `nats://` - NATS messaging

#### 6. **Cloud Storage**
- `s3://` - Amazon S3
- `gs://` - Google Cloud Storage
- `azure://` - Azure Storage
- `hdfs://` - Hadoop Distributed File System

#### 7. **Other Common Schemes**
- `mailto:` - Email addresses
- `tel:` - Phone numbers
- `sms:` - SMS messages
- `data:` - Data URLs (inline data)
- `ldap://` - LDAP directory access
- `ldaps://` - LDAP over SSL
- `docker://` - Docker daemon
- `urn:` - Uniform Resource Names

#### 8. **Package Registries**
- `npm://` - NPM packages (non-standard)
- `gem://` - Ruby gems (non-standard)
- `pypi://` - Python packages (non-standard)

### Implementation Priority
1. **High Priority** (Phase 4): http(s), database URIs, file, git
2. **Medium Priority** (Phase 5): messaging protocols, cloud storage
3. **Low Priority** (Phase 6): package registries, specialized protocols

### Grammar Implementation Note
```javascript
// Update uri_scheme to include all supported schemes
// Consider grouping similar schemes for better organization
common_schemes: ($) => choice(
  'http', 'https', 'ws', 'wss',           // Web
  'postgresql', 'postgres', 'mysql',       // Databases
  'mongodb', 'redis', 'sqlite', 'sqlite3',
  'git', 'ssh', 'git+ssh', 'git+https',   // VCS
  'ftp', 'ftps', 'sftp', 'file',          // Files
  'amqp', 'amqps', 'mqtt', 'kafka',       // Messaging
  's3', 'gs', 'azure', 'hdfs',            // Cloud
  'mailto', 'tel', 'sms', 'data',         // Misc
  'ldap', 'ldaps', 'docker', 'urn'
),

// JDBC special case (scheme:subscheme)
jdbc_scheme: ($) => seq(
  'jdbc',
  ':',
  choice('mysql', 'postgresql', 'oracle', 'sqlite', 'h2')
),
```

## 4.2 Unquoted Strings

### Implementation:
1. **Catch-all for unquoted text**
   ```javascript
   unquoted_string: ($) => token.immediate(/[^\n\r]+/),
   ```

2. **Update precedence**
   ```javascript
   _value: ($) => choice(
     $.string_double,
     $.string_single,
     $.bool,
     $.integer,
     $.uri,  // Full URI
     $.url,  // Simple URL
     $.unquoted_string  // Catch-all
   ),
   ```

### Test Cases:
- `key=hello world` → unquoted_string
- `key=/path/to/file` → unquoted_string
- `key=some-value-here` → unquoted_string
- `key=not-a-url-just-text` → unquoted_string

## 4.3 Error Nodes

### Implementation:
1. **Specific error types**
   ```javascript
   error_trailing_comma: ($) => ',',
   error_multiple_values: ($) => /[^\n\r#]+/,
   error: ($) => /[^\n\r]+/,  // Catch-all
   ```

2. **Error recovery patterns**
   ```javascript
   // After successful value parse, check for errors
   // Example: bool followed by more content
   ```

### Test Cases:
- `key=true false` → bool + error_multiple_values("false")
- `key=value,` → unquoted_string("value") + error_trailing_comma
- `key=https://url.com extra` → url + error_multiple_values("extra")

**Checkpoint 4.0 Review Requirements**:
- [ ] All value types parsing correctly: tests pass
- [ ] Error nodes properly scoped: narrow highlighting
- [ ] Complex URLs handled properly: URI components parsed
- [ ] Precedence chain working: correct type selection
- [ ] **ZED EXTENSION VERIFICATION (MANDATORY)**:
  - [ ] extension.toml commit hash is EXACTLY 40 characters
  - [ ] Hash matches latest pushed commit: `git log -1 --format="%H"`
  - [ ] Manual fetch test passed: `git fetch origin <hash> --depth 1`
  - [ ] Extension installed without errors
  - [ ] Test file shows correct highlighting for all types
- [ ] **FAILURE = CHECKPOINT NOT PASSED**

**MANDATORY EXTERNAL REVIEW BEFORE PROCEEDING**