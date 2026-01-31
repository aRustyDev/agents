---
name: Tool Selection Process
module_type: process
scope: context
priority: medium
triggers: ["select tool", "tool availability", "fallback chain"]
dependencies: ["core/defaults.md"]
conflicts: []
version: 1.0.0
---

# Tool Selection Process

## Purpose
Select the most appropriate tool from configured options based on availability and requirements. This process ensures reliable tool selection with proper fallback chains.

## Parameters
- **tool_category**: Category of tools needed (text/json/structured_logs)
- **complexity**: Required complexity level (simple/medium/complex/any)

## Process Steps

### 1. Load Tool Configuration
Read tool preferences from configuration:

```yaml
# From core/defaults.md
sanitization_tools:
  text:
    - tool: sed
      available: check
      complexity: simple
    - tool: awk
      available: check
      complexity: medium
    - tool: perl
      available: check
      complexity: complex
    - tool: python
      available: assume
      complexity: any
```

Filter by:
1. Matching tool_category
2. Complexity >= required complexity
3. Preference order (list order)

### 2. Check Tool Availability

For each tool in filtered list:

#### If available: "check"
```bash
command -v ${tool_name} >/dev/null 2>&1
if [ $? -eq 0 ]; then
    mark_available=true
else
    mark_available=false
fi
```

#### If available: "assume"
Mark as available without checking (e.g., python usually present)

#### Build Available Tools List
```yaml
available_tools:
  - name: sed
    available: true
    complexity: simple
    priority: 1
  - name: python
    available: true
    complexity: any
    priority: 4
```

### 3. Select Primary Tool

Selection algorithm:
```
1. From available_tools where complexity >= required
2. Sort by priority (preference order)
3. Select first tool
4. If no tools available:
   - Alert user
   - Suggest installation
   - Offer manual alternatives
```

Example selection:
- Required: complexity=medium
- Available: sed(simple), awk(medium), python(any)
- Selected: awk (first tool meeting requirements)

### 4. Prepare Fallback Chain

Create ordered fallback list:
```yaml
primary: awk
fallbacks:
  - python (higher complexity, always available)
  - manual (last resort)
```

Document reasons:
- sed: Insufficient complexity for task
- perl: Not installed
- python: Available but lower preference

### 5. Return Tool Configuration

Output structure:
```yaml
selected_tool:
  name: awk
  command: awk
  complexity: medium
  syntax_notes: "Use POSIX ERE syntax"
  
fallback_chain:
  - name: python
    command: python3
    reason: "Universal fallback"
  - name: manual
    command: null
    reason: "No automated tools available"

usage_examples:
  - description: "Email sanitization"
    command: "awk '{gsub(/[\\w.-]+@[\\w.-]+\\.[\\w]+/, \"<email>\"); print}'"
```

## Tool Categories

### Text Processing Tools

#### sed
- **Complexity**: simple
- **Best for**: Single-line regex replacements
- **Limitations**: Complex multi-line patterns difficult
- **Check**: `command -v sed`

#### awk  
- **Complexity**: medium
- **Best for**: Structured text, field processing
- **Limitations**: Very complex nested patterns
- **Check**: `command -v awk`

#### perl
- **Complexity**: complex
- **Best for**: Advanced regex, multi-line
- **Limitations**: May not be installed
- **Check**: `command -v perl`

#### python
- **Complexity**: any
- **Best for**: Universal fallback, complex logic
- **Limitations**: Slower for simple tasks
- **Check**: Usually assumed available

### JSON Processing Tools

#### jq
- **Complexity**: any
- **Best for**: JSON manipulation and queries
- **Limitations**: JSON only
- **Check**: `command -v jq`

#### python
- **Complexity**: any
- **Best for**: JSON with complex logic
- **Limitations**: More verbose than jq
- **Check**: `python3 -m json.tool`

### Log Processing Tools

#### awk
- **Complexity**: medium
- **Best for**: Structured logs, patterns
- **Limitations**: Very complex parsing
- **Check**: `command -v awk`

#### python
- **Complexity**: any
- **Best for**: Complex log analysis
- **Limitations**: Overhead for simple tasks
- **Check**: Usually available

## Integration Points
- Used by: Process: DataSanitization
- References: core/defaults.md for tool configs
- May trigger: Tool installation prompts

## Usage Examples

### Simple Text Sanitization
```bash
# Request
tool_category: text
complexity: simple

# Response
selected_tool: sed
command: sed -E 's/pattern/replacement/g'
```

### Complex JSON Processing
```bash
# Request  
tool_category: json
complexity: complex

# Response
selected_tool: jq
fallback: python3 -m json.tool
```

### When Primary Tool Unavailable
```bash
# Request
tool_category: text
complexity: medium

# Check awk availability
command -v awk  # Returns error

# Response
selected_tool: python
reason: "awk not available, using python fallback"
```

## Error Handling

### No Tools Available
```yaml
error: "No tools available for category"
suggestions:
  - "Install awk: apt-get install gawk"
  - "Install jq: apt-get install jq"
  - "Use manual sanitization"
```

### Insufficient Complexity
```yaml
error: "No tools meet complexity requirement"
available: ["sed (simple)"]
required: "complex"
suggestion: "Install perl or use python"
```

## Best Practices

### Tool Selection
- Prefer simpler tools for simple tasks
- Check availability before depending on tools
- Always provide fallback options
- Document tool requirements

### Performance Considerations
- sed/awk faster for simple patterns
- jq optimal for JSON
- Python for complex logic
- Consider data size when selecting

### Portability
- Assume python available
- Check for GNU vs BSD variants
- Provide platform-specific alternatives
- Test on target systems

---
*Reliable tool selection ensures processes work across different environments.*