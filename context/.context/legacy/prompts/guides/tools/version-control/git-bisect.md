---
name: Git Bisect Deep Dive
module_type: guide
scope: temporary
priority: low
triggers: ["git bisect", "binary search", "find bug commit", "regression", "bisect run", "bug hunting"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Git Bisect Deep Dive

## Purpose
Master git bisect for efficiently finding the commit that introduced a bug using binary search, including automation strategies and advanced techniques.

## Understanding Git Bisect

### How It Works
Git bisect performs a binary search through your commit history:
- Start with a known bad commit (has the bug)
- Identify a known good commit (doesn't have the bug)
- Git checks out the middle commit
- You test and mark as good or bad
- Process repeats until the problematic commit is found

### Time Complexity
With 1000 commits between good and bad:
- Linear search: up to 1000 tests
- Binary search: ~10 tests (log₂(1000))

## Basic Bisect Workflow

### Manual Bisecting
```bash
# Start bisect session
git bisect start

# Mark current commit as bad
git bisect bad

# Mark a known good commit
git bisect good v1.0
# or
git bisect good abc123

# Git checks out middle commit
# Test your code here...

# Mark result
git bisect good  # if bug not present
git bisect bad   # if bug present

# Continue until git finds the bad commit
# Git will output:
# abc123def is the first bad commit

# End bisect session
git bisect reset
```

### Bisect with Range
```bash
# Start with range specified
git bisect start HEAD v1.0

# Equivalent to:
git bisect start
git bisect bad HEAD
git bisect good v1.0
```

### Viewing Bisect Progress
```bash
# See remaining commits
git bisect visualize
# or
gitk --bisect

# Show bisect log
git bisect log

# See how many steps left
git bisect good
# Bisecting: 5 revisions left to test after this
```

## Automated Bisecting

### Basic Automation
```bash
# Create test script
cat > test.sh << 'EOF'
#!/bin/bash
# Exit 0 if good, 1 if bad

# Example: test if file exists
if [ -f "important.txt" ]; then
    exit 0
else
    exit 1
fi
EOF

chmod +x test.sh

# Run automated bisect
git bisect start HEAD v1.0
git bisect run ./test.sh
```

### Complex Test Scripts
```bash
#!/bin/bash
# test_regression.sh

# Build the project
make clean && make
if [ $? -ne 0 ]; then
    # Build failed - skip this commit
    exit 125
fi

# Run specific test
./run_tests --only regression_test
if [ $? -eq 0 ]; then
    exit 0  # Test passed - good commit
else
    exit 1  # Test failed - bad commit
fi
```

### Python Test Script
```python
#!/usr/bin/env python3
# bisect_test.py

import subprocess
import sys

def test_feature():
    """Return True if feature works correctly"""
    try:
        # Run your test
        result = subprocess.run(
            ['python', 'app.py', '--test'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check for specific output
        if "ERROR" in result.stderr:
            return False
        
        if "Success" in result.stdout:
            return True
            
        return False
        
    except subprocess.TimeoutExpired:
        # Timeout means bad
        return False
    except Exception:
        # Skip this commit
        sys.exit(125)

if __name__ == "__main__":
    if test_feature():
        sys.exit(0)  # Good
    else:
        sys.exit(1)  # Bad
```

### Exit Codes for Bisect Run
```bash
# Special exit codes:
# 0     - Good commit (test passed)
# 1-124 - Bad commit (test failed)  
# 125   - Skip this commit (cannot test)
# 126   - Test script not executable
# 127   - Test script not found
# 128+  - Fatal error, abort bisect

# Example skip conditions
#!/bin/bash
# Skip if dependencies missing
if ! command -v node &> /dev/null; then
    exit 125
fi

# Skip if build fails
if ! make build; then
    exit 125
fi

# Run actual test
npm test
```

## Advanced Techniques

### Bisecting with Terms
```bash
# Use custom terms instead of good/bad
git bisect start --term-new=slow --term-old=fast

# When performance degraded
git bisect start
git bisect slow HEAD
git bisect fast v1.0

# Custom terms for clarity
git bisect start --term-new=broken --term-old=working
```

### Bisecting Merge Commits
```bash
# Include first parent only (mainline)
git bisect start --first-parent

# Helps when bisecting through merge-heavy history
git bisect start --first-parent HEAD v1.0
```

### Skipping Commits
```bash
# Skip current commit
git bisect skip

# Skip multiple commits
git bisect skip v1.5..v1.6

# Skip specific commits
git bisect skip abc123 def456

# Pattern: skip all WIP commits
git log --oneline | grep WIP | cut -d' ' -f1 | xargs git bisect skip
```

### Replaying Bisect Sessions
```bash
# Save bisect log
git bisect log > bisect.log

# Later, replay the session
git bisect start
git bisect replay bisect.log

# Useful for:
# - Sharing bisect progress
# - Resuming after interruption
# - Debugging bisect issues
```

## Real-World Scenarios

### Performance Regression
```bash
#!/bin/bash
# find_performance_regression.sh

# Baseline performance (in ms)
BASELINE=1000
TOLERANCE=1.1  # 10% tolerance

# Run benchmark
TIME=$(./benchmark.sh | grep "Time:" | awk '{print $2}')

# Compare with baseline
if (( $(echo "$TIME > $BASELINE * $TOLERANCE" | bc -l) )); then
    echo "Performance regression detected: ${TIME}ms"
    exit 1
else
    echo "Performance OK: ${TIME}ms"
    exit 0
fi
```

### Finding Breaking API Change
```python
#!/usr/bin/env python3
# test_api_compatibility.py

import requests
import sys

def test_api():
    try:
        # Test old API endpoint
        response = requests.get('http://localhost:8080/api/v1/users')
        
        # Check if response has expected structure
        data = response.json()
        
        # Old API should have 'username' field
        if 'username' in data[0]:
            return True  # Old API structure (good)
        else:
            return False  # New API structure (bad)
            
    except Exception as e:
        print(f"Cannot test: {e}")
        sys.exit(125)  # Skip

if __name__ == "__main__":
    sys.exit(0 if test_api() else 1)
```

### CSS/UI Regression
```javascript
#!/usr/bin/env node
// visual_regression_test.js

const puppeteer = require('puppeteer');
const pixelmatch = require('pixelmatch');
const fs = require('fs');
const PNG = require('pngjs').PNG;

async function testVisual() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    try {
        await page.goto('http://localhost:3000');
        await page.screenshot({ path: 'current.png' });
        
        // Compare with baseline
        const baseline = PNG.sync.read(fs.readFileSync('baseline.png'));
        const current = PNG.sync.read(fs.readFileSync('current.png'));
        
        const diff = pixelmatch(
            baseline.data,
            current.data,
            null,
            baseline.width,
            baseline.height,
            { threshold: 0.1 }
        );
        
        await browser.close();
        
        // Exit based on difference
        process.exit(diff > 100 ? 1 : 0);
        
    } catch (error) {
        await browser.close();
        process.exit(125); // Skip
    }
}

testVisual();
```

## Bisect Strategies

### Strategy 1: Coarse to Fine
```bash
# First pass: find general area
git bisect start HEAD v1.0
git bisect run ./quick_test.sh

# Second pass: detailed testing
git bisect reset
git bisect start <bad-commit>^ <bad-commit>~10
git bisect run ./detailed_test.sh
```

### Strategy 2: Multiple Bugs
```bash
# When multiple bugs might exist

# Find first bug
git bisect start HEAD v1.0
git bisect run ./test_bug1.sh
# Found: abc123

# Find second bug
git bisect reset
git bisect start HEAD abc123^
git bisect run ./test_bug2.sh
```

### Strategy 3: Flaky Tests
```bash
#!/bin/bash
# Handle flaky tests with retry logic

run_test() {
    for i in {1..3}; do
        if ./actual_test.sh; then
            return 0
        fi
        sleep 1
    done
    return 1
}

# Require consistent results
PASS_COUNT=0
for i in {1..5}; do
    if run_test; then
        ((PASS_COUNT++))
    fi
done

# Require 4/5 passes
if [ $PASS_COUNT -ge 4 ]; then
    exit 0
else
    exit 1
fi
```

## Integration with CI/CD

### GitHub Actions Bisect
```yaml
name: Bisect Regression

on:
  workflow_dispatch:
    inputs:
      good_ref:
        description: 'Known good reference'
        required: true
      bad_ref:
        description: 'Known bad reference'
        required: true
        default: 'HEAD'

jobs:
  bisect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Run git bisect
        run: |
          git bisect start ${{ github.event.inputs.bad_ref }} ${{ github.event.inputs.good_ref }}
          git bisect run ./scripts/bisect_test.sh
          
      - name: Report result
        if: always()
        run: |
          echo "BISECT RESULT:"
          git bisect log | tail -20
```

### Bisect Helper Script
```bash
#!/bin/bash
# bisect_helper.sh - Wrapper for common bisect tasks

case "$1" in
    "build-fail")
        git bisect start HEAD $2
        git bisect run bash -c 'make clean && make || exit 1'
        ;;
        
    "test-fail")
        git bisect start HEAD $2
        git bisect run bash -c 'make test || exit 1'
        ;;
        
    "performance")
        git bisect start HEAD $2
        git bisect run ./scripts/performance_test.sh
        ;;
        
    "custom")
        git bisect start HEAD $2
        git bisect run "${@:3}"
        ;;
        
    *)
        echo "Usage: $0 {build-fail|test-fail|performance|custom} <good-ref> [args]"
        exit 1
        ;;
esac
```

## Best Practices

### DO
- ✅ Write deterministic test scripts
- ✅ Handle build failures with exit 125
- ✅ Use version tags as good references
- ✅ Save bisect logs for documentation
- ✅ Clean state between tests

### DON'T
- ❌ Use time-dependent tests
- ❌ Forget to reset after bisecting
- ❌ Test with uncommitted changes
- ❌ Ignore flaky test results
- ❌ Skip validating good/bad markers

## Troubleshooting

### Common Issues
```bash
# Reset if bisect gets confused
git bisect reset

# Check bisect state
cat .git/BISECT_LOG

# Visualize what's being tested
git log --oneline --graph --bisect

# If wrong commit marked
git bisect log > backup.log
git bisect reset
# Edit backup.log to fix
git bisect replay backup.log
```

### Debugging Test Scripts
```bash
# Debug mode for test scripts
#!/bin/bash
set -x  # Print commands
set -e  # Exit on error

# Add logging
echo "Testing commit: $(git rev-parse HEAD)" >> bisect_debug.log
echo "Date: $(date)" >> bisect_debug.log

# Your test here
```

---
*Git bisect is a powerful debugging tool that can save hours of manual searching. Automate it well, and it becomes an invaluable part of your debugging toolkit.*