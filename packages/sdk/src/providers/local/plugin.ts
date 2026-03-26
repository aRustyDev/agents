/**
 * Local plugin provider for the Component system.
 *
 * Discovers plugins by recursively scanning `content/plugins/` for directories
 * that contain a `.claude-plugin/plugin.json` manifest. Reads the manifest
 * using a simple inline parser (no dependency on CLI manifest module).
 *
 * This provider is read-only: it supports search, list, and info but not
 * add, remove, publish, outdated, or update.
 */

import { existsSync } from 'node:fs'
import { readdir, readFile } from 'node:fs/promises'
import { join, relative } from 'node:path'
import type { Result } from '@agents/core/types'
import { err, ok } from '@agents/core/types'
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

const SUPPORTED_TYPES: readonly ComponentType[] = ['plugin'] as const

/** Read and parse a plugin manifest from a directory. */
async function readPluginManifest(
  dir: string
): Promise<{ ok: true; value: Record<string, any> } | { ok: false }> {
  const manifestPath = join(dir, '.claude-plugin', 'plugin.json')
  if (!existsSync(manifestPath)) return { ok: false }

  try {
    const raw = await readFile(manifestPath, 'utf-8')
    return { ok: true, value: JSON.parse(raw) }
  } catch {
    return { ok: false }
  }
}

export class LocalPluginProvider implements ComponentProvider {
  readonly id = 'local-plugin'
  readonly displayName = 'Local Plugins'
  readonly capabilities: ProviderCapabilities = {
    search: ['plugin'],
    add: [],
    list: ['plugin'],
    remove: [],
    publish: [],
    info: ['plugin'],
    outdated: [],
    update: [],
  }

  private readonly cwd: string

  constructor(cwd?: string) {
    this.cwd = cwd ?? process.cwd()
  }

  // -------------------------------------------------------------------------
  // Discovery
  // -------------------------------------------------------------------------

  /**
   * Recursively discover plugin directories under `content/plugins/`.
   *
   * A directory is considered a plugin when it contains
   * `.claude-plugin/plugin.json`. The `.template/` directory is excluded.
   */
  private async discoverPlugins(): Promise<Component[]> {
    const pluginsRoot = join(this.cwd, 'content', 'plugins')

    if (!existsSync(pluginsRoot)) return []

    const components: Component[] = []
    const dirs = await readdir(pluginsRoot, { withFileTypes: true })

    for (const entry of dirs) {
      if (!entry.isDirectory()) continue
      if (entry.name === '.template') continue

      const pluginDir = join(pluginsRoot, entry.name)
      const manifestResult = await readPluginManifest(pluginDir)

      if (!manifestResult.ok) continue

      const manifest = manifestResult.value
      const relativePath = relative(this.cwd, pluginDir)

      components.push({
        type: 'plugin',
        name: manifest.name ?? entry.name,
        description: manifest.description ?? '',
        version: manifest.version,
        author: typeof manifest.author === 'object' ? manifest.author?.name : manifest.author,
        tags: manifest.keywords,
        url: manifest.homepage,
        source: relativePath,
        localPath: pluginDir,
      })
    }

    return components
  }

  // -------------------------------------------------------------------------
  // ComponentProvider implementation
  // -------------------------------------------------------------------------

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    if (params.type && !SUPPORTED_TYPES.includes(params.type)) {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const all = await this.discoverPlugins()
    const query = params.query.toLowerCase()

    const filtered = all.filter((c) => {
      if (!query) return true
      return (
        c.name.toLowerCase().includes(query) ||
        c.description.toLowerCase().includes(query) ||
        (c.tags ?? []).some((t) => t.toLowerCase().includes(query))
      )
    })

    const nameFiltered = params.name
      ? filtered.filter((c) => c.name.toLowerCase() === params.name?.toLowerCase())
      : filtered

    return ok(paginateArray(nameFiltered, clampPage(params.page), clampLimit(params.limit)))
  }

  async list(
    type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    if (!SUPPORTED_TYPES.includes(type)) return ok([])
    return ok(await this.discoverPlugins())
  }

  async info(
    name: string,
    type: ComponentType,
    _opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    if (!SUPPORTED_TYPES.includes(type)) {
      return err(
        new SdkError(
          `Local plugin provider does not support info for ${type}`,
          'E_PROVIDER_UNAVAILABLE'
        )
      )
    }

    const all = await this.discoverPlugins()
    const match = all.find((c) => c.name === name)

    if (!match) {
      return err(
        new SdkError(
          `Plugin not found: ${name}`,
          'E_COMPONENT_NOT_FOUND',
          'Check the plugin name and ensure it exists under content/plugins/'
        )
      )
    }

    return ok(match)
  }

  async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    return err(
      new SdkError(
        'Local plugin provider does not support adding plugins',
        'E_PROVIDER_UNAVAILABLE'
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
        'Local plugin provider does not support removing plugins',
        'E_PROVIDER_UNAVAILABLE'
      )
    )
  }

  async publish(): Promise<Result<PublishResult>> {
    return err(
      new SdkError(`${this.displayName} does not support publish`, 'E_PROVIDER_UNAVAILABLE')
    )
  }
}
