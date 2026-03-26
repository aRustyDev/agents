/**
 * Dependency injection interface for skill operations.
 *
 * The SDK does not directly depend on CLI skill modules. Instead, the CLI
 * provides implementations of this interface when constructing a
 * LocalSkillProvider, allowing the SDK to remain decoupled from filesystem
 * and CLI-specific logic.
 */

export interface SkillOperations {
  list(opts: { cwd?: string; agent?: string }): Promise<{ ok: boolean; skills: any[] }>
  add(source: string, opts: any): Promise<any>
  remove(names: string[], opts: any): Promise<any[]>
  info(name: string, opts: any): Promise<any>
}
