---
name: Commit Standards
module_type: process
scope: persistent
priority: high
triggers: ["commit", "git commit", "commit message", "conventional commits"]
dependencies: ["core/defaults.md", "processes/security/data-sanitization.md"]
conflicts: []
version: 1.0.0
---

# Commit Standards Process

## Purpose
Ensure all commits follow conventional standards, include proper issue references, handle pre-commit hooks gracefully, and maintain a clean, traceable git history.

## Trigger
Execute whenever code changes need to be committed to version control.

## Commit Message Format

### Structure
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Type (Required)
Must be one of:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect code meaning (formatting, missing semicolons, etc)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes affecting build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Scope (Optional)
Component or area affected: auth, api, ui, core, etc.

### Description (Required)
- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize first letter
- No period at the end
- Maximum 72 characters

## Process Steps

### 1. Stage Changes
```bash
# Review what will be committed
${version_control} diff

# Stage atomic changes
${version_control} add ${files}

# Verify staged changes
${version_control} status
```

**Ensure**:
- Changes are atomic (one logical change)
- Related files committed together
- Unrelated changes separated

### 2. Determine Commit Type
Analyze changes to select appropriate type:
- New functionality → feat
- Bug correction → fix
- Code improvement without behavior change → refactor
- Test additions/updates → test

Check if this:
- Closes an issue → Add "Fixes #X"
- Relates to issue → Add "Related to #X"
- Breaking change → Add "BREAKING CHANGE:" footer

### 3. Write Commit Message

#### Header Line
Format: `<type>(<scope>): <description>`

Example: `feat(auth): add password reset functionality`

#### Body (if needed)
- Blank line after header
- Explain what and why (not how)
- Wrap at 72 characters
- Use bullet points for multiple items

#### Footer
- Issue references: `Fixes #123`
- Breaking changes: `BREAKING CHANGE: explanation`
- Co-authors: `Co-authored-by: Name <email>`

### 4. Execute Commit

#### Pre-commit Preparation
```bash
# If message contains sensitive data
Execute: Process: DataSanitization
Input: Commit message content
```

#### Run Commit
```bash
${version_control} commit
```

#### If Pre-commit Hooks Fail

1. **Capture Failure**
   - Record full error output
   - Identify failure type (lint, test, format)

2. **Create Tracking Issue**
   ```
   Title: "Pre-commit: ${failure_type} in ${context}"
   Labels: ['pre-commit', 'tooling']
   Body: 
   - Error message (sanitized)
   - Files affected
   - Attempted solutions
   ```

3. **Fix Issues**
   - Apply suggested fixes
   - Re-run failed checks locally
   - Document solution in issue

4. **Check for Pattern**
   If similar failure occurred before:
   - Execute: Process: RecurringProblemIdentification
   - Consider creating custom hook

5. **Retry Commit**
   - Stage fixes
   - Attempt commit again

### 5. Push Changes
```bash
${version_control} push
```

If push fails:
- Execute: Process: PushFailureResolution
- Document resolution
- Retry until successful

### 6. Verify Success
- Check remote repository
- Ensure CI/CD triggered
- Monitor pipeline status

## Message Examples

### Feature with Issue
```
feat(api): implement user search endpoint

Add full-text search capability for users with:
- Email and name search
- Pagination support
- Result sorting options

Fixes #234
```

### Bug Fix
```
fix(auth): prevent session timeout during active use

Sessions were expiring even when user was actively using
the system. Now properly extends session on each request.

Fixes #567
```

### Breaking Change
```
refactor(api)!: change response format to camelCase

BREAKING CHANGE: All API responses now use camelCase
instead of snake_case. Update clients accordingly.

Migration guide: docs/migrations/v2-api-changes.md
```

### Test-Driven Development
```
test(utils): add failing test for date parsing edge case

Documents expected behavior for leap year handling.
Part of TDD red phase.
```

## Pre-commit Hook Patterns

### Common Failures

#### Linting Errors
```bash
# Auto-fix when possible
npm run lint:fix
# or
black . --line-length 100
```

#### Import Sorting
```bash
# Python
isort .

# JavaScript
npx import-sort-cli --write '**/*.js'
```

#### Trailing Whitespace
```bash
# Remove trailing whitespace
find . -type f -name "*.py" -exec sed -i 's/[ \t]*$//' {} +
```

## Integration Points
- Links to: Process: DataSanitization (message security)
- Links to: Process: IssueUpdate (tracking commits)
- Links to: Process: PushFailureResolution (push issues)
- Triggers: CI/CD pipeline on successful push

## Best Practices

### DO
- ✅ Commit early and often
- ✅ Keep commits atomic
- ✅ Write descriptive messages
- ✅ Reference related issues
- ✅ Fix pre-commit issues immediately

### DON'T
- ❌ Mix unrelated changes
- ❌ Use vague messages like "fix stuff"
- ❌ Skip pre-commit hooks
- ❌ Commit sensitive data
- ❌ Leave broken tests

## Troubleshooting

### Amending Commits
```bash
# Fix the last commit message
${version_control} commit --amend

# Add forgotten files to last commit
${version_control} add forgotten_file
${version_control} commit --amend --no-edit
```

### Reverting Commits
```bash
# Create a revert commit
${version_control} revert <commit-sha>
# Message: "revert: <original message>"
```

---
*Consistent commit messages enable automation, improve collaboration, and create meaningful project history.*