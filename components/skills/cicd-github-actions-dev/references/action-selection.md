# Action Selection Reference

Comprehensive guide for choosing and evaluating GitHub Actions with emphasis on the aRustyDev ecosystem approach.

## Action Selection Criteria

### Security Assessment

| Criterion | High Risk | Medium Risk | Low Risk |
|-----------|-----------|-------------|----------|
| **Source** | Unknown author | Community-maintained | Official/verified |
| **Permissions** | `contents: write` + broad | Specific permissions | Read-only or minimal |
| **Code Review** | Obfuscated/compiled only | Source available | Transparent source |
| **Update Pattern** | Irregular/abandoned | Occasional | Regular maintenance |
| **Downloads** | <10K/month | 10K-100K/month | >100K/month |

### Performance Metrics

**Execution Speed:**
```yaml
# Fast: Native actions or compiled binaries
- uses: actions/checkout@v4  # ~5-10 seconds

# Medium: Container actions with caching
- uses: docker://node:18-alpine  # ~30-60 seconds

# Slow: Complex container builds
- uses: custom-action-with-build  # 2-5 minutes
```

**Resource Usage:**
- **Minimal**: Text processing, file operations
- **Moderate**: Build tools, testing frameworks
- **Heavy**: Docker builds, full environment setup

### Maintenance Indicators

| Signal | Good | Warning | Bad |
|--------|------|---------|-----|
| **Last Commit** | <3 months | 3-12 months | >1 year |
| **Issue Response** | <1 week | 1-4 weeks | No response |
| **Version Pattern** | Semantic versioning | Irregular tags | No versioning |
| **Documentation** | Complete + examples | Basic docs | Minimal/none |

## aRustyDev Ecosystem Strategy

### Priority Framework

**1. arustydev/gha (Preferred)**
- Full control and customization
- Consistent with project standards
- Maintained specifically for our use cases
- Security reviewed and approved

**2. Verified Publishers**
```yaml
# GitHub official actions (always safe)
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
- uses: actions/cache@v4
- uses: actions/upload-artifact@v4

# Major platform actions (generally safe)
- uses: aws-actions/configure-aws-credentials@v4
- uses: docker/build-push-action@v5
- uses: microsoft/setup-msbuild@v2
```

**3. High-Quality Community**
```yaml
# Well-maintained actions with good reputation
- uses: peaceiris/actions-gh-pages@v3    # GitHub Pages deployment
- uses: coverallsapp/github-action@v2    # Code coverage
- uses: github/super-linter@v4           # Multi-language linting
```

**4. Temporary Third-Party**
- Use with tracking issue in arustydev/gha
- Include TODO comment with issue reference
- Monitor for security updates
- Plan migration timeline

### Action Discovery Process

**Step 1: Check arustydev/gha**
```bash
# Search existing actions
gh repo view arustydev/gha --json name,description
```

**Step 2: Evaluate Alternatives**
```bash
# Search GitHub marketplace
gh api search/repositories?q="github-action+<functionality>"

# Check action quality metrics
gh api repos/<owner>/<repo> --jq '.stargazers_count, .updated_at, .security_and_analysis'
```

**Step 3: Security Review**
```bash
# Review action source code
gh repo view <owner>/<repo> --web
# Check for:
# - Source code availability
# - Recent security advisories
# - Permission requirements
# - External dependencies
```

## Action Categories by Function

### Code Quality

| Purpose | aRustyDev Preferred | Alternative | Notes |
|---------|-------------------|-------------|-------|
| **Linting** | `arustydev/gha/lint-*` | `github/super-linter` | Language-specific preferred |
| **Formatting** | `arustydev/gha/format-*` | `dprint/check` | Consistent with project style |
| **Security Scan** | `arustydev/gha/security-scan` | `github/codeql-action` | Custom rules + CodeQL |
| **Dependency Check** | `arustydev/gha/audit-deps` | `ossf/scorecard-action` | Supply chain security |

### Testing & Build

| Purpose | aRustyDev Preferred | Alternative | Notes |
|---------|-------------------|-------------|-------|
| **Test Execution** | `arustydev/gha/test-*` | Language setup + scripts | Framework-specific optimizations |
| **Coverage** | `arustydev/gha/coverage` | `codecov/codecov-action` | Unified reporting |
| **Build Artifacts** | `arustydev/gha/build-*` | `actions/upload-artifact` | Enhanced metadata |
| **Docker Build** | `arustydev/gha/docker-build` | `docker/build-push-action` | Registry integration |

### Deployment

| Purpose | aRustyDev Preferred | Alternative | Notes |
|---------|-------------------|-------------|-------|
| **Environment Deploy** | `arustydev/gha/deploy-*` | Platform-specific actions | Multi-environment support |
| **Release Creation** | `arustydev/gha/release` | `softprops/action-gh-release` | Automated changelog |
| **Package Publish** | `arustydev/gha/publish-*` | Registry-specific actions | Multi-registry support |

## Custom Action Development

### When to Create New Action

**Create new action if:**
- No existing action meets specific requirements
- Need integration with aRustyDev tooling
- Complex logic that benefits from reuse
- Security or compliance requirements

**Use script step if:**
- One-time use case
- Simple command execution
- Project-specific logic
- Rapid prototyping

### Development Standards

**Action Metadata (action.yml):**
```yaml
name: 'Action Name'
description: 'Clear description of functionality'
branding:
  icon: 'tool'  # https://feathericons.com/
  color: 'blue'  # https://docs.github.com/actions/creating-actions/metadata-syntax-for-github-actions#branding

inputs:
  required-input:
    description: 'Clear description'
    required: true
  optional-input:
    description: 'Default behavior description'
    required: false
    default: 'default-value'

outputs:
  result:
    description: 'Output description with example format'

runs:
  using: 'node20'  # Use latest supported Node version
  main: 'dist/index.js'
```

**TypeScript Implementation:**
```typescript
import * as core from '@actions/core'
import * as github from '@actions/github'

interface Inputs {
  requiredInput: string
  optionalInput: string
}

function getInputs(): Inputs {
  return {
    requiredInput: core.getInput('required-input', { required: true }),
    optionalInput: core.getInput('optional-input') || 'default-value'
  }
}

async function run(): Promise<void> {
  try {
    const inputs = getInputs()

    core.info(`Processing with: ${inputs.requiredInput}`)

    // Action logic here
    const result = await processAction(inputs)

    // Set outputs
    core.setOutput('result', result)

    core.info('Action completed successfully')
  } catch (error) {
    core.setFailed(error instanceof Error ? error.message : String(error))
  }
}

// Don't call run() if we're being imported for testing
if (require.main === module) {
  run()
}

export { run, getInputs }
```

### Testing Strategy

**Unit Tests:**
```typescript
import { run, getInputs } from '../src/action'
import * as core from '@actions/core'

jest.mock('@actions/core')

describe('Action Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should process required input', () => {
    jest.spyOn(core, 'getInput').mockReturnValue('test-value')

    const inputs = getInputs()

    expect(inputs.requiredInput).toBe('test-value')
  })

  it('should handle errors gracefully', async () => {
    jest.spyOn(core, 'getInput').mockImplementation(() => {
      throw new Error('Input error')
    })
    jest.spyOn(core, 'setFailed')

    await run()

    expect(core.setFailed).toHaveBeenCalledWith('Input error')
  })
})
```

**Integration Tests:**
```yaml
# .github/workflows/test-action.yml
name: Test Action

on:
  push:
    paths:
      - 'actions/my-action/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Test action with valid inputs
        uses: ./actions/my-action
        with:
          required-input: 'test-value'
          optional-input: 'custom-value'
```

## Security Best Practices

### Input Validation

```typescript
function validateInputs(inputs: Inputs): void {
  // Validate required fields
  if (!inputs.requiredInput.trim()) {
    throw new Error('Required input cannot be empty')
  }

  // Validate format/pattern
  if (!/^[a-zA-Z0-9-_]+$/.test(inputs.requiredInput)) {
    throw new Error('Required input contains invalid characters')
  }

  // Validate against known values
  const allowedValues = ['option1', 'option2', 'option3']
  if (!allowedValues.includes(inputs.optionalInput)) {
    throw new Error(`Optional input must be one of: ${allowedValues.join(', ')}`)
  }
}
```

### Safe Command Execution

```typescript
import { exec } from '@actions/exec'

// DON'T: Command injection vulnerable
const unsafeCommand = `git clone ${userInput}`

// DO: Use exec with array arguments
await exec('git', ['clone', userInput])

// DO: Validate and sanitize inputs first
function sanitizeBranchName(branch: string): string {
  return branch.replace(/[^a-zA-Z0-9/-]/g, '')
}
```

### Permission Minimization

```yaml
# Request minimal permissions
permissions:
  contents: read  # Only read repository contents
  pull-requests: write  # Only write to PRs if needed

# Avoid broad permissions
permissions:
  contents: write  # Allows modifying any file
  actions: write   # Allows modifying workflows
```

## Migration Planning

### Third-Party to aRustyDev Migration

**Phase 1: Assessment**
1. Catalog all third-party actions in use
2. Evaluate functionality and complexity
3. Prioritize by usage frequency and risk

**Phase 2: Development**
1. Create issues in arustydev/gha for each needed action
2. Develop locally in consuming projects
3. Test thoroughly before migration

**Phase 3: Migration**
1. Submit developed actions to arustydev/gha
2. Update consuming projects to use new actions
3. Monitor for issues and iterate

**Phase 4: Maintenance**
1. Regular security reviews
2. Performance monitoring
3. Feature enhancement based on usage

### Migration Tracking

```yaml
# Example workflow with migration tracking
jobs:
  build:
    steps:
      # MIGRATED: Now using arustydev action
      - uses: arustydev/gha/setup-node@v1

      # PENDING: Waiting for arustydev/gha#123
      # TODO: Replace with arustydev/gha/deploy-preview@v1
      - uses: third-party/deploy-preview@v2

      # LOCAL: Custom action pending upstream
      # ISSUE: arustydev/gha#456
      - uses: ./.github/actions/custom-scanner
```

## Cross-References

- [GitHub Actions Security Guidelines](https://docs.github.com/en/actions/security-guides)
- [Action Metadata Syntax](https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions)
- [aRustyDev GHA Repository](https://github.com/arustydev/gha)
- [Action Toolkit Documentation](https://github.com/actions/toolkit)