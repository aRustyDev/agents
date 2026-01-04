# GitHub Actions Testing Guide

Comprehensive testing strategies for GitHub Actions development.

## Testing Pyramid

```
         E2E Tests (GitHub Workflows)
       ████████████████████████████
      Integration Tests (Act/Local)
   ████████████████████████████████████
  Unit Tests (Jest with Mocks)
████████████████████████████████████████████
```

### Test Types by Scope

| Test Type | What to Test | Tools | Frequency |
|-----------|--------------|-------|-----------|
| **Unit Tests** | Individual functions, input validation | Jest + Mocks | Every commit |
| **Integration Tests** | Full action with real filesystem | Jest + Temporary directories | PR/Release |
| **Local E2E Tests** | Action in real GitHub environment | Act | Before release |
| **GitHub E2E Tests** | Action in production | GitHub workflows | Release/Deploy |

## Unit Testing

### Test Setup

```typescript
// __tests__/setup.ts
import { jest } from '@jest/globals';

// Clear all mocks between tests
beforeEach(() => {
  jest.clearAllMocks();
  jest.resetModules();

  // Reset environment
  delete process.env.GITHUB_REPOSITORY;
  delete process.env.GITHUB_ACTOR;
  delete process.env.INPUT_TOKEN;
});

// Mock GitHub context
jest.mock('@actions/github', () => ({
  context: {
    repo: { owner: 'test-owner', repo: 'test-repo' },
    actor: 'test-actor',
    sha: 'abc123',
    ref: 'refs/heads/main',
    payload: {}
  },
  getOctokit: jest.fn()
}));
```

### Input Validation Tests

```typescript
// __tests__/input.test.ts
import * as core from '@actions/core';
import { getInputs } from '../src/input';

jest.mock('@actions/core');
const mockCore = core as jest.Mocked<typeof core>;

describe('Input validation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getInputs', () => {
    it('should return valid inputs', () => {
      mockCore.getInput.mockImplementation((name: string) => {
        const inputs: Record<string, string> = {
          'token': 'ghp_1234567890abcdef1234567890abcdef12345678',
          'config-path': '.github/my-config.yml',
          'timeout': '120'
        };
        return inputs[name] || '';
      });

      mockCore.getBooleanInput.mockReturnValue(false);
      mockCore.getMultilineInput.mockReturnValue(['file1.js', 'file2.js']);

      const inputs = getInputs();

      expect(inputs).toEqual({
        token: 'ghp_1234567890abcdef1234567890abcdef12345678',
        configPath: '.github/my-config.yml',
        timeout: 120,
        dryRun: false,
        files: ['file1.js', 'file2.js']
      });
    });

    it('should throw on invalid token format', () => {
      mockCore.getInput.mockImplementation((name: string) => {
        if (name === 'token') return 'invalid-token';
        return '';
      });

      expect(() => getInputs()).toThrow('Invalid GitHub token format');
    });

    it('should throw on invalid timeout', () => {
      mockCore.getInput.mockImplementation((name: string) => {
        const inputs: Record<string, string> = {
          'token': 'ghp_1234567890abcdef1234567890abcdef12345678',
          'timeout': '3700' // Too large
        };
        return inputs[name] || '';
      });

      expect(() => getInputs()).toThrow('Timeout must be between 1 and 3600 seconds');
    });

    it('should handle empty file list', () => {
      mockCore.getInput.mockImplementation((name: string) => {
        if (name === 'token') return 'ghp_1234567890abcdef1234567890abcdef12345678';
        return '';
      });
      mockCore.getBooleanInput.mockReturnValue(false);
      mockCore.getMultilineInput.mockReturnValue(['', '  ', 'file1.js', '']);

      const inputs = getInputs();

      expect(inputs.files).toEqual(['file1.js']);
    });
  });
});
```

### Action Logic Tests

```typescript
// __tests__/action.test.ts
import * as core from '@actions/core';
import * as github from '@actions/github';
import { run } from '../src/action';
import * as input from '../src/input';
import * as utils from '../src/utils';

jest.mock('@actions/core');
jest.mock('@actions/github');
jest.mock('../src/input');
jest.mock('../src/utils');

const mockCore = core as jest.Mocked<typeof core>;
const mockGithub = github as jest.Mocked<typeof github>;
const mockInput = input as jest.Mocked<typeof input>;
const mockUtils = utils as jest.Mocked<typeof utils>;

describe('Action', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Default mocks
    mockInput.getInputs.mockReturnValue({
      token: 'ghp_test',
      configPath: '.github/config.yml',
      timeout: 300,
      dryRun: false,
      files: ['test.js']
    });

    mockGithub.getOctokit.mockReturnValue({} as any);

    mockUtils.performWork.mockResolvedValue({
      status: 'success',
      details: { processed: 1 }
    });
  });

  it('should complete successfully', async () => {
    await run();

    expect(mockCore.setOutput).toHaveBeenCalledWith('result', 'success');
    expect(mockCore.setOutput).toHaveBeenCalledWith(
      'details',
      JSON.stringify({ processed: 1 })
    );
    expect(mockCore.exportVariable).toHaveBeenCalledWith('ACTION_RESULT', 'success');
    expect(mockCore.setFailed).not.toHaveBeenCalled();
  });

  it('should handle dry run mode', async () => {
    mockInput.getInputs.mockReturnValue({
      token: 'ghp_test',
      configPath: '.github/config.yml',
      timeout: 300,
      dryRun: true,
      files: ['test.js']
    });

    mockUtils.performWork.mockResolvedValue({
      status: 'skipped',
      details: { reason: 'dry-run' }
    });

    await run();

    expect(mockCore.setOutput).toHaveBeenCalledWith('result', 'skipped');
  });

  it('should fail gracefully on error', async () => {
    const error = new Error('Test error');
    mockUtils.performWork.mockRejectedValue(error);

    await expect(run()).rejects.toThrow('Test error');
  });
});
```

### Utility Function Tests

```typescript
// __tests__/utils.test.ts
import * as github from '@actions/github';
import { performWork, validateConfig } from '../src/utils';
import { ActionInputs } from '../src/input';

jest.mock('@actions/github');

describe('Utils', () => {
  const mockOctokit = {
    rest: {
      repos: {
        get: jest.fn()
      }
    }
  } as any;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('performWork', () => {
    const inputs: ActionInputs = {
      token: 'ghp_test',
      configPath: '.github/config.yml',
      timeout: 300,
      dryRun: false,
      files: ['test.js']
    };

    it('should return success on normal operation', async () => {
      mockOctokit.rest.repos.get.mockResolvedValue({
        data: { name: 'test-repo' }
      });

      const result = await performWork(mockOctokit, inputs);

      expect(result).toEqual({
        status: 'success',
        details: {
          repoName: 'test-repo',
          filesProcessed: 1
        }
      });
    });

    it('should handle dry run mode', async () => {
      const dryRunInputs = { ...inputs, dryRun: true };

      const result = await performWork(mockOctokit, dryRunInputs);

      expect(result).toEqual({
        status: 'skipped',
        details: { reason: 'dry-run' }
      });
      expect(mockOctokit.rest.repos.get).not.toHaveBeenCalled();
    });

    it('should throw on API error', async () => {
      const error = new Error('API Error');
      mockOctokit.rest.repos.get.mockRejectedValue(error);

      await expect(performWork(mockOctokit, inputs)).rejects.toThrow('API Error');
    });
  });

  describe('validateConfig', () => {
    it('should validate valid config', () => {
      expect(validateConfig({ key: 'value' })).toBe(true);
      expect(validateConfig({})).toBe(true);
    });

    it('should reject invalid config', () => {
      expect(validateConfig(null)).toBe(false);
      expect(validateConfig(undefined)).toBe(false);
      expect(validateConfig('string')).toBe(false);
      expect(validateConfig(123)).toBe(false);
    });
  });
});
```

### Main Entry Point Tests

```typescript
// __tests__/main.test.ts
import * as core from '@actions/core';
import { main } from '../src/main';
import * as action from '../src/action';

jest.mock('@actions/core');
jest.mock('../src/action');

const mockCore = core as jest.Mocked<typeof core>;
const mockAction = action as jest.Mocked<typeof action>;

describe('Main entry point', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should complete successfully', async () => {
    mockAction.run.mockResolvedValue();

    await main();

    expect(mockAction.run).toHaveBeenCalledOnce();
    expect(mockCore.setFailed).not.toHaveBeenCalled();
  });

  it('should handle Error objects', async () => {
    const error = new Error('Test error');
    mockAction.run.mockRejectedValue(error);

    await main();

    expect(mockCore.setFailed).toHaveBeenCalledWith('Test error');
  });

  it('should handle non-Error objects', async () => {
    mockAction.run.mockRejectedValue('String error');

    await main();

    expect(mockCore.setFailed).toHaveBeenCalledWith('An unexpected error occurred');
  });
});
```

## Integration Testing

### Filesystem Integration

```typescript
// __tests__/integration.test.ts
import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { run } from '../src/action';

describe('Integration Tests', () => {
  let tempDir: string;

  beforeEach(async () => {
    // Create temporary directory for each test
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'action-test-'));
  });

  afterEach(async () => {
    // Clean up
    await fs.rm(tempDir, { recursive: true, force: true });
  });

  it('should process real files', async () => {
    // Setup test files
    const configFile = path.join(tempDir, 'config.yml');
    await fs.writeFile(configFile, 'key: value\n');

    const testFile = path.join(tempDir, 'test.js');
    await fs.writeFile(testFile, 'console.log("hello");\n');

    // Mock environment
    process.env.INPUT_TOKEN = 'ghp_1234567890abcdef1234567890abcdef12345678';
    process.env.INPUT_CONFIG_PATH = configFile;
    process.env.INPUT_FILES = testFile;
    process.env.INPUT_DRY_RUN = 'false';

    // Mock GitHub APIs
    jest.mock('@actions/github', () => ({
      context: {
        repo: { owner: 'test-owner', repo: 'test-repo' }
      },
      getOctokit: () => ({
        rest: {
          repos: {
            get: () => Promise.resolve({
              data: { name: 'test-repo' }
            })
          }
        }
      })
    }));

    // Run action
    await expect(run()).resolves.not.toThrow();
  });
});
```

### GitHub API Integration

```typescript
// __tests__/github-integration.test.ts
import { getOctokit } from '@actions/github';
import { performWork } from '../src/utils';

describe('GitHub API Integration', () => {
  // Only run these tests if we have a real token
  const token = process.env.GITHUB_TOKEN;
  const skipMessage = 'Skipping GitHub API tests (no GITHUB_TOKEN)';

  it('should interact with real GitHub API', async () => {
    if (!token) {
      console.log(skipMessage);
      return;
    }

    const octokit = getOctokit(token);
    const inputs = {
      token,
      configPath: '.github/config.yml',
      timeout: 300,
      dryRun: false,
      files: ['package.json']
    };

    // Test with a known public repository
    const result = await performWork(octokit, inputs);

    expect(result.status).toMatch(/success|skipped/);
    expect(result.details).toBeDefined();
  });
});
```

## Local E2E Testing with Act

### Act Configuration

```json
// .actrc
{
  "platform": "ubuntu-latest=node:20-buster-slim",
  "artifact-server-path": "/tmp/artifacts",
  "env-file": ".env.test"
}
```

### Test Environment

```bash
# .env.test
GITHUB_TOKEN=ghp_your_test_token_here
INPUT_CONFIG_PATH=__tests__/fixtures/config.yml
INPUT_DRY_RUN=true
```

### Act Test Commands

```bash
# Test the action locally
act -j test

# Test with specific event
act push -j test

# Test with custom input
act -j test -s GITHUB_TOKEN="$(gh auth token)" \
  --input token="$(gh auth token)" \
  --input config-path="test-config.yml"

# Debug mode
act -j test --verbose

# Test with custom workflow
act -W .github/workflows/test-local.yml
```

### Local Test Workflow

```yaml
# .github/workflows/test-local.yml
name: Local Test

on: push

jobs:
  test-local:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Test action
        uses: ./
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config-path: '__tests__/fixtures/config.yml'
          files: |
            package.json
            src/main.ts
          dry-run: true

      - name: Validate outputs
        run: |
          echo "Testing output validation..."
          # Add output validation logic
```

## GitHub E2E Testing

### Test Matrix Workflows

```yaml
# .github/workflows/test-matrix.yml
name: Test Matrix

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20]
        include:
          - os: ubuntu-latest
            test-type: 'full'
          - os: windows-latest
            test-type: 'basic'
          - os: macos-latest
            test-type: 'basic'

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - name: Test action
        id: test
        uses: ./
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          dry-run: true

      - name: Verify output
        shell: bash
        run: |
          if [ "${{ steps.test.outputs.result }}" != "skipped" ]; then
            echo "Expected 'skipped' in dry-run mode"
            exit 1
          fi
```

### Real Environment Tests

```yaml
# .github/workflows/integration.yml
name: Integration Tests

on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  real-test:
    runs-on: ubuntu-latest
    environment: testing

    steps:
      - uses: actions/checkout@v4

      - name: Test with real data
        uses: ./
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config-path: '.github/test-config.yml'
          dry-run: false

      - name: Verify real results
        run: |
          # Add verification logic for real execution
          echo "Verifying real test results..."
```

## Mock Strategies

### Core API Mocking

```typescript
// __tests__/mocks/core.ts
export const mockCore = {
  getInput: jest.fn(),
  getBooleanInput: jest.fn(),
  getMultilineInput: jest.fn(),
  setOutput: jest.fn(),
  setFailed: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
  warning: jest.fn(),
  error: jest.fn(),
  exportVariable: jest.fn(),
  group: jest.fn().mockImplementation(async (name: string, fn: () => Promise<void>) => {
    return await fn();
  })
};
```

### GitHub API Mocking

```typescript
// __tests__/mocks/github.ts
export const mockOctokit = {
  rest: {
    repos: {
      get: jest.fn().mockResolvedValue({
        data: { name: 'mock-repo', private: false }
      }),
      listLanguages: jest.fn().mockResolvedValue({
        data: { JavaScript: 1000, TypeScript: 2000 }
      })
    },
    issues: {
      createComment: jest.fn().mockResolvedValue({
        data: { id: 123, html_url: 'https://github.com/owner/repo/issues/1#issuecomment-123' }
      })
    }
  }
};

export const mockGithubContext = {
  repo: { owner: 'test-owner', repo: 'test-repo' },
  actor: 'test-actor',
  sha: 'abc123def456',
  ref: 'refs/heads/main',
  workflow: 'Test',
  job: 'test',
  runId: 123456,
  runNumber: 42,
  payload: {
    pull_request: {
      number: 1,
      title: 'Test PR'
    }
  }
};
```

## Test Data Management

### Fixtures

```typescript
// __tests__/fixtures/index.ts
export const testConfigs = {
  valid: {
    name: 'Test Config',
    settings: {
      timeout: 300,
      retries: 3
    }
  },
  invalid: {
    // Missing required fields
    settings: {}
  }
};

export const testEvents = {
  pullRequest: {
    number: 1,
    title: 'Test PR',
    body: 'Test description',
    head: { sha: 'abc123' },
    base: { sha: 'def456' }
  },
  push: {
    commits: [
      { message: 'feat: add new feature', id: 'abc123' }
    ]
  }
};
```

### Test Factories

```typescript
// __tests__/factories/inputs.ts
export function createTestInputs(overrides: Partial<ActionInputs> = {}): ActionInputs {
  return {
    token: 'ghp_1234567890abcdef1234567890abcdef12345678',
    configPath: '.github/config.yml',
    timeout: 300,
    dryRun: false,
    files: ['test.js'],
    ...overrides
  };
}

export function createMockOctokit(overrides: any = {}): any {
  return {
    rest: {
      repos: {
        get: jest.fn().mockResolvedValue({
          data: { name: 'test-repo' }
        })
      }
    },
    ...overrides
  };
}
```

## Test Coverage

### Coverage Configuration

```json
// package.json
{
  "scripts": {
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch",
    "test:ci": "jest --ci --coverage --watchAll=false"
  },
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.ts",
      "!src/**/*.d.ts",
      "!src/main.ts"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

### Coverage Reports

```bash
# Generate HTML coverage report
npm run test:coverage

# Check coverage without tests
npx jest --coverage --passWithNoTests

# Coverage for specific files
npx jest --coverage --collectCoverageFrom="src/utils.ts"
```

## Debugging Tests

### Debug Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Jest Tests",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/jest",
      "args": ["--runInBand"],
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen"
    },
    {
      "name": "Debug Specific Test",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/jest",
      "args": ["--runInBand", "${relativeFile}"],
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen"
    }
  ]
}
```

### Test Debugging Tips

```typescript
// Add debug output in tests
describe('Debug test', () => {
  it('should debug', () => {
    console.log('Debug info:', JSON.stringify(data, null, 2));

    // Use debugger
    debugger;

    // Add temporary assertions
    expect(true).toBe(true);
  });
});

// Run single test
// npm test -- --testNamePattern="should debug"

// Run with verbose output
// npm test -- --verbose

// Run in debug mode
// node --inspect-brk node_modules/.bin/jest --runInBand
```

## Cross-References

- [Project Setup](project-setup.md) - Initial testing configuration
- [Toolkit API Reference](toolkit-api.md) - APIs to mock in tests
- [Publishing Guide](publishing.md) - Release testing strategies
- [Build Tooling](build-tooling.md) - CI/CD test integration