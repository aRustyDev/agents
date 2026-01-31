# GitHub Actions Build Tooling

Complete guide to TypeScript compilation, bundling, and CI configuration for GitHub Actions.

## TypeScript Configuration

### tsconfig.json Options

```json
{
  "compilerOptions": {
    "target": "ES2022",                          // Modern JavaScript features
    "lib": ["ES2022"],                          // Standard library
    "module": "commonjs",                       // Required for @actions/* packages
    "outDir": "./lib",                          // Intermediate output
    "rootDir": "./src",                         // Source directory
    "moduleResolution": "node",                 // Node.js resolution
    "allowSyntheticDefaultImports": true,       // Import compatibility
    "esModuleInterop": true,                    // Module interop
    "resolveJsonModule": true,                  // Import JSON files
    "skipLibCheck": true,                       // Skip .d.ts checking
    "forceConsistentCasingInFileNames": true,   // Case sensitivity

    // Strict type checking
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictPropertyInitialization": true,
    "noImplicitReturns": true,
    "noImplicitThis": true,
    "alwaysStrict": true,

    // Additional checks
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noUncheckedIndexedAccess": true,
    "noFallthroughCasesInSwitch": true,

    // Emit options
    "declaration": true,                        // Generate .d.ts files
    "declarationMap": true,                     // Generate .d.ts.map files
    "sourceMap": true,                          // Generate source maps
    "removeComments": false,                    // Preserve comments in output

    // Experimental
    "experimentalDecorators": true,             // If using decorators
    "emitDecoratorMetadata": true               // If using reflect-metadata
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "lib",
    "**/*.test.ts",
    "**/*.spec.ts"
  ]
}
```

### TypeScript Build Scripts

```json
{
  "scripts": {
    "build:ts": "tsc",
    "build:ts:watch": "tsc --watch",
    "build:ts:clean": "tsc --build --clean",
    "type-check": "tsc --noEmit",
    "type-check:watch": "tsc --noEmit --watch"
  }
}
```

## Bundling with ncc

### Why Bundle?

GitHub Actions require a single entry point. Bundling:
- Eliminates `node_modules` dependency
- Reduces cold start time
- Simplifies distribution
- Enables tree shaking

### ncc Configuration

```json
{
  "scripts": {
    "build": "ncc build src/main.ts -o dist --source-map --license licenses.txt",
    "build:watch": "ncc build src/main.ts -o dist --source-map --license licenses.txt --watch",
    "build:minify": "ncc build src/main.ts -o dist --minify --license licenses.txt"
  }
}
```

### Advanced ncc Options

```bash
# Basic build
ncc build src/main.ts -o dist

# With source maps (recommended for debugging)
ncc build src/main.ts -o dist --source-map

# With license file generation
ncc build src/main.ts -o dist --license licenses.txt

# Minified build (for production)
ncc build src/main.ts -o dist --minify

# External dependencies (don't bundle)
ncc build src/main.ts -o dist --external aws-sdk

# Target specific Node.js version
ncc build src/main.ts -o dist --target es2020

# Generate stats
ncc build src/main.ts -o dist --stats-out stats.json

# Cache builds
ncc build src/main.ts -o dist --cache .ncc-cache
```

### Bundle Analysis

```bash
# Generate bundle statistics
ncc build src/main.ts --stats-out stats.json

# Analyze bundle size
du -h dist/index.js

# Check what's included
cat licenses.txt

# View stats
cat stats.json | jq '.modules | length'
cat stats.json | jq '.modules | sort_by(.size) | reverse | .[0:10]'
```

### Bundle Optimization

```typescript
// webpack.config.js (if using webpack instead of ncc)
module.exports = {
  target: 'node',
  entry: './src/main.ts',
  output: {
    filename: 'index.js',
    path: path.resolve(__dirname, 'dist')
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },
  resolve: {
    extensions: ['.ts', '.js']
  },
  optimization: {
    minimize: true
  },
  externals: {
    // Don't bundle large dependencies
    '@aws-sdk/client-s3': 'commonjs @aws-sdk/client-s3'
  }
};
```

## Package.json Scripts

### Complete Script Set

```json
{
  "scripts": {
    // Building
    "build": "npm run build:ts && npm run build:bundle",
    "build:ts": "tsc",
    "build:bundle": "ncc build lib/main.js -o dist --source-map --license licenses.txt",
    "build:watch": "concurrently \"npm run build:ts:watch\" \"npm run build:bundle:watch\"",
    "build:clean": "rm -rf lib dist",

    // Development
    "dev": "npm run build:watch",
    "type-check": "tsc --noEmit",

    // Testing
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --watchAll=false",

    // Linting & Formatting
    "lint": "eslint src/**/*.ts",
    "lint:fix": "eslint src/**/*.ts --fix",
    "format": "prettier --write src/**/*.ts",
    "format:check": "prettier --check src/**/*.ts",

    // Quality checks
    "check": "npm run format:check && npm run lint && npm run type-check",
    "fix": "npm run format && npm run lint:fix",

    // Full pipeline
    "all": "npm run fix && npm run build && npm test",
    "ci": "npm run check && npm run build && npm run test:ci",

    // Release
    "prepare": "npm run all",
    "prepublishOnly": "npm run build"
  }
}
```

### Concurrent Development

```bash
# Install concurrently for parallel tasks
npm install -D concurrently

# Watch both TypeScript and bundling
"dev": "concurrently \"tsc --watch\" \"ncc build lib/main.js -o dist --watch\""

# Multiple watchers
"dev:all": "concurrently -n \"TS,Bundle,Test\" \"tsc --watch\" \"ncc build lib/main.js -o dist --watch\" \"jest --watch\""
```

## ESLint Configuration

### .eslintrc.js

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'jest', 'import'],
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    '@typescript-eslint/recommended-requiring-type-checking',
    'plugin:jest/recommended',
    'plugin:import/recommended',
    'plugin:import/typescript'
  ],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    project: './tsconfig.json'
  },
  rules: {
    // TypeScript specific
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-function-return-type': 'error',
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/prefer-optional-chain': 'error',
    '@typescript-eslint/strict-boolean-expressions': 'error',

    // Import rules
    'import/order': ['error', {
      groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      'newlines-between': 'always'
    }],
    'import/no-unresolved': 'error',

    // General
    'prefer-const': 'error',
    'no-var': 'error',
    'no-console': 'warn',
    'eqeqeq': 'error',
    'no-eval': 'error',
    'no-implied-eval': 'error'
  },
  env: {
    node: true,
    es2022: true,
    jest: true
  },
  settings: {
    'import/resolver': {
      typescript: true,
      node: true
    }
  }
};
```

### ESLint Ignore

```bash
# .eslintignore
node_modules/
dist/
lib/
coverage/
*.min.js
```

## Prettier Configuration

### .prettierrc

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "quoteProps": "as-needed"
}
```

### .prettierignore

```bash
node_modules/
dist/
lib/
coverage/
package-lock.json
*.min.js
CHANGELOG.md
```

## Git Hooks with Husky

### Setup

```bash
# Install husky and lint-staged
npm install -D husky lint-staged

# Initialize husky
npx husky install

# Add prepare script
npm pkg set scripts.prepare="husky install"
```

### Pre-commit Hook

```bash
# .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

### Lint-staged Configuration

```json
{
  "lint-staged": {
    "src/**/*.{ts,tsx}": [
      "prettier --write",
      "eslint --fix",
      "git add"
    ],
    "*.{md,json,yml,yaml}": [
      "prettier --write",
      "git add"
    ]
  }
}
```

### Commit Message Hook

```bash
# .husky/commit-msg
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx commitlint --edit $1
```

```json
{
  "devDependencies": {
    "@commitlint/cli": "^17.0.0",
    "@commitlint/config-conventional": "^17.0.0"
  },
  "commitlint": {
    "extends": ["@commitlint/config-conventional"]
  }
}
```

## CI/CD Configuration

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

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

      - name: Type check
        run: npm run type-check

      - name: Lint
        run: npm run lint

      - name: Format check
        run: npm run format:check

      - name: Build
        run: npm run build

      - name: Test
        run: npm run test:ci

      - name: Upload coverage
        if: matrix.node-version == 20
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

      - name: Check dist is up to date
        run: |
          if [ -n "$(git status --porcelain dist/)" ]; then
            echo "dist/ is not up to date. Run 'npm run build' and commit changes."
            exit 1
          fi

  integration-test:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Test action
        uses: ./
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          dry-run: true
```

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    reviewers:
      - "your-username"
    commit-message:
      prefix: "deps"
      include: "scope"
```

## Build Optimization

### Bundle Size Optimization

```bash
# Analyze what's in the bundle
npx ncc build src/main.ts --stats-out stats.json
cat stats.json | jq '.modules | map({name: .name, size: .size}) | sort_by(.size) | reverse | .[0:20]'

# Use webpack-bundle-analyzer alternative for ncc
npm install -D source-map-explorer
npx source-map-explorer dist/index.js dist/index.js.map
```

### External Dependencies

```bash
# Don't bundle large dependencies
ncc build src/main.ts -o dist --external @aws-sdk/client-s3
ncc build src/main.ts -o dist --external sharp
```

### Tree Shaking

```typescript
// Use specific imports instead of barrel imports
// ❌ Bad: imports entire library
import * as _ from 'lodash';

// ✅ Good: imports only what's needed
import { get } from 'lodash/get';
import { isArray } from 'lodash/isArray';

// ❌ Bad: barrel import
import { someFunction } from './utils';

// ✅ Good: direct import
import { someFunction } from './utils/someFunction';
```

### Build Caching

```bash
# Cache TypeScript builds
"build:ts": "tsc --incremental"

# Cache ncc builds
"build:bundle": "ncc build src/main.ts -o dist --cache .ncc-cache"

# Cache in CI
- name: Cache TypeScript
  uses: actions/cache@v4
  with:
    path: |
      tsconfig.tsbuildinfo
      .ncc-cache
    key: ${{ runner.os }}-build-${{ hashFiles('package-lock.json') }}
```

## Development Tools

### VS Code Configuration

```json
// .vscode/settings.json
{
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "typescript.suggest.autoImports": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "files.exclude": {
    "dist": true,
    "lib": true,
    "coverage": true,
    "node_modules": true
  },
  "search.exclude": {
    "dist": true,
    "lib": true,
    "coverage": true
  }
}
```

### Recommended Extensions

```json
// .vscode/extensions.json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next",
    "orta.vscode-jest",
    "bradlc.vscode-tailwindcss",
    "github.vscode-github-actions"
  ]
}
```

### Debug Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Action",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/lib/main.js",
      "env": {
        "INPUT_TOKEN": "ghp_fake_token_for_debugging",
        "INPUT_CONFIG_PATH": ".github/config.yml",
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_ACTOR": "debug-user"
      },
      "outFiles": ["${workspaceFolder}/lib/**/*.js"],
      "sourceMaps": true
    }
  ]
}
```

## Performance Monitoring

### Build Time Analysis

```bash
# Time each step
"build:time": "npm run build:ts && time npm run build:bundle"

# Profile TypeScript compilation
"build:ts:profile": "tsc --generateTrace trace"

# Analyze trace
npx analyze-trace trace
```

### Bundle Size Monitoring

```yaml
# .github/workflows/bundle-size.yml
name: Bundle Size

on: [pull_request]

jobs:
  bundle-size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      - name: Check bundle size
        run: |
          SIZE=$(stat -f%z dist/index.js)
          echo "Bundle size: ${SIZE} bytes"
          if [ ${SIZE} -gt 1048576 ]; then  # 1MB
            echo "Bundle size too large!"
            exit 1
          fi
```

## Troubleshooting

### Common Build Issues

```bash
# TypeScript compilation errors
npx tsc --noEmit --pretty

# ESLint errors
npx eslint src/ --fix

# Bundle errors
DEBUG=ncc npx ncc build src/main.ts -o dist

# Module resolution issues
npm ls @actions/core
npm audit fix
```

### Debug Bundle Contents

```bash
# Extract and inspect bundle
mkdir -p debug-bundle
cd debug-bundle
node -e "console.log(require('../dist/index.js'))"

# Check for missing dependencies
node dist/index.js
```

## Cross-References

- [Project Setup](project-setup.md) - Initial build configuration
- [Testing Guide](testing.md) - CI/CD test integration
- [Publishing Guide](publishing.md) - Release build process
- [Toolkit API Reference](toolkit-api.md) - APIs affecting build size