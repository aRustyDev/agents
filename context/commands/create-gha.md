---
description: Create a new GitHub Action (TypeScript) with full project structure for local development
argument-hint: <action-name> [--type ts|docker|composite] [--no-issues]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(npm:*), Bash(gh:*), Bash(ls:*), Bash(cat:*), Glob, Grep, AskUserQuestion, TodoWrite
---

# Create GitHub Action

Create a new custom GitHub Action with proper structure, action.yml, and TypeScript scaffolding for local development and testing.

**This command creates GitHub Actions (reusable components called with `uses:`), NOT workflow YAML files.**

## Arguments

- `$1` - Action name (lowercase, hyphenated). Example: `setup-rust`, `label-pr`
- `--type` - Action type (optional):
  - `ts` (default): TypeScript/JavaScript with Node.js 20
  - `docker`: Container-based action
  - `composite`: YAML-based, orchestrates other actions
- `--no-issues` - Skip creating tracking issues

## Workflow

### Phase 1: Parse and Validate

**Use TodoWrite to track progress.**

1. **Parse action name from $1**:
   - Validate: lowercase, hyphenated
   - Pattern: `^[a-z][a-z0-9-]*[a-z0-9]$`
   - Convention: `verb-noun` (e.g., `setup-node`, `label-pr`, `deploy-cloudflare`)

2. **Parse flags**:
   - `--type`: Default to `ts`
   - `--no-issues`: Boolean, default false

3. **Determine local path**:
   ```
   .github/actions/<action-name>/
   ```

4. **Check if action exists locally**:
   - If directory exists, ask to overwrite or choose different name

### Phase 2: Create Directory Structure

#### TypeScript Action (default)

```bash
mkdir -p .github/actions/$ACTION_NAME/{src,__tests__,dist}
```

**Files to create:**

```
.github/actions/<action-name>/
├── action.yml           # Action metadata
├── src/
│   └── main.ts          # Entry point
├── __tests__/
│   └── main.test.ts     # Tests
├── dist/
│   └── index.js         # Bundled output (generated)
├── package.json
├── tsconfig.json
└── README.md
```

#### Docker Action

```
.github/actions/<action-name>/
├── action.yml
├── Dockerfile
├── entrypoint.sh
└── README.md
```

#### Composite Action

```
.github/actions/<action-name>/
├── action.yml           # Contains all steps
└── README.md
```

### Phase 3: Generate Files

#### 3.1 action.yml (TypeScript)

```yaml
name: '<Action Name>'
description: '<Brief description>'
author: 'aRustyDev'

branding:
  icon: 'check-circle'
  color: 'green'

inputs:
  token:
    description: 'GitHub token'
    required: false
    default: ${{ github.token }}

outputs:
  result:
    description: 'Action result'

runs:
  using: 'node20'
  main: 'dist/index.js'
```

#### 3.2 src/main.ts

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';

export async function run(): Promise<void> {
  try {
    const token = core.getInput('token');

    core.info(`Running on ${github.context.repo.owner}/${github.context.repo.repo}`);

    // TODO: Implement action logic

    core.setOutput('result', 'success');
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message);
    }
  }
}

run();
```

#### 3.3 package.json

```json
{
  "name": "<action-name>",
  "version": "1.0.0",
  "description": "GitHub Action: <description>",
  "main": "dist/index.js",
  "scripts": {
    "build": "ncc build src/main.ts -o dist --source-map --license licenses.txt",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "all": "npm run lint && npm run test && npm run build"
  },
  "dependencies": {
    "@actions/core": "^1.10.1",
    "@actions/github": "^6.0.0",
    "@actions/exec": "^1.1.1",
    "@actions/io": "^1.1.3"
  },
  "devDependencies": {
    "@types/jest": "^29.5.12",
    "@types/node": "^20.11.0",
    "@vercel/ncc": "^0.38.1",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.2",
    "typescript": "^5.3.3"
  }
}
```

#### 3.4 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./lib",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "exclude": ["node_modules", "dist", "__tests__"]
}
```

#### 3.5 __tests__/main.test.ts

```typescript
import * as core from '@actions/core';

jest.mock('@actions/core');
jest.mock('@actions/github');

describe('action', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('sets output on success', async () => {
    (core.getInput as jest.Mock).mockReturnValue('fake-token');

    const { run } = await import('../src/main');
    await run();

    expect(core.setOutput).toHaveBeenCalledWith('result', 'success');
  });
});
```

#### 3.6 README.md

```markdown
# <Action Name>

<Description>

## Usage

\`\`\`yaml
- uses: ./.github/actions/<action-name>
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
\`\`\`

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `token` | GitHub token | No | `${{ github.token }}` |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | Action result |

## Development

\`\`\`bash
cd .github/actions/<action-name>
npm install
npm run build
npm test
\`\`\`

## Local Testing

\`\`\`yaml
# .github/workflows/test-action.yml
name: Test Action
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/<action-name>
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
\`\`\`
```

### Phase 4: Initialize and Build

```bash
cd .github/actions/$ACTION_NAME
npm install
npm run build
```

### Phase 5: Create Tracking Issues

**Skip this phase if `--no-issues` is set.**

Create three issues to track development of the action:

#### 5.1 Implementation Issue

```bash
gh issue create \
  --title "feat(gha): implement \`$ACTION_NAME\` action" \
  --label "enhancement,github-action" \
  --body "$(cat <<'EOF'
## Summary
Implement the core logic for the `$ACTION_NAME` GitHub Action.

## Location
`.github/actions/$ACTION_NAME/`

## Tasks
- [ ] Define inputs in `action.yml`
- [ ] Define outputs in `action.yml`
- [ ] Implement main logic in `src/main.ts`
- [ ] Handle errors appropriately
- [ ] Add debug logging

## Acceptance Criteria
- Action runs without errors
- All inputs are validated
- Outputs are set correctly
- Errors are handled gracefully

## Related Issues
- Testing: #TEST_ISSUE_NUMBER
- Documentation: #DOCS_ISSUE_NUMBER
EOF
)"
```

#### 5.2 Testing Issue

```bash
gh issue create \
  --title "test(gha): add tests for \`$ACTION_NAME\` action" \
  --label "testing,github-action" \
  --body "$(cat <<'EOF'
## Summary
Add comprehensive tests for the `$ACTION_NAME` GitHub Action.

## Location
`.github/actions/$ACTION_NAME/__tests__/`

## Tasks
- [ ] Unit tests for main logic
- [ ] Mock @actions/core and @actions/github
- [ ] Test error handling
- [ ] Test edge cases
- [ ] Add integration test workflow

## Test Workflow
Create `.github/workflows/test-$ACTION_NAME.yml`:
```yaml
name: Test $ACTION_NAME
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/$ACTION_NAME
```

## Acceptance Criteria
- All unit tests pass
- Integration test workflow runs successfully
- Edge cases are covered

## Related Issues
- Implementation: #IMPL_ISSUE_NUMBER
- Documentation: #DOCS_ISSUE_NUMBER
EOF
)"
```

#### 5.3 Documentation Issue

```bash
gh issue create \
  --title "docs(gha): document \`$ACTION_NAME\` action" \
  --label "documentation,github-action" \
  --body "$(cat <<'EOF'
## Summary
Complete documentation for the `$ACTION_NAME` GitHub Action.

## Location
`.github/actions/$ACTION_NAME/README.md`

## Tasks
- [ ] Update action description in `action.yml`
- [ ] Document all inputs with examples
- [ ] Document all outputs
- [ ] Add usage examples
- [ ] Add troubleshooting section
- [ ] Configure branding (icon + color)

## README Sections
- Overview
- Usage
- Inputs (table)
- Outputs (table)
- Examples
- Development
- Troubleshooting

## Acceptance Criteria
- README is complete and accurate
- action.yml has description and branding
- Examples are tested and working

## Related Issues
- Implementation: #IMPL_ISSUE_NUMBER
- Testing: #TEST_ISSUE_NUMBER
EOF
)"
```

#### 5.4 Link Issues

After creating all three issues, update each with cross-references:

```bash
# Update implementation issue with related issue numbers
gh issue edit $IMPL_ISSUE --body "$(updated body with actual issue numbers)"

# Repeat for testing and documentation issues
```

#### 5.5 Child Issues for Problems

When problems arise during development, create child issues linked to the parent:

```bash
# Example: Bug found during implementation
gh issue create \
  --title "fix(gha): handle empty input in \`$ACTION_NAME\`" \
  --label "bug,github-action" \
  --body "$(cat <<'EOF'
## Parent Issue
Relates to #$IMPL_ISSUE

## Problem
<description of the problem>

## Solution
<proposed solution>
EOF
)"
```

**Child issue conventions:**
- Use appropriate prefix: `fix(gha):`, `refactor(gha):`, `perf(gha):`
- Always reference parent issue with "Relates to #N" or "Part of #N"
- Close child issues via PR, which contributes to parent completion
- Parent issue stays open until all children are resolved

**GitHub Projects integration** (if using):
- Add child issues to the same project as parent
- Use sub-issue relationships if available

### Phase 6: Report

```
## Action Created

| Field | Value |
|-------|-------|
| Action | `<action-name>` |
| Location | `.github/actions/<action-name>/` |
| Type | TypeScript |

**Tracking Issues:**
| Issue | Title |
|-------|-------|
| #$IMPL_ISSUE | feat(gha): implement `<action-name>` action |
| #$TEST_ISSUE | test(gha): add tests for `<action-name>` action |
| #$DOCS_ISSUE | docs(gha): document `<action-name>` action |

**Development workflow:**

1. Work on implementation (#$IMPL_ISSUE)
   - Implement logic in `src/main.ts`
   - Build: `npm run build`
2. Add tests (#$TEST_ISSUE)
   - Write unit tests
   - Create integration workflow
3. Complete documentation (#$DOCS_ISSUE)
   - Update README.md
   - Add branding to action.yml
4. Close issues via PRs
5. When ready to publish: `/promote-gha <action-name>`
```

## Docker Action Template

If `--type docker`:

**action.yml:**
```yaml
name: '<Action Name>'
description: '<Description>'
author: 'aRustyDev'

branding:
  icon: 'box'
  color: 'blue'

inputs:
  args:
    description: 'Arguments'
    required: false

runs:
  using: 'docker'
  image: 'Dockerfile'
```

**Dockerfile:**
```dockerfile
FROM node:20-alpine

LABEL maintainer="aRustyDev"
LABEL com.github.actions.name="<Action Name>"
LABEL com.github.actions.description="<Description>"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

**entrypoint.sh:**
```bash
#!/bin/sh -l

# Inputs are environment variables: INPUT_<NAME> (uppercase)
echo "Args: $INPUT_ARGS"

# Do work here...

echo "result=success" >> $GITHUB_OUTPUT
```

## Composite Action Template

If `--type composite`:

**action.yml:**
```yaml
name: '<Action Name>'
description: '<Description>'
author: 'aRustyDev'

inputs:
  working-directory:
    description: 'Working directory'
    default: '.'

outputs:
  result:
    description: 'Result'
    value: ${{ steps.run.outputs.result }}

runs:
  using: 'composite'
  steps:
    - id: run
      run: echo "result=success" >> $GITHUB_OUTPUT
      shell: bash
      working-directory: ${{ inputs.working-directory }}
```

## Integration with github-actions Skill

This command uses the `github-actions` skill for reference patterns. The skill provides:
- @actions/core and @actions/github API reference
- Testing patterns with Jest
- Publishing to Marketplace guidelines

## Examples

**Create a TypeScript action (with tracking issues):**
```
/create-gha setup-rust
```
Creates action + 3 tracking issues (implementation, testing, documentation)

**Create a Docker action:**
```
/create-gha my-docker-action --type docker
```

**Create a composite action:**
```
/create-gha my-composite --type composite
```

**Create without tracking issues:**
```
/create-gha quick-fix --no-issues
```
Scaffolds files only, no GitHub issues created

## Related Commands

- `/promote-gha` - Publish action to aRustyDev/gha via Issue+PR, optionally to Marketplace

## Notes

- Actions are created in `.github/actions/` for local development
- Test thoroughly before promoting to the central repository
- Use `/promote-gha` when ready to publish
