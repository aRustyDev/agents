---
name: github-actions-dev
description: Developing custom GitHub Actions (JavaScript, TypeScript, Docker, Composite). Use this skill when the user asks to 'create a GitHub Action', 'build a custom action', 'publish action to marketplace', 'write action.yml', or 'develop reusable action'.
---

# GitHub Actions Development

## Overview

Guide for developing custom GitHub Actions - the reusable units that are called with `uses:` in workflows. Covers JavaScript/TypeScript actions, Docker actions, and composite actions.

## Action Types

| Type | Best For | Runtime | See Also |
|------|----------|---------|----------|
| **JavaScript/TypeScript** | Fast startup, GitHub API integration | Node.js 20 | [Project Setup](references/project-setup.md) |
| **Docker** | Custom environments, any language | Container | [Docker Guide](references/docker-actions.md) |
| **Composite** | Orchestrating other actions | None (YAML) | [Composite Guide](references/composite-actions.md) |

## Quick Start

### JavaScript Action
```bash
mkdir my-action && cd my-action
npm init -y
npm install @actions/core @actions/github
# See detailed setup: references/project-setup.md
```

### Docker Action
```bash
mkdir my-docker-action && cd my-docker-action
# Create Dockerfile and action.yml
# See: references/docker-actions.md
```

## action.yml Essentials

Basic structure for all action types:

```yaml
name: 'My Action'
description: 'What it does'
author: 'Your Name'

branding:
  icon: 'check-circle'
  color: 'green'

inputs:
  token:
    description: 'GitHub token'
    required: true

outputs:
  result:
    description: 'Action result'

runs:
  using: 'node20'        # or 'docker' or 'composite'
  main: 'dist/index.js'  # Entry point
```

Complete reference: [Action Metadata](references/action-metadata.md)

## Core Development Patterns

### Module System

| Pattern | Usage | Example |
|---------|-------|---------|
| **Toolkit Imports** | Standard action libraries | `import * as core from '@actions/core'` |
| **ES Modules** | Modern JavaScript | `import { readFile } from 'fs/promises'` |
| **CommonJS** | TypeScript compilation | `module: 'commonjs'` in tsconfig |

See [Toolkit API Reference](references/toolkit-api.md) for complete module documentation.

### Error Handling

| Pattern | When to Use | Implementation |
|---------|-------------|----------------|
| **Input Validation** | Required parameters | `core.getInput('token', { required: true })` |
| **Try-Catch** | Async operations | Wrap main logic, call `core.setFailed()` |
| **Graceful Degradation** | Optional features | Continue with warnings vs failing |

```typescript
try {
  const result = await performAction();
  core.setOutput('result', result);
} catch (error) {
  core.setFailed(error instanceof Error ? error.message : 'Unknown error');
}
```

### Concurrency

| Pattern | GitHub Actions Context | Example |
|---------|------------------------|---------|
| **Async/Await** | All toolkit APIs are async | `await octokit.rest.issues.get()` |
| **Parallel Operations** | Independent API calls | `Promise.all([getIssue(), getPR()])` |
| **Sequential Flow** | Dependent operations | `await step1(); await step2();` |

```typescript
// Parallel execution for independent tasks
await core.group('Parallel operations', async () => {
  await Promise.all([
    checkIssues(),
    updatePR(),
    uploadArtifact()
  ]);
});
```

### Metaprogramming

GitHub Actions provides powerful metaprogramming capabilities for dynamic workflow generation:

| Pattern | Purpose | Example |
|---------|---------|---------|
| **Expression Functions** | Runtime evaluation | `${{ fromJson(steps.data.outputs.config) }}` |
| **Matrix Strategies** | Dynamic job generation | Generate jobs from API data |
| **Context Injection** | Runtime inspection | `${{ github.event.pull_request.title }}` |
| **Reusable Workflows** | Macro-like abstractions | Template workflows with parameters |
| **Code Generation** | TypeScript action builders | Generate action.yml from schema |

```yaml
# Dynamic matrix from API
strategy:
  matrix:
    include: ${{ fromJson(steps.get-matrix.outputs.matrix) }}

# Context-based conditionals
if: ${{ github.event_name == 'pull_request' && contains(github.event.pull_request.title, 'feat') }}

# Expression functions
run: |
  CONFIG='${{ toJson(github.event.client_payload) }}'
  ESCAPED='${{ toJson(env.USER_INPUT) }}'
```

**Advanced Metaprogramming:**
```typescript
// TypeScript action that generates other actions
import { generateActionMetadata } from './generator';

const schema = await readSchema('action-schema.json');
const actionYml = generateActionMetadata(schema);
await writeFile('action.yml', actionYml);
```

See [Metaprogramming Patterns](references/metaprogramming.md) for complete examples.

### Zero/Default Handling

| Pattern | GitHub Actions Context | Implementation |
|---------|------------------------|----------------|
| **Input Defaults** | action.yml defaults | `default: '.github/config.yml'` |
| **Runtime Defaults** | Code-level defaults | `core.getInput('timeout') || '30'` |
| **Empty Handling** | Missing inputs/outputs | Check for empty strings, not undefined |

```typescript
const timeout = parseInt(core.getInput('timeout') || '30', 10);
const files = core.getMultilineInput('files').filter(f => f.trim());
```

### Serialization

| Data Type | GitHub Actions Pattern | Usage |
|-----------|------------------------|-------|
| **JSON Objects** | Inputs/outputs | `core.setOutput('data', JSON.stringify(obj))` |
| **Multiline Strings** | File contents | `core.getMultilineInput()` |
| **Base64** | Binary data | Encode before setting output |

```typescript
// Complex data serialization
const results = { passed: 10, failed: 2, files: ['a.js', 'b.js'] };
core.setOutput('test-results', JSON.stringify(results));

// Reading complex input
const config = JSON.parse(core.getInput('config') || '{}');
```

### Build/Tooling

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **TypeScript** | Type safety | `tsconfig.json` with Node.js targets |
| **ncc** | Bundling | Single file for distribution |
| **Jest** | Testing | Unit and integration tests |

```json
{
  "scripts": {
    "build": "ncc build src/main.ts -o dist --source-map",
    "test": "jest",
    "all": "npm run build && npm test"
  }
}
```

See [Build Configuration](references/build-tooling.md) for complete setup.

### Testing

| Test Type | Scope | Implementation |
|-----------|-------|----------------|
| **Unit Tests** | Individual functions | Jest with mocked toolkit |
| **Integration Tests** | Full action | Real GitHub workflows |
| **Local Testing** | Development | Act for local execution |

```typescript
// Unit test with mocked toolkit
jest.mock('@actions/core');
const mockSetOutput = core.setOutput as jest.Mock;

test('sets correct output', async () => {
  await run();
  expect(mockSetOutput).toHaveBeenCalledWith('result', 'success');
});
```

See [Testing Guide](references/testing.md) for comprehensive examples.

## Development Workflow

### 1. Setup
```bash
# Quick start
npx create-action my-action
# or manual setup - see references/project-setup.md
```

### 2. Development
```bash
npm run build    # Bundle with ncc
npm test         # Run test suite
npm run all      # Build + test
```

### 3. Testing
```bash
# Local testing with act
act -j test -s GITHUB_TOKEN="$(gh auth token)"
```

### 4. Publishing
```bash
git tag v1.0.0
git push origin v1.0.0
# Create GitHub release
# Check "Publish to Marketplace"
```

See [Publishing Guide](references/publishing.md) for complete release process.

## Common Gotchas

### Input/Output Issues
- Empty inputs return `""`, not `undefined`
- Outputs must be strings (use `JSON.stringify()` for objects)
- Required inputs throw if missing, optional inputs return empty string

### Bundle Management
- Always commit `dist/` folder for JavaScript actions
- Use `ncc` to create single-file bundles
- Don't bundle `node_modules` in Docker actions

### Permissions
- Default `GITHUB_TOKEN` has limited permissions
- Use `permissions:` in workflow to grant specific access
- Personal tokens need explicit scopes

## Quick Reference

### Essential Commands
```bash
# Toolkit APIs
npm install @actions/core @actions/github @actions/exec @actions/io

# Development
npm run build && npm test
act -j test

# Release
git tag v1.0.0 && git push origin v1.0.0
```

### File Structure
```
my-action/
├── action.yml          # Action metadata
├── src/main.ts         # Entry point
├── dist/index.js       # Bundled output (committed)
├── __tests__/          # Test files
└── package.json        # Dependencies
```

## See Also

### Reference Documentation
- [Toolkit API Reference](references/toolkit-api.md) - Complete `@actions/*` package documentation
- [Publishing Guide](references/publishing.md) - Marketplace publication process
- [Project Setup](references/project-setup.md) - Detailed project initialization
- [Testing Guide](references/testing.md) - Comprehensive testing strategies
- [Build Tooling](references/build-tooling.md) - TypeScript, bundling, CI configuration
- [Metaprogramming Patterns](references/metaprogramming.md) - Dynamic workflow generation

### Action Type Guides
- [Action Metadata](references/action-metadata.md) - Complete action.yml reference
- [Docker Actions](references/docker-actions.md) - Container-based actions
- [Composite Actions](references/composite-actions.md) - YAML-based action orchestration

### Examples
- [Templates](assets/templates/) - Project templates and examples
- [Sample Actions](assets/examples/) - Real-world action implementations