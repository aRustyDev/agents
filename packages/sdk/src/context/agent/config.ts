/**
 * Portable agent configuration interface.
 *
 * Defines the shape of an agent's directory layout and capabilities.
 * The CLI provides a concrete implementation with 44+ agents;
 * SDK consumers can provide their own.
 */

/** Agent identifier type -- a string union in the CLI, generic string in SDK. */
export type AgentId = string

/** Configuration for a single AI coding agent. */
export interface AgentConfig {
  /** Machine identifier (e.g., 'claude-code', 'cursor'). */
  readonly name: string
  /** Human-readable display name. */
  readonly displayName: string
  /** Project-relative skills directory (no leading /). */
  readonly skillsDir: string
  /** Absolute path to the global (user-level) skills directory. */
  readonly globalSkillsDir: string
  /** Whether the agent supports the universal skill format. */
  readonly universal: boolean
  /** Returns true if the agent appears to be installed on this machine. */
  detectInstalled(): boolean
}

/**
 * Resolves agent configurations at runtime.
 *
 * The SDK defines this interface; the CLI provides the implementation
 * that knows about 44+ concrete agents and their filesystem paths.
 */
export interface AgentResolver {
  /** List all known agent configurations. */
  list(): AgentConfig[]
  /** Get a specific agent by identifier. Returns undefined if unknown. */
  get(name: string): AgentConfig | undefined
  /** List only agents detected as installed on this machine. */
  detectInstalled(): AgentConfig[]
  /** List agents that support the universal skill format. */
  getUniversal(): AgentConfig[]
  /**
   * Resolve the base skills directory for an agent.
   * @param name - Agent identifier
   * @param global - true for user-level, false for project-scope
   * @param cwd - Project working directory (used when global=false)
   */
  getBaseDir(name: string, global: boolean, cwd: string): string | undefined
}
