/**
 * Local agent provider for the Component system.
 *
 * Discovers agent definition `.md` files from `content/agents/` nested
 * category directories. Excludes application agents (directories containing
 * `pyproject.toml`), underscore-prefixed directories, and non-agent files
 * like `README.md` and `prompt.md`.
 */

import { existsSync } from 'node:fs'
import { readdir, readFile } from 'node:fs/promises'
import { basename, join, relative } from 'node:path'
import type { Result } from '@agents/core/types'
import { err, ok } from '@agents/core/types'
import { parseFrontmatter } from '../../context/frontmatter'
import type {
  Component,
  ComponentAddOptions,
  ComponentAddResult,
  ComponentProvider,
  ComponentType,
  PaginatedResult,
  ProviderCapabilities,
  PublishResult,
  RemoveResult,
  SearchParams,
} from '../../context/types'
import { SdkError } from '../../util/errors'
import { clampLimit, clampPage, emptyPage, paginateArray } from '../pagination'

const SUPPORTED_TYPES: readonly ComponentType[] = ['agent'] as const

/** Filenames to skip during discovery. */
const EXCLUDED_FILES = new Set(['README.md', 'prompt.md'])

export class LocalAgentProvider implements ComponentProvider {
  readonly id = 'local-agent'
  readonly displayName = 'Local Agents'
  readonly capabilities: ProviderCapabilities = {
    search: ['agent'],
    add: [],
    list: ['agent'],
    remove: [],
    publish: [],
    info: ['agent'],
    outdated: [],
    update: [],
  }

  private readonly agentsDir: string
  private readonly cwd: string

  constructor(cwd?: string) {
    this.cwd = cwd ?? process.cwd()
    this.agentsDir = join(this.cwd, 'content', 'agents')
  }

  // -------------------------------------------------------------------------
  // Discovery
  // -------------------------------------------------------------------------

  /**
   * Recursively walk the agents directory, applying exclusion rules,
   * parsing frontmatter, and mapping each `.md` file to a Component.
   */
  private async discoverAgents(): Promise<Component[]> {
    if (!existsSync(this.agentsDir)) return []

    const components: Component[] = []
    await this.walkDir(this.agentsDir, components)
    return components
  }

  /**
   * Recursive directory walker.
   *
   * For each directory entry:
   * - Skip directories starting with `_`
   * - Skip directories containing `pyproject.toml` (application agents)
   * - Skip non-`.md` files and excluded filenames
   * - Parse remaining `.md` files as agent definitions
   */
  private async walkDir(dir: string, components: Component[]): Promise<void> {
    let entries: Awaited<ReturnType<typeof readdir>>
    try {
      entries = await readdir(dir, { withFileTypes: true })
    } catch {
      return
    }

    for (const entry of entries) {
      const fullPath = join(dir, entry.name)

      if (entry.isDirectory()) {
        // Skip underscore-prefixed directories
        if (entry.name.startsWith('_')) continue

        // Skip application agent directories (contain pyproject.toml)
        if (existsSync(join(fullPath, 'pyproject.toml'))) continue

        await this.walkDir(fullPath, components)
        continue
      }

      if (!entry.isFile()) continue

      // Only process .md files
      if (!entry.name.endsWith('.md')) continue

      // Skip excluded filenames
      if (EXCLUDED_FILES.has(entry.name)) continue

      const component = await this.parseAgentFile(fullPath)
      if (component) components.push(component)
    }
  }

  /**
   * Parse a single agent `.md` file into a Component.
   *
   * Extracts YAML frontmatter for name, description, and tools.
   * Falls back to deriving name from filename when frontmatter `name` is absent.
   *
   * Note: SDK parseFrontmatter returns { attrs, body } instead of { meta, body }.
   */
  private async parseAgentFile(filePath: string): Promise<Component | null> {
    let content: string
    try {
      content = await readFile(filePath, 'utf-8')
    } catch {
      return null
    }

    const { attrs } = parseFrontmatter(content)

    const name =
      typeof attrs.name === 'string' && attrs.name.length > 0
        ? attrs.name
        : basename(filePath, '.md')

    const description = typeof attrs.description === 'string' ? attrs.description : ''

    // Parse tools: comma-separated string -> string[]
    let tags: string[] | undefined
    if (typeof attrs.tools === 'string' && attrs.tools.length > 0) {
      tags = attrs.tools
        .split(', ')
        .map((t: string) => t.trim())
        .filter(Boolean)
    }

    const source = relative(this.cwd, filePath)

    return {
      type: 'agent',
      name,
      description,
      source,
      localPath: filePath,
      tags,
    }
  }

  // -------------------------------------------------------------------------
  // ComponentProvider interface
  // -------------------------------------------------------------------------

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    const page = clampPage(params.page)
    const limit = clampLimit(params.limit)

    if (params.type && !SUPPORTED_TYPES.includes(params.type)) {
      return ok(emptyPage(page, limit))
    }

    const agents = await this.discoverAgents()
    const query = params.query.toLowerCase()

    const filtered = agents.filter((a) => {
      if (!query) return true
      return a.name.toLowerCase().includes(query) || a.description.toLowerCase().includes(query)
    })

    return ok(paginateArray(filtered, page, limit))
  }

  async list(
    type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    if (!SUPPORTED_TYPES.includes(type)) return ok([])
    return ok(await this.discoverAgents())
  }

  async info(
    name: string,
    type: ComponentType,
    _opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    if (!SUPPORTED_TYPES.includes(type)) {
      return err(
        new SdkError(
          `Local agent provider does not support info for ${type}`,
          'E_PROVIDER_UNAVAILABLE'
        )
      )
    }

    const agents = await this.discoverAgents()
    const agent = agents.find((a) => a.name === name)

    if (!agent) {
      return err(
        new SdkError(
          `Agent "${name}" not found`,
          'E_COMPONENT_NOT_FOUND',
          'Check the agent name and ensure it exists under content/agents/'
        )
      )
    }

    return ok(agent)
  }

  async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    return err(
      new SdkError(
        'Local agent provider does not support adding agents',
        'E_PROVIDER_UNAVAILABLE',
        'Agents are discovered from content/agents/ -- add .md files directly.'
      )
    )
  }

  async remove(
    _name: string,
    _type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>> {
    return err(
      new SdkError(
        'Local agent provider does not support removing agents',
        'E_PROVIDER_UNAVAILABLE',
        'Agents are discovered from content/agents/ -- remove .md files directly.'
      )
    )
  }

  async publish(): Promise<Result<PublishResult>> {
    return err(
      new SdkError(`${this.displayName} does not support publish`, 'E_PROVIDER_UNAVAILABLE')
    )
  }
}
