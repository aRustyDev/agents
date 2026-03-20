/**
 * Local rule provider for the Component system.
 *
 * Discovers markdown files under `context/rules/` and exposes them
 * as `rule` components via the ComponentProvider interface.
 *
 * Name derivation: relative path with `.md` stripped, using `/` separator.
 *   e.g. `context/rules/agent/hooks.md` -> `"agent/hooks"`
 *
 * Description extraction: first `# ` heading text in the file body.
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

const SUPPORTED_TYPES: readonly ComponentType[] = ['rule']

/** Extract the first H1 heading text from markdown content. */
function extractFirstHeading(content: string): string {
  for (const line of content.split('\n')) {
    if (line.startsWith('# ')) {
      return line.slice(2).trim()
    }
  }
  return ''
}

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

export class LocalRuleProvider implements ComponentProvider {
  readonly id = 'local-rule'
  readonly displayName = 'Local Rules'
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

  private get rulesDir(): string {
    return join(this.cwd, 'context', 'rules')
  }

  /** Discover all rule components under context/rules/. */
  private async discoverRules(): Promise<Component[]> {
    const base = this.rulesDir
    if (!existsSync(base)) return []

    const files = await collectMarkdownFiles(base)
    const components: Component[] = []

    for (const filePath of files) {
      const rel = relative(base, filePath)
      const name = rel.replace(/\.md$/, '')
      const content = await readFile(filePath, 'utf-8')
      const description = extractFirstHeading(content)

      components.push({
        type: 'rule',
        name,
        source: 'local',
        description,
        localPath: filePath,
      })
    }

    return components
  }

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    if (params.type && !SUPPORTED_TYPES.includes(params.type)) {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const all = await this.discoverRules()
    const query = params.query.toLowerCase()

    const filtered = all.filter((c) => {
      if (!query) return true
      return c.name.toLowerCase().includes(query) || c.description.toLowerCase().includes(query)
    })

    return ok(paginateArray(filtered, clampPage(params.page), clampLimit(params.limit)))
  }

  async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    return err(new CliError('Rule provider does not support add', 'E_UNSUPPORTED_OP'))
  }

  async list(
    type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    if (!SUPPORTED_TYPES.includes(type)) return ok([])
    return ok(await this.discoverRules())
  }

  async remove(
    _name: string,
    _type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>> {
    return err(new CliError('Rule provider does not support remove', 'E_UNSUPPORTED_OP'))
  }

  async info(
    name: string,
    type: ComponentType,
    _opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    if (!SUPPORTED_TYPES.includes(type)) {
      return err(
        new CliError(`Rule provider does not support info for ${type}`, 'E_UNSUPPORTED_TYPE')
      )
    }

    const all = await this.discoverRules()
    const found = all.find((c) => c.name === name)

    if (!found) {
      return err(new CliError(`Rule not found: "${name}"`, 'E_RULE_NOT_FOUND'))
    }

    return ok(found)
  }
}
