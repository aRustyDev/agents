/**
 * Local filesystem provider for the Component system (skill type).
 *
 * Wraps injected SkillOperations behind the universal ComponentProvider
 * interface. Uses dependency injection instead of dynamic imports to
 * keep the SDK decoupled from CLI-specific modules.
 */

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
import type { SkillOperations } from './skill-ops'

const SUPPORTED_TYPES: ComponentType[] = ['skill']

export class LocalSkillProvider implements ComponentProvider {
  readonly id = 'local'
  readonly displayName = 'Local Filesystem'
  readonly capabilities: ProviderCapabilities = {
    search: SUPPORTED_TYPES,
    add: SUPPORTED_TYPES,
    list: SUPPORTED_TYPES,
    remove: SUPPORTED_TYPES,
    publish: [],
    info: SUPPORTED_TYPES,
    outdated: SUPPORTED_TYPES,
    update: SUPPORTED_TYPES,
  }

  private readonly ops: SkillOperations
  private readonly cwd: string

  constructor(ops: SkillOperations, cwd?: string) {
    this.ops = ops
    this.cwd = cwd ?? process.cwd()
  }

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    if (params.type && !SUPPORTED_TYPES.includes(params.type)) {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const listResult = await this.ops.list({ cwd: this.cwd, agent: params.agent })

    if (!listResult.ok) {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const query = params.query.toLowerCase()
    const filtered = listResult.skills
      .filter((s: any) => {
        if (!query) return true
        return (
          s.name.toLowerCase().includes(query) ||
          (s.description ?? '').toLowerCase().includes(query)
        )
      })
      .map(
        (s: any): Component => ({
          type: 'skill',
          name: s.name,
          source: s.source ?? 'local',
          description: s.description ?? '',
          version: s.version,
          tags: s.tags,
          localPath: s.path,
          installedAgents: s.agents,
          installMode: 'copy',
        })
      )

    // Apply name filter if specified
    const nameFiltered = params.name
      ? filtered.filter((c: Component) => c.name.toLowerCase() === params.name?.toLowerCase())
      : filtered

    return ok(paginateArray(nameFiltered, clampPage(params.page), clampLimit(params.limit)))
  }

  async add(source: string, opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    const result = await this.ops.add(source, {
      cwd: opts.cwd ?? this.cwd,
      agents: opts.agents,
      copy: opts.copy,
      yes: opts.yes,
    })

    if (!result.ok) {
      return err(result.error ?? new SdkError('Add failed', 'E_PROVIDER_UNAVAILABLE'))
    }

    const components: Component[] = result.installed.map((entry: any) => ({
      type: 'skill' as const,
      name: entry.name,
      source: entry.source,
      description: '',
      localPath: entry.canonicalPath,
      installedAgents: [],
    }))

    return ok({
      ok: true,
      components,
      installedTo: result.installed.flatMap((e: any) => e.agentLinks),
      warnings: result.warnings,
    })
  }

  async list(
    type: ComponentType,
    opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    if (!SUPPORTED_TYPES.includes(type)) return ok([])

    const result = await this.ops.list({
      cwd: opts?.cwd ?? this.cwd,
      agent: opts?.agent,
    })

    if (!result.ok) return ok([])

    return ok(
      result.skills.map(
        (s: any): Component => ({
          type: 'skill',
          name: s.name,
          source: s.source ?? 'local',
          description: s.description ?? '',
          version: s.version,
          tags: s.tags,
          localPath: s.path,
          installedAgents: s.agents,
        })
      )
    )
  }

  async remove(
    name: string,
    type: ComponentType,
    opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>> {
    if (!SUPPORTED_TYPES.includes(type)) {
      return err(
        new SdkError(`Local provider does not support removing ${type}`, 'E_PROVIDER_UNAVAILABLE')
      )
    }

    const results = await this.ops.remove([name], {
      cwd: opts?.cwd ?? this.cwd,
      agent: opts?.agent,
      yes: true,
    })

    const r = results[0]
    if (!r) {
      return err(new SdkError(`No result for removing "${name}"`, 'E_PROVIDER_UNAVAILABLE'))
    }

    return ok({
      ok: !r.error,
      component: name,
      removedFrom: r.removedFrom ?? [],
      error: r.error,
    })
  }

  async info(
    name: string,
    type: ComponentType,
    opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    if (!SUPPORTED_TYPES.includes(type)) {
      return err(
        new SdkError(`Local provider does not support info for ${type}`, 'E_PROVIDER_UNAVAILABLE')
      )
    }

    const result = await this.ops.info(name, { cwd: opts?.cwd ?? this.cwd })

    if (!result.ok)
      return err(new SdkError(result.error?.message ?? 'Info failed', 'E_COMPONENT_NOT_FOUND'))

    const detail = result.value
    return ok({
      type: 'skill',
      name: detail.name,
      source: detail.source ?? 'local',
      description: detail.frontmatter?.description ?? '',
      version: detail.frontmatter?.version,
      tags: detail.frontmatter?.tags,
      localPath: detail.path,
      installedAgents: detail.installedAgents,
      installMode: detail.symlinkStatus === 'symlink' ? 'symlink' : 'copy',
    })
  }

  async publish(): Promise<Result<PublishResult>> {
    return err(
      new SdkError(`${this.displayName} does not support publish`, 'E_PROVIDER_UNAVAILABLE')
    )
  }
}
