---
name: Data Sanitization Process
module_type: process
scope: context
priority: highest
triggers: ["sanitize", "redact", "clean output", "remove sensitive", "mask data", "before posting"]
dependencies: ["core/defaults.md", "processes/tooling/tool-selection.md"]
conflicts: []
version: 1.0.0
---

# Data Sanitization Process

## Purpose
Remove or mask sensitive information before posting to any public or semi-public location. This process ensures no credentials, PII, or system information is exposed in issues, PRs, or documentation.

## Trigger
- Before any IssueUpdate
- Before creating PRs or issues
- Before posting error messages or logs
- Before sharing debug output
- When explicitly requested

## Input
Raw text that may contain sensitive information

## Process Flow

### 1. Determine Content Type
Identify the format and complexity of input:

```yaml
content_types:
  text:
    - Plain text files
    - Log outputs
    - Error messages
    - Command outputs
  
  json:
    - Configuration files
    - API responses
    - Structured data
  
  structured_logs:
    - Application logs
    - System logs
    - Debug traces
```

Assess complexity:
- **Simple**: Single-line replacements, basic patterns
- **Medium**: Multi-line patterns, context-aware
- **Complex**: Nested structures, conditional logic

### 2. Select Sanitization Tool

Execute: Process: ToolSelection with parameters:
- tool_category: ${content_type}
- complexity: ${assessed_complexity}

Tool preference order (from core/defaults.md):
```yaml
text:
  - sed (simple)
  - awk (medium)  
  - perl (complex)
  - python (any)

json:
  - jq (any)
  - python (any)

structured_logs:
  - awk (medium)
  - python (any)
```

### 3. Apply Sanitization Patterns

#### Multi-Pass Strategy

**Pass 1: Credentials and Keys**
```bash
# API Keys and Tokens
s/(api[_-]?key|token|bearer)[\s:=]+["'`]?[\w\-]{20,}["'`]?/\1=<api-key-REDACTED>/gi

# SSH Keys
s/-----BEGIN [\w\s]+ KEY-----[\s\S]+?-----END [\w\s]+ KEY-----/<ssh-key-REDACTED>/g

# JWT Tokens
s/eyJ[\w\-]+\.eyJ[\w\-]+\.[\w\-]+/<jwt-token-REDACTED>/g

# Passwords
s/(password|passwd|pwd)[\s:="']+([^\s"']+)/\1=<password-REDACTED>/gi
```

**Pass 2: Personal Information**
```bash
# Email addresses
s/[\w\.-]+@[\w\.-]+\.\w+/<email>/g

# IP addresses (preserve common local IPs)
s/\b(?!127\.0\.0\.1|0\.0\.0\.0|localhost)(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/<ip-address>/g
s/([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}/<ipv6-address>/g

# Phone numbers
s/[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}/<phone>/g

# UUIDs
s/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/<uuid>/g
```

**Pass 3: System Information**
```bash
# User paths
s|/home/([^/]+)/|/home/<username>/|g
s|/Users/([^/]+)/|/Users/<username>/|g
s|C:\\Users\\([^\\]+)\\|C:\\Users\\<username>\\|g

# Database URLs
s|(mongodb|postgres|mysql|redis)://[^@]+@[^\s]+|\1://<credentials>@<host>|g

# Internal hostnames
s/[a-zA-Z0-9\-]+\.(local|internal|corp)/<hostname>/g
```

**Pass 4: Context-Specific**
- Session IDs
- Temporary paths
- Port numbers (when sensitive)
- Custom project patterns

### 4. Tool-Specific Implementation

#### Using sed (simple patterns)
```bash
echo "${content}" | sed -E \
  -e 's/[\w\.-]+@[\w\.-]+\.\w+/<email>/g' \
  -e 's/\b(?!127\.0\.0\.1)([0-9]{1,3}\.){3}[0-9]{1,3}\b/<ip-address>/g' \
  -e 's/(api[_-]?key)[\s:=]+["'\''`]?[\w\-]{20,}["'\''`]?/\1=<api-key-REDACTED>/gi'
```

#### Using awk (medium complexity)
```bash
echo "${content}" | awk '
/-----BEGIN .* KEY-----/ { in_key=1; print "<ssh-key-REDACTED>"; next }
/-----END .* KEY-----/ { in_key=0; next }
!in_key {
    gsub(/\/home\/[^\/]+\//, "/home/<username>/")
    gsub(/\/Users\/[^\/]+\//, "/Users/<username>/")
    gsub(/api[_-]?key[\s:=]+["\'`]?[\w\-]{20,}["\'`]?/, "api_key=<api-key-REDACTED>")
    gsub(/[\w\.-]+@[\w\.-]+\.\w+/, "<email>")
    print
}'
```

#### Using python (complex patterns)
```python
#!/usr/bin/env python3
import re
import sys

content = sys.stdin.read()

# Define sanitization patterns with priority order
patterns = [
    # Critical - Credentials
    (r'(api[_-]?key|apikey|token|bearer)[\s:="\']+([A-Za-z0-9\-_]{20,})', r'\1=<api-key-REDACTED>'),
    (r'(password|passwd|pwd)[\s:="\']+([^\s"\']+)', r'\1=<password-REDACTED>'),
    (r'-----BEGIN ([A-Z ]+) KEY-----[\s\S]+?-----END \1 KEY-----', '<ssh-key-REDACTED>'),
    (r'eyJ[\w\-]+\.eyJ[\w\-]+\.[\w\-]+', '<jwt-token-REDACTED>'),
    
    # Personal info
    (r'[\w\.-]+@[\w\.-]+\.\w+', '<email>'),
    (r'\b(?!127\.0\.0\.1|0\.0\.0\.0|localhost)(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '<ip-address>'),
    (r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', '<phone>'),
    
    # System paths
    (r'/home/([^/]+)/', '/home/<username>/'),
    (r'/Users/([^/]+)/', '/Users/<username>/'),
    (r'C:\\Users\\([^\\]+)\\', 'C:\\Users\\<username>\\'),
    
    # Identifiers
    (r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '<uuid>'),
    (r'(session[_-]?id|sid)[\s:="\']+([A-Za-z0-9]{16,})', r'\1=<session-id>'),
    
    # Database URLs
    (r'(mongodb|postgres|mysql|redis)://[^:]+:[^@]+@[^\s]+', r'\1://<credentials>@<host>'),
]

# Apply all patterns
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.MULTILINE)

# Add sanitization notice
print("# Note: This content has been sanitized for security")
print(f"# Patterns applied: {len(patterns)}")
print("# Date: $(date)")
print()
print(content)
```

#### Using jq (JSON data)
```bash
cat file.json | jq '
walk(
  if type == "object" then
    with_entries(
      if .key | test("password|secret|token|key"; "i") then
        .value = "<redacted>"
      else . end
    )
  elif type == "string" then
    gsub("(?<prefix>api[_-]?key[\"\'\\s:=]+)[^\"\'\\s]+"; "\(.prefix)<api-key-REDACTED>") |
    gsub("[\\w\\.-]+@[\\w\\.-]+\\.\\w+"; "<email>") |
    gsub("\\b(?!127\\.0\\.0\\.1)([0-9]{1,3}\\.){3}[0-9]{1,3}\\b"; "<ip-address>")
  else . end
)'
```

### 5. Validate Sanitization

After sanitization:
1. **Quick scan for missed patterns**
   - Re-run pattern detection without replacement
   - Flag any sensitive patterns still found
   
2. **Check for partial exposures**
   - Key prefixes/suffixes (e.g., `sk_live_...` should be fully redacted)
   - Encoded data (base64, hex)
   - URLs with embedded credentials
   
3. **Context preservation**
   - Error messages still meaningful?
   - Stack traces still debuggable?
   - Relationships between data preserved?

4. **Apply conservative fallback if unsure**
   ```bash
   # Any long alphanumeric string could be sensitive
   s/[A-Za-z0-9\-_]{40,}/<possible-sensitive-data-REDACTED>/g
   ```

### 6. Handle Tool Failures

If primary tool fails:
1. **Log failure reason**
   ```bash
   echo "Warning: ${tool} not available, trying ${next_tool}" >&2
   ```

2. **Try fallback chain**
   - sed → awk → perl → python
   - jq → python -m json.tool

3. **Manual fallback**
   ```bash
   echo "MANUAL SANITIZATION REQUIRED"
   echo "Please remove:"
   echo "- Email addresses"
   echo "- API keys and passwords"
   echo "- IP addresses"
   echo "- Usernames in paths"
   ```

### 7. Document Sanitization

Add metadata to sanitized content:
```
# Note: This content has been sanitized for security
# Tool used: ${tool_name}
# Patterns applied: ${pattern_count}
# Date: ${timestamp}
# 
# Sanitized items:
# - ${count} email addresses → <email>
# - ${count} API keys → <api-key-REDACTED>
# - ${count} IP addresses → <ip-address>
```

## Output
Sanitized text safe for public posting

## Integration Points
- Used by: Process: IssueUpdate
- Used by: Process: CommitWork  
- Used by: Process: SubmitWork (PRs)
- Uses: Process: ToolSelection
- References: core/defaults.md for patterns

## Common Use Cases

### Issue Creation
```bash
# Capture error with full context
error_output=$(./failing_command 2>&1)

# Sanitize before posting
sanitized=$(echo "$error_output" | python3 /path/to/sanitize.py)

# Create issue with clean content
gh issue create --title "Deployment error" --body "$sanitized"
```

### Debug Log Sharing
```bash
# Sanitize docker logs
docker logs container_name 2>&1 | \
  awk -f /path/to/sanitize.awk > \
  debug_logs_sanitized.txt
```

### CI/CD Output
```bash
# Clean build logs before artifact upload
cat build.log | \
  sed -f /path/to/sanitize.sed > \
  build_clean.log
```

## Testing Sanitization

Create test file with known patterns:
```bash
cat > test_sensitive.txt << 'EOF'
API_KEY=sk_test_abcd1234efgh5678ijkl9012mnop
Email: user@example.com
Database: postgres://dbuser:SuperSecret123@db.internal:5432/prod
Path: /home/johndoe/projects/secret-project
IP: 192.168.1.100
Session: session_id=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
EOF

# Test sanitization
./sanitize.sh < test_sensitive.txt

# Expected output:
# API_KEY=<api-key-REDACTED>
# Email: <email>
# Database: postgres://<credentials>@<host>
# Path: /home/<username>/projects/secret-project
# IP: <ip-address>
# Session: session_id=<session-id>
```

## Best Practices

### DO
- ✅ Sanitize BEFORE posting, not after
- ✅ Keep original for local debugging
- ✅ Test patterns regularly
- ✅ Err on side of over-sanitization
- ✅ Preserve error context

### DON'T
- ❌ Trust automatic sanitization blindly
- ❌ Post first, sanitize later
- ❌ Remove so much that errors are useless
- ❌ Forget about encoded/hashed secrets
- ❌ Skip review of sanitized output

## Troubleshooting

### Pattern Not Matching
- Check regex escaping for your tool
- Test pattern in isolation
- Verify tool regex syntax support
- Consider case sensitivity

### Over-Sanitization
- Refine patterns to be more specific
- Add negative lookbehind/ahead
- Whitelist known safe patterns
- Use word boundaries

### Performance Issues
- Use streaming for large files
- Pre-compile regex patterns
- Process in chunks
- Use most efficient tool for data size

---
*Security through sanitization is critical. When in doubt, redact it out!*