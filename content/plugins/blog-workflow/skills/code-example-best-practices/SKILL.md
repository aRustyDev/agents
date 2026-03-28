---
name: code-example-best-practices
description: Guidelines for writing effective code examples in technical blog posts
created: 2025-02-19
updated: 2025-02-19
tags: [blog, code, examples, documentation]
source: blog-workflow-plugin
---

# Code Example Best Practices

Guidelines for writing clear, effective code examples in technical blog posts.

## Overview

Code examples are often the most valuable part of technical content. This skill provides standards for writing code snippets that are easy to understand, copy, and adapt.

**This skill covers:**

- Code snippet formatting and structure
- Comment and annotation guidelines
- Context and setup requirements
- Error handling in examples

**This skill does NOT cover:**

- Prose writing style (see technical-writing-style)
- Overall post structure (see content-structure-patterns)

## Quick Reference

### Code Block Essentials

| Element | Guideline |
|---------|-----------|
| Language tag | Always specify (`python`, `bash`, etc.) |
| Length | Under 30 lines preferred |
| Width | Under 80 characters per line |
| Comments | Explain "why", not "what" |
| Imports | Include when relevant to example |

### Example Quality Checklist

- [ ] Runs without modification
- [ ] Language tag specified
- [ ] Non-obvious lines commented
- [ ] Variables have meaningful names
- [ ] Sensitive values use placeholders
- [ ] Expected output shown (where helpful)

## Principles

### 1. Make Examples Runnable

Code that doesn't run frustrates readers. Every example should:

- Include necessary imports
- Define required variables
- Use realistic (but safe) placeholder values
- Work in a standard environment

**Good:**

```python
import os
from pathlib import Path

# Read config from environment (provide default for local dev)
api_key = os.environ.get("API_KEY", "your-api-key-here")
config_path = Path("config.json")

if config_path.exists():
    config = json.loads(config_path.read_text())
```

**Bad:**

```python
# Missing imports, undefined variables
config = json.loads(config_path.read_text())
```

### 2. Keep Examples Focused

Show only what's necessary. Strip everything else.

**Good:**

```python
# Retry with exponential backoff
for attempt in range(max_retries):
    try:
        return make_request(url)
    except RequestError:
        sleep(2 ** attempt)
raise MaxRetriesExceeded()
```

**Bad:**

```python
# Too much context obscures the pattern
import requests
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    max_retries: int = 3
    base_url: str = "https://api.example.com"
    timeout: int = 30

def make_request(url: str, config: Optional[Config] = None) -> dict:
    config = config or Config()
    # ... 20 more lines before getting to the retry logic
```

### 3. Use Progressive Disclosure

For complex examples, build up incrementally:

#### Step 1: Basic version

```python
def process_data(data):
    return [item.upper() for item in data]
```

#### Step 2: Add error handling

```python
def process_data(data):
    results = []
    for item in data:
        try:
            results.append(item.upper())
        except AttributeError:
            results.append(str(item).upper())
    return results
```

#### Step 3: Add logging (optional)

```python
def process_data(data, logger=None):
    results = []
    for item in data:
        try:
            results.append(item.upper())
        except AttributeError:
            if logger:
                logger.warning(f"Converting {type(item)} to string")
            results.append(str(item).upper())
    return results
```

### 4. Show Expected Output

Help readers verify they're on track:

```bash
$ curl -s https://api.example.com/health | jq
{
  "status": "healthy",
  "version": "1.2.3"
}
```

```python
>>> calculate_hash("hello world")
'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
```

## Formatting Standards

### Language Tags

Always specify the language for syntax highlighting:

````markdown
```python
def example():
    pass
```
````

Common tags: `python`, `javascript`, `typescript`, `bash`, `json`, `yaml`, `sql`, `go`, `rust`

### Line Length

Keep lines under 80 characters to prevent horizontal scrolling:

```python
# Good: Line breaks at logical points
result = (
    some_long_function_name(
        parameter_one=value,
        parameter_two=other_value,
    )
)

# Avoid: Long lines that scroll
result = some_long_function_name(parameter_one=value, parameter_two=other_value, parameter_three=another_value)
```

### Comments

Comment the "why", not the "what":

```python
# Good: Explains reasoning
# Use a set for O(1) lookup on large datasets
seen = set()

# Bad: States the obvious
# Create a set called seen
seen = set()
```

Inline comments for non-obvious lines:

```python
response = client.get(url, timeout=30)  # Server can be slow during peak hours
data = response.json().get("results", [])  # API returns empty list as null
```

### Placeholder Values

Use obvious placeholders that won't accidentally work:

| Type | Good Placeholder | Bad Placeholder |
|------|-----------------|-----------------|
| API keys | `your-api-key-here` | `abc123` |
| URLs | `https://api.example.com` | `https://api.com` |
| Passwords | `<your-password>` | `password123` |
| Emails | `user@example.com` | `test@test.com` |
| IDs | `12345` or `<user-id>` | `1` |

### Diffs and Changes

Show what changed when modifying code:

```diff
 def process_data(data):
-    return data.upper()
+    return data.strip().upper()
```

Or use comments to highlight changes:

```python
def process_data(data):
    return data.strip().upper()  # Added strip() to handle whitespace
```

## Common Patterns

### Configuration Examples

Show both environment variables and code:

```bash
# Set in your shell or .env file
export DATABASE_URL="postgres://user:pass@localhost:5432/mydb"
export REDIS_URL="redis://localhost:6379"
```

```python
import os

DATABASE_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
```

### Command Line Examples

Use `$` prefix for commands, show output without prefix:

```bash
$ npm install express
added 57 packages in 2.3s

$ npm start
Server running on http://localhost:3000
```

### Multi-File Examples

When showing multiple files, use clear headers:

**`src/config.py`**

```python
DATABASE_URL = "postgres://localhost/mydb"
```

**`src/main.py`**

```python
from config import DATABASE_URL
```

### Error Examples

When showing errors, include enough context to diagnose:

```python
>>> import missing_module
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'missing_module'
```

## Anti-Patterns

### Screenshot of Code

Never use images for code. Always use text that readers can copy.

### Untested Examples

Run every example before publishing. Typos and API changes break tutorials.

### Missing Context

Don't assume readers know the file structure or have run previous steps:

```python
# Bad: Where does 'client' come from?
response = client.get("/users")

# Good: Show the setup
from myapp import create_client
client = create_client(api_key=os.environ["API_KEY"])
response = client.get("/users")
```

### Hardcoded Secrets

Never include real credentials, even in "example" form:

```python
# NEVER do this
api_key = "sk-live-abc123..."  # This looks like a real key

# Do this instead
api_key = os.environ["API_KEY"]
```

## See Also

- `technical-writing-style` skill - Writing prose around code
- `content-structure-patterns` skill - Where code fits in post structure
