#!/usr/bin/env python3
"""
Initialize a new GitHub Action project with TypeScript.

Usage:
    python3 scripts/init-action.py <action-name> [--docker] [--composite]

Examples:
    python3 scripts/init-action.py my-action
    python3 scripts/init-action.py my-docker-action --docker
    python3 scripts/init-action.py my-composite-action --composite
"""

import argparse
import sys
from pathlib import Path


ACTION_YML_TS = '''name: '{name}'
description: 'Description of what this action does'
author: 'Your Name'

branding:
  icon: 'check-circle'
  color: 'green'

inputs:
  token:
    description: 'GitHub token'
    required: true
    default: ${{{{ github.token }}}}

outputs:
  result:
    description: 'Action result'

runs:
  using: 'node20'
  main: 'dist/index.js'
'''

ACTION_YML_DOCKER = '''name: '{name}'
description: 'Description of what this action does'
author: 'Your Name'

branding:
  icon: 'box'
  color: 'blue'

inputs:
  args:
    description: 'Arguments to pass'
    required: false

runs:
  using: 'docker'
  image: 'Dockerfile'
'''

ACTION_YML_COMPOSITE = '''name: '{name}'
description: 'Description of what this action does'
author: 'Your Name'

inputs:
  working-directory:
    description: 'Working directory'
    default: '.'

outputs:
  result:
    description: 'Action result'
    value: ${{{{ steps.run.outputs.result }}}}

runs:
  using: 'composite'
  steps:
    - id: run
      run: echo "result=success" >> $GITHUB_OUTPUT
      shell: bash
      working-directory: ${{{{ inputs.working-directory }}}}
'''

MAIN_TS = '''import * as core from '@actions/core';
import * as github from '@actions/github';

async function run(): Promise<void> {
  try {
    const token = core.getInput('token', { required: true });

    core.info(`Running on ${{github.context.repo.owner}}/${{github.context.repo.repo}}`);

    // TODO: Implement action logic

    core.setOutput('result', 'success');
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message);
    }
  }
}

run();
'''

MAIN_TEST_TS = '''import * as core from '@actions/core';
import * as github from '@actions/github';

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
'''

PACKAGE_JSON = '''{
  "name": "%s",
  "version": "1.0.0",
  "description": "GitHub Action",
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
    "@typescript-eslint/eslint-plugin": "^7.0.0",
    "@typescript-eslint/parser": "^7.0.0",
    "@vercel/ncc": "^0.38.1",
    "eslint": "^8.57.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.2",
    "typescript": "^5.3.3"
  }
}
'''

TSCONFIG_JSON = '''{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./lib",
    "rootDir": "./src",
    "strict": true,
    "noImplicitAny": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true
  },
  "exclude": ["node_modules", "dist", "__tests__"]
}
'''

JEST_CONFIG = '''module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.test.ts'],
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
'''

DOCKERFILE = '''FROM node:20-alpine

LABEL maintainer="Your Name <email@example.com>"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
'''

ENTRYPOINT_SH = '''#!/bin/sh -l

# Inputs are environment variables: INPUT_<NAME> (uppercase)
echo "Args: $INPUT_ARGS"

# Do work here...

# Set outputs
echo "result=success" >> $GITHUB_OUTPUT
'''

GITIGNORE = '''node_modules/
lib/
coverage/
*.log
.DS_Store
'''

README_MD = '''# {name}

Description of what this action does.

## Usage

```yaml
- uses: owner/{name}@v1
  with:
    token: ${{{{ secrets.GITHUB_TOKEN }}}}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `token` | GitHub token | Yes | `${{{{ github.token }}}}` |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | The action result |

## Development

```bash
npm install
npm run build
npm test
```

## License

MIT
'''


def create_typescript_action(name: str, project_path: Path) -> None:
    """Create a TypeScript-based action."""
    # Create directories
    (project_path / 'src').mkdir()
    (project_path / '__tests__').mkdir()
    (project_path / 'dist').mkdir()

    # Write files
    (project_path / 'action.yml').write_text(ACTION_YML_TS.format(name=name))
    (project_path / 'src' / 'main.ts').write_text(MAIN_TS)
    (project_path / '__tests__' / 'main.test.ts').write_text(MAIN_TEST_TS)
    (project_path / 'package.json').write_text(PACKAGE_JSON % name)
    (project_path / 'tsconfig.json').write_text(TSCONFIG_JSON)
    (project_path / 'jest.config.js').write_text(JEST_CONFIG)
    (project_path / '.gitignore').write_text(GITIGNORE)
    (project_path / 'README.md').write_text(README_MD.format(name=name))

    # Create placeholder dist/index.js
    (project_path / 'dist' / 'index.js').write_text('// Run npm run build to generate\n')


def create_docker_action(name: str, project_path: Path) -> None:
    """Create a Docker-based action."""
    (project_path / 'action.yml').write_text(ACTION_YML_DOCKER.format(name=name))
    (project_path / 'Dockerfile').write_text(DOCKERFILE)
    (project_path / 'entrypoint.sh').write_text(ENTRYPOINT_SH)
    (project_path / '.gitignore').write_text(GITIGNORE)
    (project_path / 'README.md').write_text(README_MD.format(name=name))


def create_composite_action(name: str, project_path: Path) -> None:
    """Create a composite action."""
    (project_path / 'action.yml').write_text(ACTION_YML_COMPOSITE.format(name=name))
    (project_path / '.gitignore').write_text(GITIGNORE)
    (project_path / 'README.md').write_text(README_MD.format(name=name))


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Initialize a new GitHub Action project'
    )
    parser.add_argument('name', help='Action name (lowercase, hyphenated)')
    parser.add_argument('--docker', action='store_true', help='Create Docker action')
    parser.add_argument('--composite', action='store_true', help='Create composite action')

    args = parser.parse_args()

    if args.docker and args.composite:
        print("Error: Cannot specify both --docker and --composite", file=sys.stderr)
        return 1

    project_path = Path(args.name)

    if project_path.exists():
        print(f"Error: Directory '{args.name}' already exists", file=sys.stderr)
        return 1

    project_path.mkdir()

    if args.docker:
        create_docker_action(args.name, project_path)
        action_type = "Docker"
    elif args.composite:
        create_composite_action(args.name, project_path)
        action_type = "Composite"
    else:
        create_typescript_action(args.name, project_path)
        action_type = "TypeScript"

    print(f"\n✅ Created {action_type} action: {args.name}")
    print(f"\nNext steps:")
    print(f"  cd {args.name}")

    if not args.docker and not args.composite:
        print("  npm install")
        print("  npm run build")
        print("  npm test")

    print(f"\nTo test locally:")
    print(f"  act -j test")

    return 0


if __name__ == '__main__':
    sys.exit(main())
