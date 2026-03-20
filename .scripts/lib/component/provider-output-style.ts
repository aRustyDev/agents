/**
 * Local output-style provider for the Component system.
 *
 * Discovers output styles by scanning `context/output-styles/` for `.md` files.
 * Each file becomes a component whose name is the filename without `.md` and
 * whose description is the first non-heading, non-empty paragraph line.
 *
 * This provider is read-only: it supports search, list, and info but not
 * add, remove, publish, outdated, or update.
 */

import { existsSync } from 'node:fs'
import { readdir, readFile } from 'node:fs/promises'
import { join, relative } from 'node:path'
import { CliError, err, ok, type Result } from '../types'
import { clampLimit, clampPage, emptyPage, paginateArray } from './pagination'
import type {
  Component,
  ComponentAddOptions,
  ComponentAddResult,
  ComponentProvider,
  ComponentType,
  PaginatedResult,
  ProviderCapabilities,
  RemoveResult,
  SearchParams,
} from './types'

const SUPPORTED_TYPES: readonly ComponentType[] = ['output_style'] as const

/** Maximum description length before truncation. */
const MAX_DESCRIPTION_LENGTH = 200

/**
 * Extract the first non-heading, non-empty paragraph line from markdown content.
 * Skips lines that start with `#` or are blank.
 */
function extractDescription(content: string): string {
  const lines = content.split('\n')
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    if (trimmed.startsWith('#')) continue
    return trimmed.length > MAX_DESCRIPTION_LENGTH
      ? `${trimmed.slice(0, MAX_DESCRIPTION_LENGTH)}...`
      : trimmed
  }
  return ''
}

export class LocalOutputStyleProvider implements ComponentProvider {
  readonly id = 'local-output-style'
  readonly displayName = 'Local Output Styles'
  readonly capabilities: ProviderCapabilities = {
    search: ['output_style'],
    add: [],
    list: ['output_style'],
    remove: [],
    publish: [],
    info: ['output_style'],
    outdated: [],
    update: [],
  }

  private readonly stylesDir: string
  private readonly cwd: string

  constructor(cwd?: string) {
    this.cwd = cwd ?? process.cwd()
    this.stylesDir = join(this.cwd, 'context', 'output-styles')
  }

  // -------------------------------------------------------------------------
  // Discovery
  // -------------------------------------------------------------------------

  /**
   * Discover output style files under `context/output-styles/`.
   *
   * Reads all `.md` files, excluding `TODO.md` and dot-prefixed files.
   * Each file is parsed to extract a description from the first paragraph.
   */
  private async discoverStyles(): Promise<Component[]> {
    if (!existsSync(this.stylesDir)) return []

    const entries = await readdir(this.stylesDir, { withFileTypes: true })
    const components: Component[] = []

    for (const entry of entries) {
      if (!entry.isFile()) continue
      if (!entry.name.endsWith('.md')) continue
      if (entry.name === 'TODO.md') continue
      if (entry.name.startsWith('.')) continue

      const filePath = join(this.stylesDir, entry.name)
      const name = entry.name.replace(/\.md$/, '')

      let description = ''
      try {
        const content = await readFile(filePath, 'utf-8')
        description = extractDescription(content)
      } catch {
        // If we cannot read the file, use an empty description
      }

      const relativePath = relative(this.cwd, filePath)

      components.push({
        type: 'output_style',
        name,
        description,
        source: relativePath,
        localPath: filePath,
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

    const all = await this.discoverStyles()
    const query = params.query.toLowerCase()

    const filtered = all.filter((c) => {
      if (!query) return true
      return c.name.toLowerCase().includes(query) || c.description.toLowerCase().includes(query)
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
    return ok(await this.discoverStyles())
  }

  async info(
    name: string,
    type: ComponentType,
    _opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    if (!SUPPORTED_TYPES.includes(type)) {
      return err(
        new CliError(
          `Local output style provider does not support info for ${type}`,
          'E_UNSUPPORTED_TYPE'
        )
      )
    }

    const all = await this.discoverStyles()
    const match = all.find((c) => c.name === name)

    if (!match) {
      return err(
        new CliError(
          `Output style not found: ${name}`,
          'E_OUTPUT_STYLE_NOT_FOUND',
          'Check the name and ensure it exists under context/output-styles/'
        )
      )
    }

    return ok(match)
  }

  async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    return err(
      new CliError(
        'Local output style provider does not support adding styles',
        'E_UNSUPPORTED_OPERATION'
      )
    )
  }

  async remove(
    _name: string,
    _type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>> {
    return err(
      new CliError(
        'Local output style provider does not support removing styles',
        'E_UNSUPPORTED_OPERATION'
      )
    )
  }
}
