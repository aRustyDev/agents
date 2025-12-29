---
name: lang-typescript-library-dev
description: TypeScript-specific library/package development patterns. Use when creating npm packages, configuring package.json exports, setting up tsconfig.json for libraries, generating declaration files, publishing to npm, or configuring ESM/CJS dual packages. Extends meta-library-dev with TypeScript tooling and ecosystem patterns.
---

# TypeScript Library Development

TypeScript-specific patterns for library/package development. This skill extends `meta-library-dev` with TypeScript tooling, module system configuration, and npm ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **TypeScript tooling**: tsconfig.json for libraries, declaration files, source maps
- **Package configuration**: package.json exports, ESM/CJS dual packages, bundling
- **npm ecosystem**: Publishing workflow, scoped packages, monorepos

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- TypeScript syntax/patterns - see `lang-typescript-patterns-dev`
- React component libraries - see frontend skills
- Node.js application development

---

## Quick Reference

| Task | Command |
|------|---------|
| New package | `npm init` or `pnpm init` |
| Build | `tsc` or bundler command |
| Test | `vitest` or `jest` |
| Lint | `eslint .` |
| Format | `prettier --write .` |
| Pack (dry run) | `npm pack --dry-run` |
| Publish | `npm publish` |
| Publish (scoped public) | `npm publish --access public` |

---

## Package.json Structure

### Required Fields for Publishing

```json
{
  "name": "my-library",
  "version": "1.0.0",
  "description": "A brief description of what this library does",
  "license": "MIT",
  "author": "Your Name <email@example.com>",
  "repository": {
    "type": "git",
    "url": "https://github.com/username/repo"
  },
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
  },
  "files": ["dist"],
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### Exports Field (Modern)

The `exports` field controls what can be imported:

```json
{
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    },
    "./utils": {
      "types": "./dist/utils.d.ts",
      "import": "./dist/utils.js",
      "require": "./dist/utils.cjs"
    },
    "./package.json": "./package.json"
  }
}
```

**Order matters**: `types` must come first for TypeScript resolution.

### Files Field

Control what gets published:

```json
{
  "files": [
    "dist",
    "!dist/**/*.test.*",
    "!dist/**/*.spec.*"
  ]
}
```

Always verify with `npm pack --dry-run`.

---

## tsconfig.json for Libraries

### Base Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],

    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,

    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,

    "outDir": "./dist",
    "rootDir": "./src",

    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "**/*.test.ts", "**/*.spec.ts"]
}
```

### Declaration Files

| Option | Purpose |
|--------|---------|
| `declaration: true` | Generate `.d.ts` files |
| `declarationMap: true` | Enable "Go to Definition" in source |
| `emitDeclarationOnly: true` | Only emit declarations (use with bundler) |
| `declarationDir` | Separate output for declarations |

### Module Systems

| Config | Output | Use Case |
|--------|--------|----------|
| `"module": "NodeNext"` | ESM with `.js` | Modern Node.js packages |
| `"module": "CommonJS"` | CJS with `.js` | Legacy Node.js |
| `"module": "ESNext"` | ESM | For bundlers |

---

## ESM/CJS Dual Package

### Strategy 1: Dual Build (Recommended)

Build both formats from TypeScript:

```json
{
  "scripts": {
    "build": "npm run build:esm && npm run build:cjs",
    "build:esm": "tsc -p tsconfig.esm.json",
    "build:cjs": "tsc -p tsconfig.cjs.json"
  }
}
```

**tsconfig.esm.json:**
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "module": "NodeNext",
    "outDir": "./dist/esm"
  }
}
```

**tsconfig.cjs.json:**
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "module": "CommonJS",
    "outDir": "./dist/cjs"
  }
}
```

### Strategy 2: Use a Bundler

Use tsup, unbuild, or rollup for simpler dual builds:

**tsup.config.ts:**
```typescript
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  clean: true,
  sourcemap: true,
});
```

**package.json scripts:**
```json
{
  "scripts": {
    "build": "tsup"
  }
}
```

### Strategy 3: ESM-Only (Simplest)

For modern packages, consider ESM-only:

```json
{
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    }
  }
}
```

---

## Public API Design

### Export Patterns

**Explicit Named Exports (Preferred):**
```typescript
// src/index.ts
export { parse, serialize } from './parser.js';
export { validate } from './validator.js';
export type { Config, Options, Result } from './types.js';
```

**Avoid Default Exports:**
```typescript
// Avoid: Harder to tree-shake, inconsistent naming
export default class Parser { }

// Prefer: Named exports
export class Parser { }
```

### Type Exports

**Use `export type` for type-only exports:**
```typescript
// Enables proper tree-shaking and prevents runtime import
export type { User, Config } from './types.js';

// Re-export with types
export { parseUser, type ParseOptions } from './parser.js';
```

### Barrel Files

**src/index.ts (public API):**
```typescript
// Public API - explicit exports
export { createClient } from './client.js';
export { parse, serialize } from './parser.js';
export type { ClientOptions, ParseResult } from './types.js';

// Do NOT re-export internal modules
// import './internal.js';  // Wrong
```

---

## Type Declaration Best Practices

### Provide Good Types

```typescript
// Good: Specific, useful types
export interface ClientOptions {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export function createClient(options: ClientOptions): Client;

// Avoid: Overly generic
export function createClient(options: object): unknown;
```

### Use Generics Appropriately

```typescript
// Good: Generic with constraints
export function parse<T extends Record<string, unknown>>(
  input: string,
  schema: Schema<T>
): T;

// Good: Infer return type
export function map<T, U>(
  items: T[],
  fn: (item: T) => U
): U[];
```

### Document with JSDoc

```typescript
/**
 * Parses a configuration string into a typed object.
 *
 * @param input - The configuration string to parse
 * @param options - Optional parsing options
 * @returns The parsed configuration object
 * @throws {ParseError} If the input is malformed
 *
 * @example
 * ```typescript
 * const config = parse('key=value', { strict: true });
 * console.log(config.key); // 'value'
 * ```
 */
export function parse<T>(input: string, options?: ParseOptions): T;
```

---

## Testing Libraries

### Vitest Configuration

**vitest.config.ts:**
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.test.ts', '**/*.d.ts'],
    },
  },
});
```

### Test File Organization

```
src/
├── parser.ts
├── parser.test.ts      # Unit tests next to source
├── validator.ts
├── validator.test.ts
└── __tests__/          # Or separate test directory
    └── integration.test.ts
```

### Type Testing

**Test that types work correctly:**
```typescript
import { expectTypeOf } from 'vitest';
import { parse } from './parser.js';

test('parse returns correct type', () => {
  const result = parse('{"name": "test"}');
  expectTypeOf(result).toEqualTypeOf<ParsedResult>();
});
```

---

## Monorepo Patterns

### pnpm Workspace

**pnpm-workspace.yaml:**
```yaml
packages:
  - 'packages/*'
```

### Package Structure

```
my-monorepo/
├── package.json
├── pnpm-workspace.yaml
├── tsconfig.json          # Base config
└── packages/
    ├── core/
    │   ├── package.json
    │   ├── tsconfig.json  # Extends base
    │   └── src/
    └── utils/
        ├── package.json
        ├── tsconfig.json
        └── src/
```

### Internal Dependencies

```json
{
  "name": "@myorg/app",
  "dependencies": {
    "@myorg/core": "workspace:*",
    "@myorg/utils": "workspace:*"
  }
}
```

### Project References

**Root tsconfig.json:**
```json
{
  "references": [
    { "path": "./packages/core" },
    { "path": "./packages/utils" }
  ]
}
```

**Package tsconfig.json:**
```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "composite": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "references": [
    { "path": "../utils" }
  ]
}
```

---

## Publishing to npm

### Pre-publish Checklist

- [ ] `npm run build` succeeds
- [ ] `npm run test` passes
- [ ] `npm run lint` passes
- [ ] Version bumped in package.json
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] `npm pack --dry-run` shows correct files
- [ ] Types are correctly generated
- [ ] Exports work: `node -e "import('my-lib')"`

### Publishing Commands

```bash
# Verify package contents
npm pack --dry-run

# Publish to npm
npm publish

# Publish scoped package as public
npm publish --access public

# Publish with tag (for pre-releases)
npm publish --tag beta
```

### Scoped Packages

```json
{
  "name": "@myorg/my-library",
  "publishConfig": {
    "access": "public"
  }
}
```

### Automation with Changesets

```bash
# Initialize changesets
npx changeset init

# Add a changeset
npx changeset

# Version packages
npx changeset version

# Publish
npx changeset publish
```

---

## Common Dependencies

### Build Tools

```json
{
  "devDependencies": {
    "typescript": "^5.0.0",
    "tsup": "^8.0.0",
    "@types/node": "^20.0.0"
  }
}
```

### Testing

```json
{
  "devDependencies": {
    "vitest": "^1.0.0",
    "@vitest/coverage-v8": "^1.0.0"
  }
}
```

### Linting/Formatting

```json
{
  "devDependencies": {
    "eslint": "^8.0.0",
    "typescript-eslint": "^7.0.0",
    "prettier": "^3.0.0"
  }
}
```

---

## Anti-Patterns

### 1. Missing Types Field

```json
// Bad: Types not specified
{
  "main": "./dist/index.js"
}

// Good: Types explicitly declared
{
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

### 2. Wrong Export Order

```json
// Bad: types not first
{
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  }
}

// Good: types first
{
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    }
  }
}
```

### 3. Publishing Source Files

```json
// Bad: Publishing everything
{
  "files": ["src", "dist"]
}

// Good: Only publish dist
{
  "files": ["dist"]
}
```

### 4. Missing Peer Dependencies

```json
// Bad: Bundling React in a React library
{
  "dependencies": {
    "react": "^18.0.0"
  }
}

// Good: Peer dependency
{
  "peerDependencies": {
    "react": "^18.0.0"
  }
}
```

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-typescript-patterns-dev` - TypeScript syntax and patterns
- [TypeScript Handbook: Publishing](https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html)
- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json)
- [Are The Types Wrong?](https://arethetypeswrong.github.io/) - Validate package types
