/**
 * @agents/core — Shared foundation for AI Context Library tools.
 *
 * Provides: Result monad, file I/O, config, output formatting,
 * component type system, git/GitHub integration, hashing.
 *
 * This barrel re-exports all public APIs. For tree-shaking or
 * smaller imports, use deep paths: `@agents/core/types`, etc.
 */

// Archive
export * from './archive'
// Note: symlink is re-exported via file-io, not directly
export * from './config'
export * from './file-io'
// Integration
export * from './git'
export * from './github'
export * from './hash'
export * from './runtime'
export * from './source-parser'
// Foundation
export * from './types'
export * from './uuid'
