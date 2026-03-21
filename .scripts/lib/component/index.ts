/**
 * Universal component model for the AI Context Library.
 *
 * Re-exports core types, pagination helpers, and the ComponentManager.
 * Providers are imported directly from their modules — not re-exported
 * here to keep the barrel lightweight.
 *
 * @example
 * ```typescript
 * import { ComponentManager, type Component } from './component'
 * import { LocalProvider } from './component/provider-local'
 * import { SmitheryProvider } from './component/provider-smithery'
 * ```
 */

export { ComponentManager } from './manager'
export * from './pagination'
export * from './types'
