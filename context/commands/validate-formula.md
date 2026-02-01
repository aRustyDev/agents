---
description: Validate a Homebrew formula with ruby syntax check, brew audit, and brew style
argument-hint: <formula-path> [--fix] [--strict]
allowed-tools: Read, Bash(ruby:*), Bash(brew:*), Bash(ls:*), Bash(cat:*), Glob, Grep
---

# Validate Homebrew Formula

Run a multi-stage validation pipeline on a Homebrew formula file: Ruby syntax check, `brew audit`, and `brew style`.

## Arguments

- `$1` - Path to the formula `.rb` file (required)
- `--fix` - Auto-fix style issues with `brew style --fix` (optional)
- `--strict` - Run `brew audit --strict` for extra checks (optional)

## Workflow

### Step 1: Verify Input

1. Confirm `$1` points to an existing `.rb` file
2. Read the file to confirm it contains a Homebrew formula (class inheriting from `Formula`)
3. Extract the formula name and class name for reporting

### Step 2: Ruby Syntax Check

Run `ruby -c "$1"` to verify valid Ruby syntax.

- If it fails, read the file, identify the syntax error, and report the line number and issue
- Do not proceed to further checks if syntax is invalid

### Step 3: Brew Audit

Run the appropriate audit command:

```bash
# Standard audit
brew audit --formula "$1"

# With --strict flag
brew audit --strict --formula "$1"
```

Capture and categorize output:
- **Errors**: Must fix before submitting
- **Warnings**: Should fix, but not blocking
- **New formula warnings**: Expected for new formulas

### Step 4: Brew Style

Run style check:

```bash
# Check only
brew style "$1"

# With --fix flag (if user passed --fix)
brew style --fix "$1"
```

Report any RuboCop offenses found.

### Step 5: Report Results

Present a summary table:

```
## Validation Results: <formula-name>

| Check | Status | Details |
|-------|--------|---------|
| Ruby syntax | PASS/FAIL | ... |
| brew audit | PASS/WARN/FAIL | N errors, M warnings |
| brew style | PASS/FAIL | N offenses |
```

If all checks pass, suggest:
- `brew install --build-from-source "$1"` to test the build
- `brew test <name>` to run the formula's test block

If checks fail, list each issue with a suggested fix.

## Examples

```
/validate-formula Formula/my-tool.rb
/validate-formula Formula/my-tool.rb --fix
/validate-formula Formula/my-tool.rb --strict
```

## Notes

- Requires Homebrew installed locally (`brew` in PATH)
- `brew audit` needs the formula in a tap or uses `--formula` flag for standalone files
- `--fix` only applies to style (RuboCop) issues, not audit errors
- For new formulas, `--new` flag is automatically added to `brew audit` if the formula doesn't exist in any tap
