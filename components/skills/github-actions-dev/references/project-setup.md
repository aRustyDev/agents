# GitHub Actions Project Setup

Complete guide to setting up GitHub Actions development projects from scratch.

## Quick Start Templates

### Official Template (Recommended)

```bash
# Use GitHub's official TypeScript template
npx create-action my-action
cd my-action
npm install
npm run all
```

### Manual Setup

```bash
mkdir my-action && cd my-action
npm init -y
npm install @actions/core @actions/github @actions/exec @actions/io
npm install -D typescript @types/node @vercel/ncc jest @types/jest ts-jest
```

## Project Structure

```
my-action/
├── action.yml                 # Action metadata
├── src/
│   ├── main.ts               # Entry point
│   ├── input.ts              # Input validation
│   ├── action.ts             # Core logic
│   └── utils.ts              # Helper functions
├── dist/
│   └── index.js              # Bundled output (must commit)
├── __tests__/
│   ├── main.test.ts          # Unit tests
│   └── integration.test.ts   # Integration tests
├── .github/
│   └── workflows/
│       └── test.yml          # CI workflow
├── package.json
├── tsconfig.json
├── jest.config.js
├── .gitignore
├── README.md
└── LICENSE
```

## Configuration Files

### package.json

```json
{
  "name": "my-action",
  "version": "1.0.0",
  "description": "GitHub Action description",
  "main": "dist/index.js",
  "scripts": {
    "build": "ncc build src/main.ts -o dist --source-map --license licenses.txt",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts",
    "all": "npm run format && npm run lint && npm run build && npm test"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/owner/my-action.git"
  },
  "keywords": ["actions", "github"],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "@actions/core": "^1.10.1",
    "@actions/github": "^6.0.0",
    "@actions/exec": "^1.1.1",
    "@actions/io": "^1.1.3"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vercel/ncc": "^0.38.0",
    "eslint": "^8.0.0",
    "eslint-plugin-jest": "^27.0.0",
    "jest": "^29.0.0",
    "prettier": "^3.0.0",
    "ts-jest": "^29.0.0",
    "typescript": "^5.0.0"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "commonjs",
    "outDir": "./lib",
    "rootDir": "./src",
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictPropertyInitialization": true,
    "noImplicitReturns": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noUncheckedIndexedAccess": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["dist", "node_modules", "**/*.test.ts"]
}
```

### jest.config.js

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src/', '<rootDir>/__tests__/'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/main.ts' // Entry point usually just calls run()
  ],
  coverageReporters: ['text', 'lcov', 'html'],
  coverageDirectory: 'coverage',
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true
};
```

### .eslintrc.js

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'jest'],
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:jest/recommended'
  ],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module'
  },
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-function-return-type': 'error',
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/prefer-optional-chain': 'error',
    'prefer-const': 'error',
    'no-var': 'error'
  },
  env: {
    node: true,
    es2022: true,
    jest: true
  }
};
```

### .prettierrc

```json
{
  "semi": true,
  "trailingComma": "none",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

### .gitignore

```gitignore
# Dependencies
node_modules/

# TypeScript build outputs
lib/
*.tsbuildinfo

# Coverage reports
coverage/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Temporary folders
tmp/
temp/

# DON'T ignore dist/ - it must be committed for JavaScript actions!
# dist/  ← This line should be commented out or removed
```

## Source Code Templates

### src/main.ts (Entry Point)

```typescript
import * as core from '@actions/core';
import { run } from './action';

// Entry point for the action
async function main(): Promise<void> {
  try {
    await run();
  } catch (error) {
    // Fail the action with an error message
    if (error instanceof Error) {
      core.setFailed(error.message);
    } else {
      core.setFailed('An unexpected error occurred');
    }
  }
}

// Don't call main() directly if we're in test mode
if (require.main === module) {
  main();
}

export { main };
```

### src/input.ts (Input Validation)

```typescript
import * as core from '@actions/core';

export interface ActionInputs {
  token: string;
  configPath: string;
  timeout: number;
  dryRun: boolean;
  files: string[];
}

export function getInputs(): ActionInputs {
  const token = core.getInput('token', { required: true });
  if (!token.match(/^gh[ps]_[a-zA-Z0-9]{36,255}$/)) {
    throw new Error('Invalid GitHub token format');
  }

  const configPath = core.getInput('config-path') || '.github/config.yml';

  const timeoutStr = core.getInput('timeout') || '300';
  const timeout = parseInt(timeoutStr, 10);
  if (isNaN(timeout) || timeout < 1 || timeout > 3600) {
    throw new Error('Timeout must be between 1 and 3600 seconds');
  }

  const dryRun = core.getBooleanInput('dry-run');

  const files = core
    .getMultilineInput('files')
    .filter(f => f.trim().length > 0);

  return {
    token,
    configPath,
    timeout,
    dryRun,
    files
  };
}
```

### src/action.ts (Core Logic)

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';
import { getInputs, ActionInputs } from './input';
import { performWork } from './utils';

export async function run(): Promise<void> {
  const inputs = getInputs();

  core.info(`Starting action with config: ${inputs.configPath}`);
  core.debug(`Dry run mode: ${inputs.dryRun}`);

  // Get GitHub context
  const { owner, repo } = github.context.repo;
  const octokit = github.getOctokit(inputs.token);

  // Perform the main work
  await core.group('Performing main action', async () => {
    const result = await performWork(octokit, inputs);

    // Set outputs
    core.setOutput('result', result.status);
    core.setOutput('details', JSON.stringify(result.details));

    // Export variables for subsequent steps
    core.exportVariable('ACTION_RESULT', result.status);

    core.info(`Action completed with result: ${result.status}`);
  });
}
```

### src/utils.ts (Helper Functions)

```typescript
import * as core from '@actions/core';
import { getOctokit } from '@actions/github';
import { ActionInputs } from './input';

export interface ActionResult {
  status: 'success' | 'failure' | 'skipped';
  details: Record<string, unknown>;
}

export async function performWork(
  octokit: ReturnType<typeof getOctokit>,
  inputs: ActionInputs
): Promise<ActionResult> {
  core.debug('Starting work with inputs');

  if (inputs.dryRun) {
    core.info('Dry run mode - skipping actual work');
    return {
      status: 'skipped',
      details: { reason: 'dry-run' }
    };
  }

  try {
    // Perform actual work here
    core.info('Performing actual work...');

    // Example API call
    const { data: repo } = await octokit.rest.repos.get({
      owner: github.context.repo.owner,
      repo: github.context.repo.repo
    });

    return {
      status: 'success',
      details: {
        repoName: repo.name,
        filesProcessed: inputs.files.length
      }
    };
  } catch (error) {
    core.error(`Work failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    throw error;
  }
}

export function validateConfig(config: unknown): boolean {
  // Add configuration validation logic
  return typeof config === 'object' && config !== null;
}
```

## CI Workflow Setup

### .github/workflows/test.yml

```yaml
name: Test Action

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18, 20]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Test action
        id: test
        uses: ./
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config-path: '__tests__/fixtures/config.yml'
          dry-run: true

      - name: Verify output
        run: |
          echo "Result: ${{ steps.test.outputs.result }}"
          if [ "${{ steps.test.outputs.result }}" != "skipped" ]; then
            echo "Expected 'skipped' in dry-run mode"
            exit 1
          fi

  integration:
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Test action (real run)
        uses: ./
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          dry-run: false
```

### .github/workflows/release.yml

```yaml
name: Release

on:
  release:
    types: [published]

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run all

      - name: Update major version tag
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          MAJOR=${VERSION%%.*}

          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          # Update or create major version tag
          git tag -fa "v$MAJOR" -m "Update v$MAJOR tag to $VERSION"
          git push origin "v$MAJOR" --force
```

## Common Setup Issues

### Bundle Size

The `dist/` folder must be committed but can get large:

```bash
# Check bundle size
ls -la dist/
du -h dist/

# Optimize bundle
npm run build -- --minify

# Analyze what's in the bundle
npx ncc build src/main.ts --source-map --stats-out stats.json
```

### TypeScript Compilation

```bash
# Check TypeScript compilation
npx tsc --noEmit

# Watch mode during development
npx tsc --watch --noEmit
```

### Testing Setup

```bash
# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- main.test.ts

# Run tests in watch mode
npm test -- --watch
```

## Development Workflow

1. **Initial Setup**
   ```bash
   npx create-action my-action
   cd my-action
   ```

2. **Development Cycle**
   ```bash
   # Make changes to src/
   npm run build     # Bundle for testing
   npm test          # Run test suite
   npm run all       # Full check (format, lint, build, test)
   ```

3. **Testing**
   ```bash
   # Local testing with act
   act -j test -s GITHUB_TOKEN="$(gh auth token)"

   # Debug action
   act -j test --verbose
   ```

4. **Release**
   ```bash
   # Commit dist/ changes
   git add dist/
   git commit -m "Build for release"

   # Create and push tag
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

## Cross-References

- [Action Metadata](action-metadata.md) - Complete action.yml reference
- [Toolkit API Reference](toolkit-api.md) - Core action APIs
- [Testing Guide](testing.md) - Comprehensive testing strategies
- [Publishing Guide](publishing.md) - Marketplace publication