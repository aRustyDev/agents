/**
 * Local command provider for the Component system.
 *
 * Discovers markdown files under `content/commands/` and exposes them
 * as `command` components via the ComponentProvider interface.
 *
 * Name derivation: relative path with `.md` stripped, `/` replaced by `:`.
 *   e.g. `content/commands/skill/create.md` -> `"skill:create"`
 *
 * Metadata extraction: YAML frontmatter parsed via `parseFrontmatter`.
 *   - `description` field -> Component.description
 *   - `allowed-tools` field (comma-separated) -> Component.tags
 *   - `argument-hint` field -> appended to description in parentheses
 */

import { existsSync } from 'node:fs'
import { readdir, readFile } from 'node:fs/promises'
import { join, relative } from 'node:path'
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

const SUPPORTED_TYPES: readonly ComponentType[] = ['command']

/** Recursively collect all `.md` files under a directory. */
async function collectMarkdownFiles(dir: string): Promise<string[]> {
  const results: string[] = []
  const entries = await readdir(dir, { withFileTypes: true })
  for (const entry of entries) {
    const full = join(dir, entry.name)
    if (entry.isDirectory()) {
      results.push(...(await collectMarkdownFiles(full)))
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      results.push(full)
    }
  }
  return results
}

export class LocalCommandProvider implements ComponentProvider {
  readonly id = 'local-command'
  readonly displayName = 'Local Commands'
  readonly capabilities: ProviderCapabilities = {
    search: SUPPORTED_TYPES,
    add: [],
    list: SUPPORTED_TYPES,
    remove: [],
    publish: [],
    info: SUPPORTED_TYPES,
    outdated: [],
    update: [],
  }

  private readonly cwd: string

  constructor(cwd?: string) {
    this.cwd = cwd ?? process.cwd()
  }

  private get commandsDir(): string {
    return join(this.cwd, 'content', 'commands')
  }

  /** Discover all command components under content/commands/. */
  private async discoverCommands(): Promise<Component[]> {
    const base = this.commandsDir
    if (!existsSync(base)) return []

    const files = await collectMarkdownFiles(base)
    const components: Component[] = []

    for (const filePath of files) {
      const rel = relative(base, filePath)
      const name = rel.replace(/\.md$/, '').replaceAll('/', ':')
      const content = await readFile(filePath, 'utf-8')
      const { attrs } = parseFrontmatter(content)

      const description = typeof attrs.description === 'string' ? attrs.description : ''

      const allowedTools =
        typeof attrs['allowed-tools'] === 'string'
          ? attrs['allowed-tools']
              .split(', ')
              .map((t: string) => t.trim())
              .filter(Boolean)
          : undefined

      components.push({
        type: 'command',
        name,
        source: 'local',
        description,
        tags: allowedTools,
        localPath: filePath,
      })
    }

    return components
  }

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    if (params.type && !SUPPORTED_TYPES.includes(params.type)) {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const all = await this.discoverCommands()
    const query = params.query.toLowerCase()

    const filtered = all.filter((c) => {
      if (!query) return true
      return c.name.toLowerCase().includes(query) || c.description.toLowerCase().includes(query)
    })

    return ok(paginateArray(filtered, clampPage(params.page), clampLimit(params.limit)))
  }

  async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    return err(new SdkError('Command provider does not support add', 'E_PROVIDER_UNAVAILABLE'))
  }

  async list(
    type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    if (!SUPPORTED_TYPES.includes(type)) return ok([])
    return ok(await this.discoverCommands())
  }

  async remove(
    _name: string,
    _type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>> {
    return err(new SdkError('Command provider does not support remove', 'E_PROVIDER_UNAVAILABLE'))
  }

  async info(
    name: string,
    type: ComponentType,
    _opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    if (!SUPPORTED_TYPES.includes(type)) {
      return err(
        new SdkError(`Command provider does not support info for ${type}`, 'E_PROVIDER_UNAVAILABLE')
      )
    }

    const all = await this.discoverCommands()
    const found = all.find((c) => c.name === name)

    if (!found) {
      return err(new SdkError(`Command not found: "${name}"`, 'E_COMPONENT_NOT_FOUND'))
    }

    return ok(found)
  }

  async publish(): Promise<Result<PublishResult>> {
    return err(
      new SdkError(`${this.displayName} does not support publish`, 'E_PROVIDER_UNAVAILABLE')
    )
  }
}
