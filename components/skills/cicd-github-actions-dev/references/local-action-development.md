# Local Action Development Reference

Comprehensive guide for developing GitHub Actions locally within projects before publishing to aRustyDev/gha.

## Development Workflow

### 1. Create Needs Issue

Create tracking issue in arustydev/gha when no suitable action exists:

```bash
gh issue create --repo arustydev/gha \
  --title "[ACTION] Need <action-name>" \
  --body "## Use Case
<describe the need>

## Proposed Solution
<high-level approach>

## Initial Development
Will develop locally in: <project-name>"
```

### 2. Local Project Structure

Set up action development within your project:

```
.github/
└── actions/
    └── my-action/
        ├── action.yml
        ├── package.json
        ├── tsconfig.json
        ├── jest.config.js
        ├── .gitignore
        └── src/
            ├── index.ts
            └── action.test.ts
```

### 3. Action Metadata (action.yml)

```yaml
name: 'My Action'
description: 'Clear description of what this action does'
branding:
  icon: 'tool'  # https://feathericons.com/
  color: 'blue'

inputs:
  required-input:
    description: 'Required input parameter'
    required: true
  optional-input:
    description: 'Optional parameter with default'
    required: false
    default: 'default-value'

outputs:
  result:
    description: 'Output from the action'

runs:
  using: 'node20'
  main: 'dist/index.js'
```

### 4. TypeScript Implementation

**package.json:**
```json
{
  "name": "my-action",
  "version": "1.0.0",
  "main": "dist/index.js",
  "scripts": {
    "build": "ncc build src/index.ts -o dist --source-map",
    "test": "jest",
    "package": "npm run build && npm test"
  },
  "dependencies": {
    "@actions/core": "^1.10.1",
    "@actions/github": "^6.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@vercel/ncc": "^0.38.1",
    "jest": "^29.7.0",
    "typescript": "^5.3.2"
  }
}
```

**src/index.ts:**
```typescript
import * as core from '@actions/core'
import * as github from '@actions/github'

interface ActionInputs {
  requiredInput: string
  optionalInput: string
}

function getInputs(): ActionInputs {
  return {
    requiredInput: core.getInput('required-input', { required: true }),
    optionalInput: core.getInput('optional-input') || 'default-value'
  }
}

async function run(): Promise<void> {
  try {
    const inputs = getInputs()

    core.info(`Processing with required input: ${inputs.requiredInput}`)
    core.info(`Optional input: ${inputs.optionalInput}`)

    // Action logic here
    const result = await processAction(inputs)

    // Set outputs
    core.setOutput('result', result)

    core.info('Action completed successfully')
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error)
    core.setFailed(`Action failed: ${errorMessage}`)
  }
}

async function processAction(inputs: ActionInputs): Promise<string> {
  // Your action logic implementation
  core.info('Executing action logic...')

  // Example: work with GitHub context
  const context = github.context
  core.info(`Repository: ${context.repo.owner}/${context.repo.repo}`)
  core.info(`Event: ${context.eventName}`)

  return `Processed: ${inputs.requiredInput}`
}

// Export for testing
export { run, getInputs, processAction }

// Run the action if not being imported
if (require.main === module) {
  run()
}
```

### 5. Testing Strategy

**src/action.test.ts:**
```typescript
import * as core from '@actions/core'
import * as github from '@actions/github'
import { run, getInputs, processAction } from './index'

// Mock @actions/core
jest.mock('@actions/core')
const mockCore = core as jest.Mocked<typeof core>

// Mock @actions/github
jest.mock('@actions/github', () => ({
  context: {
    repo: { owner: 'test-owner', repo: 'test-repo' },
    eventName: 'push'
  }
}))

describe('My Action', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('getInputs', () => {
    it('should get required input', () => {
      mockCore.getInput.mockImplementation((name: string) => {
        switch (name) {
          case 'required-input':
            return 'test-value'
          case 'optional-input':
            return ''
          default:
            return ''
        }
      })

      const inputs = getInputs()

      expect(inputs.requiredInput).toBe('test-value')
      expect(inputs.optionalInput).toBe('default-value')
    })

    it('should use custom optional input', () => {
      mockCore.getInput.mockImplementation((name: string) => {
        switch (name) {
          case 'required-input':
            return 'test-value'
          case 'optional-input':
            return 'custom-value'
          default:
            return ''
        }
      })

      const inputs = getInputs()

      expect(inputs.optionalInput).toBe('custom-value')
    })
  })

  describe('processAction', () => {
    it('should process inputs correctly', async () => {
      const inputs = {
        requiredInput: 'test-input',
        optionalInput: 'test-optional'
      }

      const result = await processAction(inputs)

      expect(result).toBe('Processed: test-input')
      expect(mockCore.info).toHaveBeenCalledWith('Executing action logic...')
    })
  })

  describe('run', () => {
    it('should complete successfully', async () => {
      mockCore.getInput.mockImplementation((name: string) => {
        switch (name) {
          case 'required-input':
            return 'test-value'
          default:
            return ''
        }
      })

      await run()

      expect(mockCore.setOutput).toHaveBeenCalledWith('result', 'Processed: test-value')
      expect(mockCore.info).toHaveBeenCalledWith('Action completed successfully')
    })

    it('should handle errors gracefully', async () => {
      mockCore.getInput.mockImplementation(() => {
        throw new Error('Input error')
      })

      await run()

      expect(mockCore.setFailed).toHaveBeenCalledWith('Action failed: Input error')
    })
  })
})
```

**jest.config.js:**
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.test.ts',
    '!src/**/*.d.ts'
  ]
}
```

### 6. Build Configuration

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**.gitignore:**
```
node_modules/
dist/
coverage/
*.log
.env
```

### 7. Development Commands

```bash
# Install dependencies
npm install

# Build the action
npm run build

# Run tests
npm test

# Package for distribution
npm run package
```

### 8. Local Testing in Workflow

```yaml
name: Test Local Action

on: [push, pull_request]

jobs:
  test-action:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Build the action
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: .github/actions/my-action/package-lock.json

      - name: Install action dependencies
        working-directory: .github/actions/my-action
        run: npm ci

      - name: Build action
        working-directory: .github/actions/my-action
        run: npm run build

      # Test the action
      - name: Test action
        id: test-action
        uses: ./.github/actions/my-action
        with:
          required-input: 'test-value'
          optional-input: 'custom-value'

      - name: Verify action output
        run: |
          echo "Action output: ${{ steps.test-action.outputs.result }}"
```

### 9. Migration to aRustyDev/gha

When the action is complete and tested:

**1. Copy to gha repository:**
```bash
# Clone gha repo if not already local
git clone https://github.com/arustydev/gha.git ~/repos/gha

# Copy action directory
cp -r .github/actions/my-action ~/repos/gha/actions/

# Navigate to gha repo
cd ~/repos/gha
```

**2. Create feature branch:**
```bash
git checkout -b feat/add-my-action
git add actions/my-action
git commit -m "feat(action): add my-action

- Implements functionality for <use case>
- Developed and tested in <project-name>
- Closes #<issue-number>"
```

**3. Create pull request:**
```bash
git push -u origin feat/add-my-action
gh pr create --title "feat(action): add my-action" \
  --body "## Summary
Adds my-action for <purpose>

## Development
- Developed locally in: <project-name>
- Tests passing: ✅
- Documentation complete: ✅

## Closes
Closes #<issue-number>"
```

**4. Update original project after merge:**
```yaml
# Replace local action with published version
steps:
  - uses: arustydev/gha/my-action@v1
    with:
      required-input: 'value'
```

Remove the local `.github/actions/my-action/` directory.

### 10. Advanced Patterns

#### Composite Actions

For shell-based actions:

```yaml
# action.yml
name: 'Composite Action'
description: 'Runs multiple commands'
inputs:
  target:
    description: 'Target directory'
    required: true

runs:
  using: 'composite'
  steps:
    - name: Setup
      shell: bash
      run: |
        echo "Setting up action in ${{ inputs.target }}"

    - name: Process
      shell: bash
      run: |
        cd "${{ inputs.target }}"
        # Action logic here
```

#### Docker Actions

For containerized actions:

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .

ENTRYPOINT ["node", "/app/dist/index.js"]
```

```yaml
# action.yml
name: 'Docker Action'
description: 'Runs in container'

runs:
  using: 'docker'
  image: 'Dockerfile'
```

## Best Practices

### Error Handling

```typescript
async function safeOperation(): Promise<void> {
  try {
    // Operation logic
  } catch (error) {
    if (error instanceof Error) {
      core.error(`Operation failed: ${error.message}`)
      throw error
    }
    throw new Error(`Unknown error: ${String(error)}`)
  }
}
```

### Input Validation

```typescript
function validateInputs(inputs: ActionInputs): void {
  if (!inputs.requiredInput.trim()) {
    throw new Error('Required input cannot be empty')
  }

  if (!/^[a-zA-Z0-9-_]+$/.test(inputs.requiredInput)) {
    throw new Error('Required input contains invalid characters')
  }
}
```

### Logging Best Practices

```typescript
// Use appropriate log levels
core.debug('Debug information')
core.info('General information')
core.notice('Important notice')
core.warning('Warning message')
core.error('Error message')

// Group related logs
core.startGroup('Processing files')
// ... processing logic ...
core.endGroup()
```

## Cross-References

- [Action Metadata Syntax](https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions)
- [Actions Toolkit](https://github.com/actions/toolkit)
- [Action Selection Reference](action-selection.md)