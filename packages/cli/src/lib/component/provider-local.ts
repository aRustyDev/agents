/**
 * Local filesystem provider for the Component system.
 *
 * Wraps the existing skill-* modules (skill-list, skill-info, skill-add,
 * skill-remove) behind the universal ComponentProvider interface.
 *
 * Currently only supports the `skill` component type. Other entity types
 * (agents, plugins, rules, etc.) will be added in Phase 3.
 */

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
  PublishResult,
  RemoveResult,
  SearchParams,
} from './types'

const SUPPORTED_TYPES: ComponentType[] = ['skill']

export class LocalProvider implements ComponentProvider {
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

  private readonly cwd: string

  constructor(cwd?: string) {
    this.cwd = cwd ?? process.cwd()
  }

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    if (params.type && !SUPPORTED_TYPES.includes(params.type)) {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    // Use listSkills to get installed skills, then filter by query
    const { listSkills } = await import('../skill-list')
    const listResult = await listSkills({ cwd: this.cwd, agent: params.agent })

    if (!listResult.ok) {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const query = params.query.toLowerCase()
    const filtered = listResult.skills
      .filter((s) => {
        if (!query) return true
        return (
          s.name.toLowerCase().includes(query) ||
          (s.description ?? '').toLowerCase().includes(query)
        )
      })
      .map(
        (s): Component => ({
          type: 'skill',
          name: s.name,
          source: s.source ?? 'local',
          description: s.description ?? '',
          version: s.version,
          tags: s.tags,
          localPath: s.path,
          installedAgents: s.agents,
          installMode: 'copy', // local listing doesn't differentiate yet
        })
      )

    // Apply name filter if specified
    const nameFiltered = params.name
      ? filtered.filter((c) => c.name.toLowerCase() === params.name?.toLowerCase())
      : filtered

    return ok(paginateArray(nameFiltered, clampPage(params.page), clampLimit(params.limit)))
  }

  async add(source: string, opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    const { addSkill } = await import('../skill-add')
    const result = await addSkill(source, {
      cwd: opts.cwd ?? this.cwd,
      agents: opts.agents,
      copy: opts.copy,
      yes: opts.yes,
    })

    if (!result.ok) {
      return err(result.error ?? new CliError('Add failed', 'E_ADD_FAILED'))
    }

    const components: Component[] = result.installed.map((entry) => ({
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
      installedTo: result.installed.flatMap((e) => e.agentLinks),
      warnings: result.warnings,
    })
  }

  async list(
    type: ComponentType,
    opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    if (!SUPPORTED_TYPES.includes(type)) return ok([])

    const { listSkills } = await import('../skill-list')
    const result = await listSkills({
      cwd: opts?.cwd ?? this.cwd,
      agent: opts?.agent,
    })

    if (!result.ok) return ok([])

    return ok(
      result.skills.map(
        (s): Component => ({
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
        new CliError(`Local provider does not support removing ${type}`, 'E_UNSUPPORTED_TYPE')
      )
    }

    const { removeSkills } = await import('../skill-remove')
    const results = await removeSkills([name], {
      cwd: opts?.cwd ?? this.cwd,
      agent: opts?.agent,
      yes: true,
    })

    const r = results[0]
    if (!r) {
      return err(new CliError(`No result for removing "${name}"`, 'E_REMOVE_FAILED'))
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
        new CliError(`Local provider does not support info for ${type}`, 'E_UNSUPPORTED_TYPE')
      )
    }

    const { skillInfo } = await import('../skill-info')
    const result = await skillInfo(name, { cwd: opts?.cwd ?? this.cwd })

    if (!result.ok) return err(result.error)

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
    return err(new CliError(`${this.displayName} does not support publish`, 'E_UNSUPPORTED'))
  }
}
